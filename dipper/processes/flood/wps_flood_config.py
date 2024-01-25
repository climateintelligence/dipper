from pywps.app.exceptions import ProcessError
import yaml # pip install pyyaml
from pathlib import Path


import logging

import os

class floodConfig():

	FLOODSCONFIGFILE = 'wps_flood_config.yml'
	
	def __init__(self, floodsconfigfile=None):
		
		if floodsconfigfile == None:
			floodsconfigfile = floodConfig.FLOODSCONFIGFILE
		
		# load parameters from yml config file
		cfgfile = self.getLocalpath() / floodsconfigfile
		try:
			with open(cfgfile,'r') as file:
				self.params = yaml.safe_load(file)
		except FileNotFoundError as e:
			# LOGGER.info(f'	FAIL to find config file = "{os.path.abspath(floodsconfigfile)}"')
			raise ProcessError(f'could not find configuration file "{cfgfile}": {e}')
		
		self.logger = logging.getLogger(self.params['logname'])
		
	
	def getLocalpath(self):
		return Path(os.path.realpath(__file__)).parent
	
	def getFlodlimits(self):
		return self.getLocalpath() / self.params['reference']['floodlimitsnc']

	def getFlodlimitsnc(self):
		return self.getLocalpath() / self.params['reference']['floodlimitsnc']
	
	def getRefnc(self):
		return self.getLocalpath() / self.params['reference']['referenceperiodnc']
		
	def getShapefile(self):
		return self.getLocalpath() / self.params['shapefile']
	
	def getPlotoutputs(self):
		plotoutputs = {}
		for plotId in self.params['plots'].keys():
			functionname = plotId
			shortname = self.params['plots'][plotId]['shortname']
			abstract = self.params['plots'][plotId]['abstract']
			plotoutputs[functionname] = [shortname, abstract]
		return plotoutputs
