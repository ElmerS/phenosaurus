# Import Django related libraries and functions
from django.contrib.auth.decorators import login_required

# Import Bokeh related libraries and functions
from bokeh.plotting import figure, output_file, show, vplot
from bokeh.models.widgets import Select
from bokeh.models import HoverTool, TapTool, OpenURL, Circle, Text, CustomJS, FixedTicker, ColumnDataSource, Legend
from bokeh.models.widgets import TableColumn, DataTable
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.layouts import column, row, layout, Row, Spacer, gridplot
from bokeh.charts import Bar
from bokeh.io import vplot, hplot, gridplot

# Import other custom phenosaurus functions
import models as db
import custom_functions as cf
import globalvars as gv

# Other general libraries
import pandas as pd
import numpy as np
import operator
from math import pi
import sys

import logging
from django.conf import settings

##########################################################
# 1. Fistail plots                                       #
##########################################################

def fishtail(title, df, sag, oca, textsize, authorized_screens, legend=pd.DataFrame(), setwidth=1000, setheight=700, legend_location="top_right"):

    TOOLS = "resize,hover,save,pan,wheel_zoom,box_zoom,reset,tap"

    absmin = np.absolute(df.min()['logmi'])
    absmax = np.absolute(df.max()['logmi'])
    if (absmin >= absmax):
        min = -absmin-(0.1*absmin)
        max = absmin+(0.1*absmin)
    else:
        min = -absmax-(0.1*absmax)
        max = absmax+(0.1*absmax)
    max_x = np.absolute(df.max()['loginsertions'])*1.05
    
    p = figure(
        width=setwidth,
        height=setheight,
        y_range=(min, max),
        x_range=(0, max_x),
        tools=[TOOLS],
        title=title,
        webgl=True,
        x_axis_label = "Insertions [10log]",
        y_axis_label = "Mutational index [2log]"
    )

    # This is the place for some styling of the graph
    p.toolbar_location = 'below'
    p.outline_line_width = 3
    p.outline_line_alpha = 1
    p.outline_line_color = "black"
    p.line([0, 120],[0, 0], line_width=2, line_color="black")   # This actually is part of the data but it as it merely functions a accent if the x-axis, it is under the styling tab    
    
    # The hover guy
    hover = p.select(type=HoverTool)
    hover.tooltips = [
        ('P-Value', '@fcpv'),
        ('Gene', '@relgene'),
    ]            

    # Create a ColumnDataSource from the merged dataframa
    source = ColumnDataSource(df)          
    # Create a new dataframe and source that only holds the names and the positions of datapoints, used for labeling genes
    textsource = ColumnDataSource(data=dict(loginsertions=[], logmi=[], relgene=[]))
    # Define the layout of the circle (a Bokeh Glyph) if nothing has been selected, ie. the inital view
    initial_view = Circle(x='loginsertions', y='logmi', fill_color='color', fill_alpha=1, line_color='linecolor', size=5, line_width=1) # This is the initial view, if there's no labeling if genes, this is the only plot

    # sag == "on" means that all significant genes needs to be annotated
    if sag == "on":
        p.text('loginsertions', 'logmi', text='signame', text_color='black', text_font_size=textsize, source=source)
    if oca == "hah": # If the 'on click action' is highlight and label
    # Start with creating an empty overlaying plot for the textlabels
        p.text('loginsertions', 'logmi', text='relgene', text_color='black', text_font_size=textsize, source=textsource) # This initally is an empty p because the textsource is empty as long as no hits have been selected
        # Define how the bokeh glyphs should look if selected
        selected_circle = Circle(fill_color='black', line_color='black', fill_alpha=1, line_alpha=1, size=5, line_width=1)
        # Define how the bokeh glyphs should look if not selected
        nonselected_circle = Circle(fill_color='color', line_color='linecolor', fill_alpha=gv.transp_nsel_f, line_alpha=gv.transp_nsel_l, size=5, line_width=1)
        
        source.callback = CustomJS(args=dict(textsource=textsource), code="""
            var inds = cb_obj.get('selected')['1d'].indices;
            var d1 = cb_obj.get('data');
            var d2 = textsource.get('data');
            d2['loginsertions'] = []
            d2['logmi'] = []
            d2['relgene'] = []
            for (i = 0; i < inds.length; i++) {
                d2['loginsertions'].push(d1['loginsertions'][inds[i]])
                d2['logmi'].push(d1['logmi'][inds[i]])
                d2['relgene'].push(d1['relgene'][inds[i]])
            }
            textsource.trigger('change');
        """)

    elif oca == "gc": # If linking out to genecards
        selected_circle = initial_view
        nonselected_circle = initial_view
            
        #ng = "".join("@relgene".split('@')[:2])
        url = "http://www.genecards.org/cgi-bin/carddisp.pl?gene=@relgene"
        taptool = p.select(type=TapTool)
        taptool.callback = OpenURL(url=url)

    # If linking out to geneplots
    elif oca == "gp":
        selected_circle = initial_view
        nonselected_circle = initial_view

        url = cf.create_gene_plot_url("@relgene", authorized_screens)
        taptool = p.select(type=TapTool)
        taptool.callback = OpenURL(url=url)

    # Plot the final graph  
    p.add_glyph(
        source,
        initial_view,
        selection_glyph=selected_circle,
        nonselection_glyph=nonselected_circle
    )

    r = row(children=[p], responsive=True)
    script, div = components(r, CDN)
    return script, div



