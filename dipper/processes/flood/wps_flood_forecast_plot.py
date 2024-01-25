
"""
from pathlib import Path
import importlib
import wps_flood_forecast_plot; plotfile = wps_flood_forecast_plot.flood_plot(floodlevels,Path('./'))
importlib.reload(wps_flood_forecast_plot); plotfile = wps_flood_forecast_plot.flood_plot(floodlevels,Path('./'))
"""
from pathlib import Path
from pywps.app.exceptions import ProcessError
"""
from flood.wps_flood_utils_myplot import MyPlotter

"""
import yaml
from .wps_flood_utils_myplot import MyPlotter
import colorsys
from matplotlib.colors import LinearSegmentedColormap

def flood_plot(
	floodcfg,
	floodlevels,
	plot_type,
	workdir,
	includeLevels=None,
	valuerange=None):
	
	if plot_type == FloodForecast.OID_PLOT_WEEKS:
		result = warning_plot(
			floodcfg,
			floodlevels,
			plot_type,
			workdir)
	elif plot_type == FloodForecast.OID_PLOT_TIMING:
		result = timing_plot(
			floodcfg,
			floodlevels,
			plot_type,
			workdir)
	else:
		raise Exception(f'plot type not implemented: {plot_type}')
	
	return result

def warning_plot(
	floodcfg,
	floodlevels,
	plot_type,
	workdir,
	includeLevels=None,
	valuerange=None):
	
	# extract parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	resolution_dpi = floodcfg.params['plots'][plot_type]['dpi']
	title = floodcfg.params['plots'][plot_type]['title']
	file_name = floodcfg.params['plots'][plot_type]['filename']
	
	# include levels defaults to all
	if includeLevels == None:
		includeLevels = flood_quantiles.keys()
	
	# make certain file name endex is png
	file_name = Path(file_name)
	file_name = file_name.with_suffix('.png')
	
	# get variable parameters needed
	shapefile = floodcfg.getShapefile()
	
	# set output name
	file_out_plot = workdir / file_name
	
	# start map plotter
	myplotter = MyPlotter(shapefile)
	
	# prep and set colormap
	# colormap = {}
	for header in includeLevels:
		
		myplotter.addColor(
			flood_quantiles[header]['quantile'],
			flood_quantiles[header]['color_rgba'],
			header)
		# colormap[header] = flood_quantiles[header]['color_rgba']
	# myplotter.setColors(colormap)
	# print('  colors set')
	
	timeindex = 0
	
	# plot map
	myplotter.plotmap(
		title=title,
		dataarray=floodlevels,
		file_outplot=file_out_plot,
		timeindex=timeindex,
		dpi=resolution_dpi)
	
	# print('  map plotted')
	return file_out_plot

def timing_plot_1(
	floodcfg,
	floodlevels,
	plot_type,
	workdir,
	includeLevels=None,
	valuerange=None):
	
	# extract parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	resolution_dpi = floodcfg.params['plots'][plot_type]['dpi']
	title = floodcfg.params['plots'][plot_type]['title']
	file_name = floodcfg.params['plots'][plot_type]['filename']
	
	# include levels defaults to all
	if includeLevels == None:
		includeLevels = flood_quantiles.keys()
	
	# make certain file name endex is png
	file_name = Path(file_name)
	file_name = file_name.with_suffix('.png')
	# file_name.rename(file_name.with_suffix('.png'))
	
	# get variable parameters needed
	shapefile = floodcfg.getShapefile()
	
	# set output name
	file_out_plot = workdir / file_name
	
	# start map plotter
	myplotter = MyPlotter(shapefile)
	# print('  my plotter created for shapefile {}'.format(shapefile))
	
	# prep and set colormap
	# colormap = {}
	for header in includeLevels:
		q = flood_quantiles[header]['quantile']
		rgbColorBase = flood_quantiles[header]['color_rgba']
		for saturation in range(0,101):
			
			hsvColor = colorsys.rgb_to_hsv(rgbColorBase[0], rgbColorBase[1], rgbColorBase[2])
			rgbColor = colorsys.hsv_to_rgb(hsvColor[0],saturation,hsvColor[2])
			
			myplotter.addColor(
				q,
				rgbColor,
				header)
	# print('  colors set')
	
	timeindex = 0
	
	# plot map
	myplotter.plotmap(
		title=title,
		dataarray=floodlevels,
		file_outplot=file_out_plot,
		timeindex=timeindex,
		dpi=resolution_dpi)
	
	# print('  map plotted')
	return file_out_plot

def timing_plot_2(
	floodcfg,
	floodlevels,
	plot_type,
	workdir,
	includeLevels=None,
	valuerange=None):
	
	# extract parameters needed
	flood_quantiles = floodcfg.params['quantiles']
	resolution_dpi = floodcfg.params['plots'][plot_type]['dpi']
	title = floodcfg.params['plots'][plot_type]['title']
	subtitle = floodcfg.params['plots'][plot_type]['subtitle']
	file_name = floodcfg.params['plots'][plot_type]['filename']
	shapefile = floodcfg.getShapefile()
	
	# make certain file name endex is png
	file_name = Path(file_name)
	file_name = file_name.with_suffix('.png')
	
	# set output name
	file_out_plot = workdir / file_name
	
	# init plotter
	myplotter = MyPlotter(shapefile)
	
	for header in flood_quantiles.keys():
		q = float(flood_quantiles[header]['quantile'])
		rgbColorBase = flood_quantiles[header]['color_rgba']
		hsvColorBase = colorsys.rgb_to_hsv(rgbColorBase[0], rgbColorBase[1], rgbColorBase[2])
		for saturation in range(0,101):
			rgbColor = colorsys.hsv_to_rgb(hsvColorBase[0],float(saturation)/100.0,hsvColorBase[2])
			myplotter.addColor(
				float(saturation) + q,
				rgbColor,
				header)
		
		# for header in flood_quantiles.keys():
		showcolorbar = True
		if 'colorbar' in flood_quantiles[header]:
			showcolorbar = flood_quantiles[header]['colorbar'] == 'true'
		# rgbColorBase = flood_quantiles[header]['color_rgba']
		# hsvColorBase = colorsys.rgb_to_hsv(rgbColorBase[0], rgbColorBase[1], rgbColorBase[2])
		minColor = colorsys.hsv_to_rgb(hsvColorBase[0],0.0,hsvColorBase[2])
		maxColor = colorsys.hsv_to_rgb(hsvColorBase[0],1.0,hsvColorBase[2])
		myplotter.setColormap(
					header,
					LinearSegmentedColormap.from_list(header, [maxColor, minColor]), #, N=32),
					showcolorbar=showcolorbar)
	
	# plot map
	timeindex = 0
	myplotter.plotmap(
				title=title,
				subtitle=subtitle,
				dataarray=floodlevels,
				file_outplot=file_out_plot,
				timeindex=timeindex,
				dpi=resolution_dpi,
				valuerange=valuerange)
	
	# done, return
	return file_out_plot
