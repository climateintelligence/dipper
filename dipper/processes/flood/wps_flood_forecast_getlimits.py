"""
import wps_flood_forecast_getlimits; floodlimits = wps_flood_forecast_getlimits.getFloodlimits(True)
importlib.reload(wps_flood_forecast_getlimits); floodlimits = wps_flood_forecast_getlimits.getFloodlimits(True)
"""

import os
import xarray as xr
# import numpy as np
from datetime import datetime
from pywps.app.exceptions import ProcessError

from .wps_flood_config import floodConfig

def getFloodlimits(
		floodcfg,
		createIfMissing=False,
		includeLevels=None
	):
	
	# get parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	dataVar = floodcfg.params['reference']['var_data']
	timeDim = floodcfg.params['reference']['dim_time']
	refStart = floodcfg.params['reference']['datespan']['start']
	refStop = floodcfg.params['reference']['datespan']['stop']
	# floodcfg.logger.info(f"flood levels read from {FLOODSCONFIGFILE}")
	
	# include levels defaults to all
	if includeLevels == None:
		includeLevels = flood_quantiles.keys()
	
	# get variable parameters needed
	flodlimitsFile = floodcfg.getFlodlimitsnc()
	refNc = floodcfg.getRefnc()
	
	load_floodlimits = os.path.isfile(flodlimitsFile)
	# check if limits are already present
	if load_floodlimits:
		
		# load floodlimits
		try:
			floodlimits = xr.open_dataset(flodlimitsFile) 
			floodcfg.logger.info(f'  existing floodlimits loaded from {flodlimitsFile}')
			# print('LOADING')
		except:
			load_floodlimits = False
	
	if not load_floodlimits:
		
		# re-create permitted?
		if not createIfMissing:
			raise ProcessError(f'Floodlimits netcdf missing (and flag to re-create was set to false): {flodlimitsFile}')
		
		floodcfg.logger.info('  pre-existing floodlimits file not found, creating new')
		# print('CREATING')
		
		# get values from netcdf
		try:
			ncvalues = xr.open_dataset(refNc)
			floodcfg.logger.info(f"	values read from {refNc}")
		except:
			raise ProcessError(f'Fail to open ref netcdf: {refNc}')
		
		# create floodlimits
		refdataarray = ncvalues[dataVar].sel(time=slice(refStart,refStop))
		floodcfg.logger.info('	refdataarray extracted from netcdf')
		
		# extract floodlimits
		floodlimits = refdataarray.quantile([flood_quantiles[wl]['quantile'] for wl in includeLevels], dim=timeDim)
		floodcfg.logger.info('	floodlimits calculated')
		# print('  floodlimits: {}\n{}'.format(
			# floodlimits.sizes,
			# float(floodlimits.sel(id=8000003,quantile=0.95).get(NC_VAR_DATA))))
		
		# write floodlimits to file for reuse and doc.
		try:
			floodlimits.to_netcdf(
				path=flodlimitsFile,
				mode='w',
				format='NETCDF4')  # OR 'NETCDF4_CLASSIC' to be netcdf3 compatible..
			floodcfg.logger.info(f'	floodlimits written to {flodlimitsFile}')
		except:
			raise ProcessError(f'Fail to write flood limit netcdf: {flodlimitsFile}')
	
	return floodlimits