##########################################################
# 3. Single gene plots (genefinder histogram things)     #
##########################################################

def single_gene_plots(df_all, hidelegend=False):
    # A limited set of tools
    TOOLS = "resize,save,pan,wheel_zoom,box_zoom,reset,hover"
    # The labels for the x-axis
    x_range = [str(screen) for screen in df_all.relscreen.unique()]
    # Now we create a dictionary that uses the genenames to create variables. An sich this is a nice approach but because dictionaries are intrinsically unsorted, the plots will have an unsorted order in which they appear under each other
    figures = {str(name): 0 for name in df_all.relgene.unique()}
    # Now we create another empty array, which will hold the actual plotobjects instead of the variables
    # The reason for restructing like this is that bokeh gridplot can only handle an array of plot objects, and certainly not a dict of variables
    calculated_plot_width = cf.calc_geneplot_width('normal', len(x_range))
    plot_dict = {}
    print('x-range: ', x_range)
    print('figures: ', figures)
    for y in figures:
        df = df_all[df_all['relgene']==y]
        print("current df: ", df)
        title=y
        source = ColumnDataSource(df)
        # This gives optimal separation of the datapoints but 0 is not always in the middle (or present at all!)... would that be desirable?
        absmin = np.absolute(df['logmi'].min())
        absmax = np.absolute(df['logmi'].max())
        if (absmin >= absmax):
            min = -absmin-(0.1*absmin)
            max = absmin+(0.1*absmin)
        else:
            min = -absmax-(0.1*absmax)
            max = absmax+(0.1*absmax)
        figures[y] = figure(
            width=calculated_plot_width,
            height=400,
            y_range=(min, max),
            x_range=x_range,
            tools=[TOOLS],
            title=title,
            min_border_left=65,
            min_border_top=45,
            toolbar_location='above',
            sizing_mode = 'scale_both'
        )
        figures[y].circle('relscreen', 'logmi', color='color', alpha=1, source=source, size=10)
        figures[y].xaxis.major_label_orientation = pi/4
        # The hover guy
        hover = figures[y].select(type=HoverTool)
        hover.tooltips = [
            ('P-Value', '@fcpv'),
            ('log(MI)', '@logmi'),
            ('Screen', '@relscreen'),
        ]

        if not hidelegend:
            legend = Legend(items=[
                ('Pos. reg', [figures[y].circle(x=0, y=0, color=gv.color_sb)]),
                ('Neg. reg', [figures[y].circle(x=0, y=0, color=gv.color_st)]),
                ('Not sign', [figures[y].circle(x=0, y=0, color=gv.color_ns)])],
                location='top_right'
            )
            legend.orientation = 'horizontal'
            legend.background_fill_alpha = 0.1
            legend.background_fill_color = gv.legend_background
            legend.border_line_width = 1
            legend.border_line_color = "black"
            legend.border_line_alpha = 0.3

            figures[y].add_layout(legend)
        plot_dict[y] = figures[y]

    return(plot_dict.values())


##########################################################
# 4. Vertical layout of geneplots                        #
##########################################################

def vertical_geneplots_layout(list_of_geneplot_objects):
    p = column(list_of_geneplot_objects, responsive=True)
    script, div = components(p)
    return script, div
