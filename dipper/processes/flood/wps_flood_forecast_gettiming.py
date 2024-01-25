from pywps.app.exceptions import ProcessError
import os

import xarray as xr

import colorsys

def getFloodtiming(
	floodcfg,
	warningsDArray):
	
	threshold_id = 'none'
	
	dimname_data = 'cout_dd'
	dimname_time = 'time'
	
	# extract parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	
	threshold_quantile = flood_quantiles[threshold_id]['quantile']
	
	# get indexes of where the quantiles exceeds the threshold
	indexesDataset = warningsDArray > threshold_quantile
	
	# add timestep nr in reverse to the quantiles in warningsDArray
	#  (so e.g for one 'id' in the dataset it will go from:  "0.0 0.0 0.9 0.95 0.99 0.0 0.0" to "7.0 6.0 5.9 4.95 3.99 2.0 1.0" assuming 7 timesteps)
	nrTimes = warningsDArray.sizes[dimname_time]
	for t in range(0,nrTimes):
		warningsDArray ... [dimname_time=t]
	
	# set all quantiles lower than the threshold to 0
	#  (so the example will go from:  "7.0 6.0 5.9 4.95 3.99 2.0 1.0" to "0.0 0.0 5.9 4.95 3.99 0.0 0.0" assuming threshold '0.0' a.k.a 'none')
	timingDArray = warningsDArray.where( indexesDataset, drop=True )
	
	# form max value array to find the quantile of the first occuring warning level above the threshold
	#  (so the example will go from:  "0.0 0.0 5.9 4.95 3.99 0.0 0.0" to "5.9")
	#  (( the inverse week nr (the integer) will be used in the plot to set color saturation and the quantile (the fraction) will set the actual color..))
	timingDArray = 
	
	# done, ready for plotting
	return timingDArray
	
	
	return timingDArray

def plotFloodtiming(
	floodcfg,
	warningsDArray,
	timingDArray):
	
	dimname_time = 'time' # TODO..
	
	# convert the timing (timestep nr) to saturation of the color
	nrTimes = warningsDArray.sizes[dimname_time]
	
	# prep and set colormap
	for header in flood_quantiles.keys():
		
		q = flood_quantiles[header]['quantile']
		rgb = flood_quantiles[header]['color_rgba']
		
		for t in range(0,nrTimes):
			
			hls = colorsys.rgb_to_hls(rgb[0],rgb[1],rgb[2])
			adjrgb = colorsys.hls_to_rgb( hls[0], hls[1], (t+1) / nrTimes)
			
			# add alpha channel if present
			# if len(rgb) > 3:
				# adjrgb += (rgb[3],)
			
			myplotter.addColor(
				t + q,
				rgb,
				f'{header}_{t}')
	
	# form
	
	plotDArray = warningsDArray + timingDArray