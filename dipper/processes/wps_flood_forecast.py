from pathlib import Path
from pywps import Process, LiteralInput, LiteralOutput, UOM, ComplexInput, FORMATS, ComplexOutput, Format
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

# import subprocess
import sys
import os
import xarray as xr
import shutil
import matplotlib.pyplot as plt

import tempfile

# import flood functions
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from flood import getFloodlimits, getFloodlevels, floodConfig, wps_flood_forecast_plot

# set up logger
import logging
LOGGER = logging.getLogger("PYWPS")
# LOGNAME = LOGGER.name + '-debug.log'
LOGNAME = tempfile.mkstemp(".log", f"{LOGGER.name}-debug-")
filehandler_dbg = logging.FileHandler(LOGNAME, mode='w')
filehandler_dbg.setLevel('DEBUG') 
#Create custom formats of the logrecord fit for both the logfile and the console
streamformatter = logging.Formatter(fmt='%(levelname)s:\t%(threadName)s:\t%(funcName)s:\t\t%(message)s', datefmt='%H:%M:%S') #We only want to see certain parts of the message
#Apply formatters to handlers
filehandler_dbg.setFormatter(streamformatter)
#Add handlers to LOGGER
LOGGER.addHandler(filehandler_dbg)

# import support for export formats
FORMAT_PNG = Format("image/png", extension=".png", encoding="base64")

