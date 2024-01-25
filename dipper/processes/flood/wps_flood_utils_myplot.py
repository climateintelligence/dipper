
import sys # for test

import cartopy.io.shapereader as shpreader
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Rectangle
from matplotlib.ticker import AutoMinorLocator
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cf
from colorsys import rgb_to_hls, hls_to_rgb, rgb_to_hsv

# import logging
# LOGGER = logging.getLogger("PYWPS")

mpl.use('agg') # a file output only backend to avoid causing problem in threads

"""
How to Use:
1) Direct:
	call this script with arguments, see parser below.
	examples:
		
2) Import:
	1) create plotter, e.g:
		myplotter = MyPlotter(shapefile)
	2) set colormap, e.g:
		myplotter.setColors(colordict)
		where colordict are a dict with <name>=(maxvalue, (r g b)), e.g:
				colordict = dict(
						none = (0.0, (0.39, 0.79, 0.85,0.2)),
						low = (0.9, (0.16, 0.8, 0.18, 0.9)),
						medium = (0.95, (1.0, 0.96, 0.31, 0.9)),
						high = (0.99, (0.85, 0.18, 0.25, 0.9)) )
	3) plot map
		myplotter.plotmap(plottitle, warningsarray, file_out, dpi=400)
"""

def myplot(
		file_shapefile):
	
	print('\MyPlot started\n')
	
	# file_shapefile = 'SUBID_TotalDomain_WGS84_20140428_2_rev20150415.shp'
	
	file_plotout = "map.png"
	
	print('  creating myplotter')
	myplotter = MyPlotter(file_shapefile)
	
	print('  plotmap')
	myplotter.plotmap()
	
	print('\nDONE\n')

class ColorDict():
	
	def __init__(self, defaultcolor=[1.0, 0.0, 0.0, 1.0]):
		
		self.defaultcolor = defaultcolor
		self.colordict = {} # value vs (hexcolor, legendtext)
		self.colorkeys = []
		self.isSorted = False
	
	def addColor(self,
				value,
				rgbcolor,
				legendtext):
		"""
		NOTE:  value must be float, not numpy.ncarray(), use .tolist()
		"""
		
		# LOGGER.info(f'ADDING {value} = {rgbcolor}') #.tolist()
		# print('   => hexcolor = {}'.format(mpl.colors.rgb2hex(rgbcolor))) #.tolist()
		self.colordict[value] = (rgbcolor, legendtext) # (mpl.colors.rgb2hex(rgbcolor), legendtext)
		self.isSorted = False
	
	def __sort(self):
		if self.isSorted:
			return
		# print('before: {}'.format(self.colordict
		# self.colordict = sorted(self.colordict.items())
		self.colorkeys = sorted(self.colordict.keys())
		self.isSorted = True
	
	def plotLegend(self, ax, title):
		self.__sort()
		
		legend_lines = []
		legend_headings = []
		for value in self.colordict.keys():
			# add legend entry
			legend_lines.append(
							Rectangle(
								(0, 0),
								3,
								1,
								facecolor=self.colordict[value][0],
								edgecolor='black', #legend_framecolor,
								linewidth=0.5,
							)
			)
			legend_headings.append(self.colordict[value][1])
		
		# add legend?
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		ax.legend(
				reversed(legend_lines),
				reversed(legend_headings),
				loc="center left",
				bbox_to_anchor=(1, 0.5))
		# ax.legend(lines, titles, loc='upper center', bbox_to_anchor=(0.5, -0.05),
		#		   fancybox
		
		# legend title
		# legend = ax.get_legend()
		ax.get_legend().set_title(title)
		# plt.setp(legend.get_title(), fontsize=plot_legend_fontsize)
	
	def getLegendtext(self, colorrgb):
		"""
		returns the text [String] for this colorrgb
		"""
		for clrentry in self.colordict.values():
			if clrentry[0] == colorrgb:
				return clrentry[1]
		
		return f'No legend found for color {colorrgb}, available are: ' + str([str(s[0]) for s in self.colordict.values()])
	
	def getHexColor(self,value):
		self.__sort()
		# print('self.colorkeys = "{}"'.format(self.colorkeys))
		# print('len(self.colorkeys)-1 = "{}"'.format((len(self.colorkeys)-1)))
		# print('value = "{}"'.format(value))
		key = ColorDict.floorSearch(
							self.colorkeys,
							0,
							len(self.colorkeys)-1,
							value)
		if key >= 0:
			return self.colordict[self.colorkeys[key]][0]
		else:
			return self.defaultcolor

	def getRGBColor(self,value):
		self.__sort()
		key = ColorDict.floorSearch(
							self.colorkeys,
							0,
							len(self.colorkeys)-1,
							value)
		if key >= 0:
			return self.colordict[self.colorkeys[key]][0]
		else:
			return self.defaultcolor
	
	def floorSearch(arr, low, high, x):
		# from https://www.geeksforgeeks.org/floor-in-a-sorted-array/
	 
		# If low and high cross each other
		if (low > high):
			return -1
	 
		# If last element is smaller than x
		# print('arr[high] = {}'.format(arr[high]))
		if (x >= arr[high]):
			return high
	 
		# Find the middle point
		mid = int((low + high) / 2)
	 
		# If middle point is floor.
		if (arr[mid] == x):
			return mid
	 
		# If x lies between mid-1 and mid
		if (mid > 0 and arr[mid-1] <= x
				and x < arr[mid]):
			return mid - 1
	 
		# If x is smaller than mid,
		# floor must be in left half.
		if (x < arr[mid]):
			return ColorDict.floorSearch(arr, low, mid-1, x)
	 
		# If mid-1 is not floor and x is greater than
		# arr[mid],
		return ColorDict.floorSearch(arr, mid + 1, high, x)

