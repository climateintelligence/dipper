"""
import wps_flood_forecast_getfloods; floodlevels = wps_flood_forecast_getfloods.getFloodlevels('/data/proj/Fouh/staff/Jorgen.Rosberg/CLINT/birdhouse/testdata/timeCOUT_week_40.nc', 'cout_dd', floodlimits)
import importlib;
importlib.reload(wps_flood_forecast_getfloods); floodlevels = wps_flood_forecast_getfloods.getFloodlevels('/data/proj/Fouh/staff/Jorgen.Rosberg/CLINT/birdhouse/testdata/timeCOUT_week_40.nc', 'cout_dd', floodlimits)
"""

from pywps.app.exceptions import ProcessError
import os

import xarray as xr

def getFloodlevels(
	floodcfg,
	inNc,
	datavariable,
	floodlimits,
	dateSpan=None,
	includeLevels=None):
	
	inTimeName = 'time'
	
	# extract parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	# stopDate = floodcfg.params['forecast']['datespan']['stop']
	# startDate = floodcfg.params['forecast']['datespan']['start']
	# varData = floodcfg.params['forecast']['var_data']
	basefloodlevel = floodcfg.params['basefloodlevel']
	floodlimitsVarname = floodcfg.params['reference']['var_data']
	
	# include levels defaults to all
	if includeLevels == None:
		includeLevels = flood_quantiles.keys()
	
	# check file
	if not os.path.isfile(inNc):
		raise ProcessError(f'Ref netcdf not found: {inNc}')
	floodcfg.logger.info(f"	reading values read {inNc}")
	
	# get values from netcdf
	try:
		ncvalues = xr.open_dataset(inNc)
		floodcfg.logger.info(f"	values read from {inNc}")
	except:
		raise ProcessError(f'Fail to open ref netcdf: {inNc}')
	
	# extract the data
	if dateSpan == None:
		ncvaluesDArray = ncvalues[datavariable]
	else:
		startDate = dateSpan[0]
		endDate = dateSpan[1]
		ncvaluesDArray = ncvalues[datavariable].sel(time=slice(startDate, stopDate))
		
		# check forecast data length
		expectedLength = (datetime.strptime(stopDate, '%Y-%m-%d') - datetime.strptime(startDate, '%Y-%m-%d')).days + 1 # inclusive range
		if len(ncvaluesDArray) != expectedLength:
			raise ProcessError(f'extracted data not of expected length: {len(ncvaluesDArray)} points extracted between {startDate} and {stopDate}, should have been {expectedLength}')
		print(f'  forecast dataarray extracted between {startDate} and {stopDate}')
	
	# apply floodlimits to find potential floods
	#  1) add new variable with value ='basefloodlevel' i.e "no warning"
	warningsDArray = ncvaluesDArray * 0 + basefloodlevel
	#  2) use xr.where() to set the quantile for each value (increasing)
	nrTimes = len(ncvaluesDArray[inTimeName])
	for warnlvl in includeLevels:
		
		if warnlvl == 'none':
			continue
		quantile = float(flood_quantiles[warnlvl]['quantile'])
		
		try:
			floodlimit = floodlimits.sel(quantile=quantile)[floodlimitsVarname]
		except KeyError:
			continue #!?
		
		tC = nrTimes
		for t in ncvaluesDArray[inTimeName]:
			# timestep as integer, falling order
			tC -= 1.0
			lvl = float(int((tC / nrTimes) * 100))
			
			# set <timestep int> + <quantile> for this timestep
			selArr = warningsDArray.sel(time=t)
			# selArr.values[:] = xr.where(ncvaluesDArray.sel(time=t) > floodlimit, 1.9, selArr)
			selArr.values[:] = xr.where(
					ncvaluesDArray.sel(time=t) > floodlimit,	# select values that exceeds this warning level
					lvl + quantile,								#   values for selected 
					selArr										#   values for not selected
				) #.to_array()
	
	# find first week of exceedance, with skill
	warningsDArray = warningsDArray.max(dim=inTimeName)
	
	# SO, not the warningsDArray [xarray.DataArray] has one value for each 'id'
	#  with value = <level>.<quantile> where "level" is counting linearly down 100 to 0 and quantile is the highest quantile exceeded at this week.
	#  f.ex: for a particular 'id' if the value exceeds the 0.95 quantile at timestep 6/30 the value will be 20.95
	#        EVEN if the values for a later timestep exceeds a higher quantile, e.g 0.99 at timestep 11/30 (which would be value 36.99)
	# NOW this is ready for visualization, chose color by quantile (i.e the fraction) and color intensity by the integer
	
	return (warningsDArray, len(ncvaluesDArray))