class FloodForecast(Process):
	
	OID_NC = 'netcdf'
	OID_LOG = 'log'
	
	def __init__(self):
		
		# self.floodcfg = floodConfig('wps_flood_config_DEV.yml')
		self.floodcfg = floodConfig('wps_flood_config.yml')
		self.plotoutputs = self.floodcfg.getPlotoutputs()
		
		self.dataset_input = ComplexInput('dataset', 'Add your netCDF file here',
						abstract="Enter a URL pointing to a NetCDF file with variables for flood forecast.",
						min_occurs=1,
						max_occurs=1,
						default='/data/proj/Fouh/staff/Jorgen.Rosberg/CLINT/birdhouse/smartduck/tests/netcdf_weekly/timeCOUT_416.nc',
						supported_formats=[FORMATS.NETCDF, FORMATS.ZIP])
		self.variable_input = LiteralInput(
						identifier='variable',
						title='Netcdf variable',
						abstract='Please enter the netcdf variable to use.',
						default='COUT',
						data_type='string')
		warningLevels = list(self.floodcfg.params['quantiles'].keys())
		warningLevels.remove('none')
		warningLevels.append('all')
		warninglvls_input = LiteralInput('warninglvls', 'Warning Level', data_type='string',
						abstract='Choose Warning levels to plot',
						allowed_values=warningLevels,
						default='all')
		inputs = [
						self.dataset_input,
						self.variable_input,
						warninglvls_input,
						]
		outputs = [
			ComplexOutput(FloodForecast.OID_NC, 'netCDF containing the flood forecast',
						abstract='netCDF containing a Flood forecast ... and more description',
						as_reference=True,
						supported_formats=[FORMATS.NETCDF]),
						
			ComplexOutput(FloodForecast.OID_LOG, 'textfile containing logging information of process performance',
						abstract='textfile containing logging information of process performance',
						as_reference=True,
						supported_formats=[FORMATS.TEXT]),
						]
		for plotId in self.plotoutputs:
			outputs.append(
				ComplexOutput(plotId, self.plotoutputs[plotId][0],
						abstract=self.plotoutputs[plotId][1],
						as_reference=True,
						supported_formats=[FORMAT_PNG]),
				)
		
		super(FloodForecast, self).__init__(
			self._handler,
			identifier='floodforecast',
			title='Flood Forecast',
			abstract='abstract comming soon, line 1'
					 'abstract comming soon, line 2',
			keywords=['floodforecast', 'process'],
			metadata=[
				Metadata('PyWPS', 'https://pywps.org/'),
				Metadata('Birdhouse', 'http://bird-house.github.io/'),
				Metadata('PyWPS Demo', 'https://pywps-demo.readthedocs.io/en/latest/'),
				Metadata('Emu: PyWPS examples', 'https://emu.readthedocs.io/en/latest/'),
			],
			version='1.5',
			inputs=inputs,
			outputs=outputs,
			store_supported=True,
			status_supported=True
		)
		
		LOGGER.info("dipper initiated")

	#@staticmethod
	def _handler(self, request, response):
		LOGGER.info("flood forecast process start")
		
		response.update_status('*** START running the process ***', 0)
			
		#####################################
		### read the parameters
		try:
			
			# dataset
			datasetlist = request.inputs['dataset'][0].file
			if datasetlist == None:
				datasetname = self.dataset_input._default
			else:
				try:
					datasetname = open(datasetlist,'r').readline()
				except:
					raise ProcessError(f'FAILED get find dataset listed in: {datasetlist}')
			if not os.path.isfile(datasetname):
				raise ProcessError(f'FAILED get find dataset: {datasetname}')
			
			# variable
			variable = request.inputs['variable'][0].data
			if variable == None:
				variable = self.variable_input._default
			
			# warning levels
			includeLevels = request.inputs['warninglvls'][0].data
			if includeLevels == 'all':
				includeLevels = list(self.floodcfg.params['quantiles'].keys())
				includeLevels.remove('none')
			else:
				includeLevels = list(includeLevels)
			
			# set workdir
			workdir = Path(self.workdir)
			if workdir.is_dir():
				LOGGER.info(f'	DEV workdir exist at start!')
			else:
				LOGGER.info(f'	DEV workdir does NOT exist at start')
			workdir.mkdir(exist_ok=True)
			if workdir.is_dir():
				LOGGER.info(f'	DEV workdir exist after mkdir!')
			else:
				LOGGER.info(f'	DEV workdir does NOT exist after mkdir')
				
		except Exception as ex:
			raise ProcessError(f'FAILED get parameter values: {ex}')
		
		LOGGER.info('Parameter values retrieved:')
		LOGGER.info(f'	parameter "datasetname" = "{datasetname}"')
		LOGGER.info(f'	parameter "variable" = "{variable}"')
		LOGGER.info(f'	workdir = "{workdir}"')
		
		#####################################
		### checks
		if len(request.outputs) < 1:
			raise ProcessError(f'no outputs defined')
		
		#####################################
		### get limits (for each basin, what actual flow is the limit for each warning level)
		floodlimits = getFloodlimits(self.floodcfg, includeLevels=includeLevels)
		LOGGER.info(f'	flood limits set')
		
		##################################
		### get flood levels (for each basin, mark each timestep with the level the flow it is exceeding)
		floodlevels, nrTimesteps = getFloodlevels(self.floodcfg, datasetname, variable, floodlimits, includeLevels=includeLevels)
		LOGGER.info(f'	flood levels found, nr time steps = {nrTimesteps}')
		
		##################################
		### produce outputs
		outC = 0
		
		if FloodForecast.OID_NC in request.outputs:
			##################################
			### netcdf output
			
			ncfile = workdir / 'out.nc'
			
			try:
				# reorder the dimensions so that time is first
				# floodlevels = floodlevels[['time', 'id']] only on a DataSet, floodlevels is a DataArray..
				# floodlevels = floodlevels.transpose('time', 'id')
				floodlevels.to_netcdf(
					path=ncfile,
					# unlimited_dims='time'
					)
			except Exception as e:
				raise ProcessError(f'could not save netcdf to {ncfile}') from e
			
			response.outputs[FloodForecast.OID_NC].file = ncfile
			
			LOGGER.info(f'	{FloodForecast.OID_NC} output created')
			outC += 1
		
		##################################
		### plot output graphs
		for plotId in request.outputs:
			
			if plotId not in self.plotoutputs:
				continue
			
			LOGGER.info(f'	getting attr for "{plotId}"')
			plotFunc = getattr(wps_flood_forecast_plot, plotId)
			
			try:
				response.outputs[plotId].file = plotFunc(
					floodcfg=self.floodcfg,
					floodlevels=floodlevels,
					plot_type=plotId,
					workdir=workdir,
					includeLevels=includeLevels,
					valuerange=(0,nrTimesteps)
				)
			except Exception as e:
				raise ProcessError(f'could not produce plot {plotId}') from e
			LOGGER.info(f'	output created for "{plotId}"')
			outC += 1
		
		##################################
		### log output
		if FloodForecast.OID_LOG in request.outputs:
			
			# logfile = workdir / 'log.txt'
			# try:
				# if workdir.is_dir():
					# LOGGER.info(f'	DEV workdir exist prior to copy!')
				# else:
					# LOGGER.info(f'	DEV workdir does NOT exist prior to copy')
				# shutil.copy(LOGNAME, logfile)
			# except Exception as e:
				# raise ProcessError(f'could not save log to {logfile}') from e
			
			response.outputs[FloodForecast.OID_LOG].file = LOGNAME #logfile
			
			LOGGER.info(f'	{FloodForecast.OID_LOG} output created')
			outC += 1
		
		LOGGER.info(f'	{outC} outputs produced')
		
		##################################
		### done, wrapping up
		
		response.update_status('done.', 100)
