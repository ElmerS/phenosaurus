from bokeh.plotting import figure, output_file, show, vplot
from bokeh.models.widgets import Select
from bokeh.models import HoverTool, TapTool, OpenURL, Circle, Text, CustomJS, FixedTicker, ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import components
import pandas as pd
import numpy as np
from django.contrib.auth.decorators import login_required
import operator
from math import pi
from globalvars import *
import math


# Size (ie. the surface of a circle pi*r*r) of bubble is reflect by number of insertions (nm)


def pbubbleplot(title, df, scaling, oca, sag, textsize):
	# In the positive selection bubbleplot the following is plotted along the axis
	# x = seq
	# y = logfcpv

	TOOLS = "resize,hover,save,pan,wheel_zoom,box_zoom,reset,tap"

	# Adjust plot attributes according to desired y-scaling
	if scaling=='log':
		ymin = .008
		ymax = 11
		yat="log"
#		df = df[(df['yval'] >= 0.01) & (df['yval'] <= 10)]
	else:
		ymin = -15
		ymax = 375
		hw=True
		yat='linear'

	p = figure(
		width=bubbleplotwidth,
		height=bubbleplotheight,
		y_range=(ymin,ymax),
		x_range=(0-0.05*len(df.index), 1.05*len(df.index)),
		tools=[TOOLS],
		title=title,
		webgl=True,
		x_axis_label = "Genes",
 		y_axis_label = '-log(p)',
 		y_axis_type = yat
	)

	p.xgrid.grid_line_color = None
	p.ygrid.grid_line_color = None
	p.xaxis[0].ticker=FixedTicker(ticks=[])

	# The hover guy
	hover = p.select(type=HoverTool)
	hover.tooltips = [
		('P-Value', '@fcpv'),
		('Gene', '@relgene'),
		('Insertions','@nm')
	]

	# Create a new dataframe and source that only holds the names and the positions of datapoints, used for labeling genes
 	textsource = ColumnDataSource(data=dict(txval=[], tyval=[], relgene=[]))
	# Build a ColumnDataSource from the Pandas dataframe required for Bokeh
	source = ColumnDataSource(df)
	# Define the layout of the circle (a Bokeh Glyph) if nothing has been selected, ie. the inital view
	initial_view = Circle(x='xval', y='yval', fill_color='color', line_color='black', fill_alpha=0.9, line_alpha=0.9, size='dotsize') # This is the initial view, if there's no labeling if genes, this is the only plot
	
	# In case all significant hits needs to be labled
	if sag == "on":
		p.text('txval', 'tyval', text='signame', text_color='black', text_font_size=textsize, source=source)

	if oca == "hah": # If the 'on click action' is highlight and label (hah)
		# Define how the bokeh glyphs should look if selected
		selected_circle = Circle(fill_alpha=0.9, size='dotsize', line_color='#000000', fill_color='color')
		# Define how the bokeh glyphs should look if not selected
		nonselected_circle = Circle(fill_alpha=0.5, size='dotsize', line_color='#000000', fill_color='color', line_alpha=0.5)
		# Start with creating an empty overlaying plot for the textlabels
		p.text('txval', 'tyval', text='relgene', text_color='black', text_font_size=textsize, source=textsource) # This initally is an empty p because the textsource is empty as long as no hits have been selected
		
		source.callback = CustomJS(args=dict(textsource=textsource), code="""
			var inds = cb_obj.get('selected')['1d'].indices;
			var d1 = cb_obj.get('data');
			var d2 = textsource.get('data');
			d2['txval'] = []
			d2['tyval'] = []
 			d2['relgene'] = []
			for (i = 0; i < inds.length; i++) {
				d2['txval'].push(d1['txval'][inds[i]])
				d2['tyval'].push(d1['tyval'][inds[i]])
				d2['relgene'].push(d1['relgene'][inds[i]])
			}
			textsource.trigger('change');
		""")

	elif oca == "gc": # If linking out to genecards
		selected_circle = initial_view
		nonselected_circle = initial_view

		url = "http://www.genecards.org/cgi-bin/carddisp.pl?gene=@relgene"
		taptool = p.select(type=TapTool)
		taptool.callback = OpenURL(url=url)

	# Plot the final graph
	p.add_glyph(
		source,
		initial_view,
		selection_glyph=selected_circle,
		nonselection_glyph=nonselected_circle
	)

	return p