class MyPlotter():
	
	def __init__(self,
				file_shapefile,
				shapefileIdItem = "SUBID"):
		
		self.colormap = None
		self.colormaps = {}
		self.showcolorbar = {}
		
		# Read shape file
		self.reader_shapefile = shpreader.Reader(file_shapefile)
		
		self.shapefileIdItem = shapefileIdItem
	
	# def setColors(self,
				# dataarray,
				# numcolors=12,
				# colormapname='RdYlGn'):
		
		# quantiles = dataarray.quantile(np.linspace(0, 1.0, num=12, endpoint=True))
		# self.setColors_quantiles(quantiles, colormapname)
	
	def setColormap(self,
				legendtxt,
				colormap,
				showcolorbar=False):
		
		self.colormaps[legendtxt] = colormap
		self.showcolorbar[legendtxt] = showcolorbar
	
	def getColormap(self,
				legendtxt):
		
		return self.colormaps[legendtxt]
	
	def getColortypes(self):
		return self.colormaps.keys()
	
	
	def showColorbar(self,
				legendtxt):
		return self.showcolorbar[legendtxt]
	
	def getNrvisiblecolorbars(self):
		return list(self.showcolorbar.values()).count(True)
	
	def addColor(
			self,
			minvalue,
			rgbcolor,
			legendtext):
		
		if self.colormap == None:
			self.colormap = ColorDict()
		
		self.colormap.addColor(
			minvalue,
			rgbcolor,
			legendtext
			)

	def setColors(self,
				colormap,
				colormapname='RdYlGn'):
		"""
		colormap is assumed to be a dict:
			keys: legend text
			value: tuple(
						minimum VALUE
						rgb color
						)
		"""
		
		try:
			cmap = mpl.cm.get_cmap(colormapname)
		except ValueError as ve:
			raise Exception('color map not in matplotlib.colormaps: "{}"'.format(colormapname))
		
		self.colormap = ColorDict()
		for legendtext in colormap.keys():
			self.colormap.addColor(
							colormap.get(legendtext)[0], # min value
							colormap.get(legendtext)[1],  # rgbcolor
							legendtext  # legend text
							)
							# quantile.data.tolist(),  # min value
							# cmap(quantile.coords['quantile'].values),  # rgbcolor
							# legendtext)  # legend text
	
	# def getRGB(color):
		
		# if type(color) is tuple:
			# nc = []
			# for c in color:
				# if c > 
		
	
	def plotmap(self,
				title,
				dataarray,
				file_outplot,
				subtitle=None,
				timeindex=0,
				dpi=1200,
				valuerange=None):
		
		# if self.colormap == None:
			# raise Exception('no color map set when calling plotmap')
		
		# settings:
		plot_zorder = 10
		alpha_subids = 0.9
		plot_background = True
		plot_coastline = True
		
		# assumes:
		#  TODO: map projection taken from shapefile?
		proj = ccrs.PlateCarree()
		#  projection for data (i.e. coord. unit) matches shapefile
		
		# image settings
		colorbarWidth = 0.015
		figDim = [0.1, 0.1, 0.7, 0.9] # width is adjusted later when colorbars are known
		
		# start image
		fig = plt.figure(figsize = (20,10))
		ax = fig.add_axes(figDim, projection=proj) # label=
		# (axes for colorbars added later when number is known)
		plt.sca(ax) # set current axes
	
		# ax = plt.axes(projection=proj)
		if plot_background:
			ax.stock_img()
		if plot_coastline:
			ax.add_feature(cf.COASTLINE, lw=2)
		if subtitle:
			# set suptitle of the figure
			supt = fig.suptitle(title, fontsize=20, fontweight='bold')
			# center title on the figure, not the axes
			titleXshift = supt.get_position()[0] - (ax.get_position().get_points()[1,0] / 2.0)
			plt.title(subtitle, y=1.05, fontsize=14,x=supt.get_position()[0] + titleXshift)
		else:
			plt.suptitle(title, fontsize=20, fontweight='bold')
		# plt.gcf().set_size_inches(20, 10)
		
		# form matplotlib collections, group subid shapes by color
		shapes_dict = {} # FOR TEST 1
		shapes = {} # FOR TEST 2
		colors = {} # FOR TEST 2
		# bounds in matplotlib: (left, right, bottom, top)
		bounds = [sys.float_info.max, -sys.float_info.max, sys.float_info.max, -sys.float_info.max]
		for record in self.reader_shapefile.records():
			
			subid = record.attributes[self.shapefileIdItem]
			# print('subid = {}'.print(subid))
			
			# get color for this subid
			values = dataarray.sel(dict(id=subid)).data
			# values = dataarray.sel(dict(id=subid))[()]
			
			# are values a single value or a collection?
			try:
				nrValues = len(values)
			except:
				nrValues = 1 # yeah.. python..
				values = [values]
			
			# collection of enough size?
			if timeindex >= nrValues:
				raise Exception(f'can not plot time index {timeindex}: exceeds arrays size ({nrValues})')
			
			# extract value for this timeindex
			# try:
			value = values[timeindex] #.data
			
			# hexcolor = self.colormap.getHexColor(value.tolist())
			# LOGGER.info(f' VALUE == {value.data}')
			# LOGGER.info(f' RGB list == {self.colormap.getRGBColor(value.data)}')
			# rgbcolor = tuple(self.colormap.getRGBColor(value))
			rgbcolor = self.colormap.getRGBColor(value)
			
			# add each shape
			#   convert to matplotlib polygon and add to this color group:
			legendtxt = self.colormap.getLegendtext(rgbcolor)
			if legendtxt not in shapes.keys():
				shapes[legendtxt] = []
				colors[legendtxt] = []
			if record.geometry.geom_type == 'MultiPolygon':
				for shape in record.geometry.geoms:
					shapes[legendtxt].append(Polygon(list(zip(shape.exterior.xy[0],shape.exterior.xy[1])),closed=True))
					colors[legendtxt].append(rgbcolor)
			elif record.geometry.geom_type == 'Polygon':
				shapes[legendtxt].append(Polygon(list(zip(record.geometry.exterior.xy[0],record.geometry.exterior.xy[1])),closed=True))
				colors[legendtxt].append(rgbcolor)
			else:
				raise Exception('can not plot shapefile geometry of type: {}'.format(record.geometry.geom_type))
			
			# collect bounding box
			#   BUT bounds for geometry is (left, bottom, right, top)
			bounds[0] = min(bounds[0], record.geometry.bounds[0]) # left
			bounds[1] = max(bounds[1], record.geometry.bounds[2]) # right
			bounds[2] = min(bounds[2], record.geometry.bounds[1]) # bottom
			bounds[3] = max(bounds[3], record.geometry.bounds[3]) # top
		
		# so, now all shapes has been added to shapes_dict, one key per color and values are the shapes as an array
		#     also, bounds has been updated
		
		# check
		# if len(shapes_dict) < 1:
			# raise Exception('no records found')
		
		# zoom
		ax.set_extent(bounds)
		
		if True:
			gl = ax.gridlines(crs=proj, draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
			# gl.top_labels = False
			# gl.left_labels = False
			
			from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter,
											LatitudeLocator, LongitudeLocator)
			
			gl.xlocator = LongitudeLocator()
			gl.ylocator = LatitudeLocator()
			gl.xformatter = LongitudeFormatter(auto_hide=False)
			gl.yformatter = LatitudeFormatter()
			
			# set ticks params
			ax.tick_params(which='major', length=8, direction='inout', top=True, right=True, grid_transform=proj)
			ax.tick_params(which='minor', length=4, direction='in', top=True, right=True, grid_transform=proj)
			# ax.tick_params(axis="both",
						   # tickdir='out',
						   # length=15,
						   # grid_transform=proj)
		
		else:
			
			# set X-ticks in the most complex way
			tickPrec = np.power(10, max(0, -np.floor(np.log10(bounds[1]-bounds[0]))))
			ax.set_xticks(np.arange(float(int(bounds[0]*tickPrec))/tickPrec,float(int(bounds[1]*tickPrec)+2)/tickPrec))
			ax.xaxis.set_minor_locator(AutoMinorLocator(10))
			
			# set Y-ticks
			tickPrec = np.power(10, max(0, -np.floor(np.log10(bounds[3]-bounds[2]))))
			ax.set_yticks(np.arange(float(int(bounds[2]*tickPrec))/tickPrec,float(int(bounds[3]*tickPrec)+2)/tickPrec))
			ax.yaxis.set_minor_locator(AutoMinorLocator(10))
			
			# set ticks params
			ax.tick_params(which='major', length=8, direction='inout', top=True, right=True)
			ax.tick_params(which='minor', length=4, direction='in', top=True, right=True)
			
		# make room and axes for colorbars
		colorbarPad = colorbarWidth + 0.01
		nrColorbars = self.getNrvisiblecolorbars() # len(shapes)
		figDim[3] = 1.0 - figDim[0] - nrColorbars * colorbarWidth - (nrColorbars-1) * colorbarWidth # adjust width of main axes
		ax.set_position(figDim) # set new dim of main axes
		figBBox = ax.get_position() # get actual dim of main axes
		clbX = figBBox.get_points()[0,0] + figBBox.width # + colorbarWidth # x pos of first colorbar
		clbY = figBBox.get_points()[0,1]
		clbDim = [clbX, clbY, colorbarWidth, figBBox.height] # dim of first colorbar
		
		# 
		for legendtxt in self.getColortypes():
			
			if legendtxt not in shapes.keys():
				continue
						
			coll = PatchCollection(
					shapes[legendtxt],
					linewidths=0.0,
					cmap=self.getColormap(legendtxt))
			# print(f' dims of colors[{legendtxt}] = {np.array(colors[legendtxt]).shape}')
			coll.set_color(np.array(colors[legendtxt]))
			
			if valuerange:
				coll.set_clim(valuerange[0],valuerange[1])
			
			mappable = ax.add_collection(coll)
			
			if self.showColorbar(legendtxt):
				
				clbDim[0] += colorbarWidth + colorbarPad # xpos for next colorbar
				axclb=fig.add_axes(clbDim)
				
				clb = plt.colorbar(mappable, cax=axclb) #shrink=0.5) #ax=ax, default pad=0.05   ,shrink=0.25,pad=0.05
				# clb.set_label(legendtxt, labelpad=-40, y=1.05, rotation=0)
				# clb.ax.set_title(legendtxt) # at top
				clb.ax.set_xlabel(legendtxt, fontsize=14, fontweight='bold') # at bottom
				# clb.ax.invert_yaxis()
		
		plt.savefig(file_outplot, bbox_inches="tight", dpi=dpi)

