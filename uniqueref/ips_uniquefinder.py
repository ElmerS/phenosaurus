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

def pipsuniquefinder(title, df, sag, oca, textsize):

		TOOLS = "resize,hover,save,pan,wheel_zoom,box_zoom,reset,tap"
		
		# Determine the min and max values for the y-axis on the plot. This still needs to be specific for a screen and/or gene. Now all datapoints throughout all screen are taken into account
		max_y = Datapoint.objects.all().aggregate(Max('mi'))
		min_y = Datapoint.objects.all().aggregate(Min('mi'))
		log_max_y = np.log2(max_y.values()[0]) 
		log_min_y = np.log2(min_y.values()[0])
		 
		p = figure(
			width=1275,
			height=900,
			y_range=(-10,10),
			x_range=(0, 5),
			tools=[TOOLS],
            title=title,
			webgl=True,
			x_axis_label = "Insertions [10log]",
			y_axis_label = "Mutational index [2log]",
			)		
	
		hover = p.select(type=HoverTool)
		
		# And the build the source
		source = ColumnDataSource(data=merged)	
		columns = ['loginsertions', 'logmi', 'name']
		df_text = pd.DataFrame(columns=columns)
		textsource = ColumnDataSource(data=df_text)
	
		# We want the toolbar on the right side
		p.toolbar_location = "below"
		p.outline_line_width = 3
		p.outline_line_alpha = 1
		p.outline_line_color = "black"
		p.text('loginsertions', 'logmi', text='name', text_color='black', source=textsource)
		initial_view = Circle(x='loginsertions', y='logmi', fill_color='highlightcolor', fill_alpha=1, line_color='highlightcolor')
		
		if oca == "hah":	
			selected_circle = Circle(fill_color='highlightcolor', line_color='highlightcolor', fill_alpha=1, line_alpha=1)
			nonselected_circle = Circle(fill_color='highlightcolor', line_color='highlightcolor', fill_alpha=transp_nsel_f, line_alpha=transp_nsel_l)
			p.add_glyph(
		  		source,
		  		initial_view,
		  		selection_glyph=selected_circle,
  				nonselection_glyph=nonselected_circle
			)
	
			source.callback = CustomJS(args=dict(textsource=textsource), code="""
		        	var inds = cb_obj.get('selected')['1d'].indices;
		        	var d1 = cb_obj.get('data');
		        	var d2 = textsource.get('data');
		        	d2['loginsertions'] = []
		        	d2['logmi'] = []
				d2['name'] = []	
		        	for (i = 0; i < inds.length; i++) {
		            		d2['loginsertions'].push(d1['loginsertions'][inds[i]])
		            		d2['logmi'].push(d1['logmi'][inds[i]])
					d2['name'].push(d1['name'][inds[i]])
		        	}
		        	textsource.trigger('change');
			""")

		hover.tooltips = [
            ('P-Value', '@fcpv'),
            ('Gene', '@name'),
            ('Screen', '@relscreen'),
            ]
		
		elif oca == "gc":
			selected_circle = initial_view
			nonselected_circle = initial_view
			p.add_glyph(
				source,
				initial_view,
				selection_glyph=selected_circle,
				nonselection_glyph=nonselected_circle
			)
			url = "http://www.genecards.org/cgi-bin/carddisp.pl?gene=@relgene_id"
			taptool = p.select(type=TapTool)
			taptool.callback = OpenURL(url=url)

	        p.line([0, 120],[0, 0], line_width=2, line_color="black")