def darkenColor(rgbcolor, amount):
	# print('rgbcolor = {}'.format(rgbcolor))
	hlscolor = rgb_to_hls(rgbcolor[0],rgbcolor[1],rgbcolor[2])
	ret_rgb = hls_to_rgb(hlscolor[0], 1 - amount * (1 - hlscolor[1]), hlscolor[2])
	if len(rgbcolor) > 3:
		return ret_rgb + (rgbcolor[3],)
	return ret_rgb

def getParser():
	# PARSER
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-shp','--shapefile', help='shape file to plot', required=True)
	# parser.add_argument('-out','--output', help='file to write to (OBS, overwrites!) (default adds .png to input data name)')
	# proggroup = parser.add_mutually_exclusive_group()
	# proggroup.add_argument('--showprogress', action="store_true", help='(default)')
	# proggroup.add_argument('--hideprogress', action="store_true", help='(not default)')
	# defgroup = parser.add_mutually_exclusive_group()
	# defgroup.add_argument('--ignoredefaults', action="store_true", help='(default) do not crash if default value is found (see code for default value limits)')
	# defgroup.add_argument('--crashondefaults', action="store_true", help='(not default) crash if default value is found (see code for default value limits)')
	return parser

def main(raw_args=None):
	# parser arguments
	parser = getParser()
	args = parser.parse_args(raw_args)
	
	print('\narguments:')
	for arg in vars(args):
		print(' {} = {}'.format(arg,getattr(args,arg)))
	print('--------\n')
	
	myplot(args.shapefile)

if __name__ == '__main__':
	main()
