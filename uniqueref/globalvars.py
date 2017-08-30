import pandas as pd
from bokeh.palettes import Blues9, Reds9

# A bunch of global statics
#----------------------------
# The colorspace to pick colors from when plotting multiple screens on top of each other
df_colorspace = pd.DataFrame([[0,"#DF3A01"],[1,"#DF0101"],[2,"#04B486"],[3,"#0040FF"],[4,"#8000FF"],[5,"#FF00FF"],[6,"#A52A2A"],[7,"#5F9EA0"],[8,"#7FFF00"],[9,"#D2691E"],[10,"#FF7F50"],[11,"#6495ED"],[12,"#DC143C"],[13,"#00FFFF"],[14,"#00008B"],[15,"#008B8B"],[16,"#B8860B"],[17,"#A9A9A9"],[18,"#006400"],[19,"#BDB76B"],[20,"#8B008B"],[21,"#556B2F"],[22,"#FF8C00"],[23,"#9932CC"],[24,"#8B0000"],[25,"#E9967A"],[26,"#8FBC8F"],[27,"#483D8B"],[28,"#2F4F4F"],[29,"#00CED1"],[30,"#9400D3"],[31,"#FF1493"],[32,"#00BFFF"],[33,"#696969"],[34,"#1E90FF"],[35,"#B22222"],[36,"#228B22"],[37,"#FF00FF"],[38,"#FFD700"],[39,"#DAA520"],[40,"#808080"],[41,"#008000"],[42,"#ADFF2F"],[43,"#FF69B4"],[44,"#CD5C5C"],[45,"#4B0082"],[46,"#F0E68C"],[47,"#ADD8E6"],[48,"#F08080"],[49,"#D3D3D3"],[50,"#90EE90"],[51,"#FFB6C1"],[52,"#FFA07A"],[53,"#20B2AA"],[54,"#87CEFA"],[55,"#778899"],[56,"#B0C4DE"],[57,"#00FF00"],[58,"#32CD32"],[59,"#FAF0E6"],[60,"#FF00FF"],[61,"#800000"],[62,"#66CDAA"],[63,"#0000CD"],[64,"#BA55D3"],[65,"#9370DB"],[66,"#3CB371"],[67,"#7B68EE"],[68,"#00FA9A"],[69,"#48D1CC"],[70,"#C71585"],[71,"#191970"],[72,"#000080"],[73,"#FDF5E6"],[74,"#808000"],[75,"#6B8E23"],[76,"#FFA500"],[77,"#FF4500"],[78,"#DA70D6"],[79,"#EEE8AA"],[80,"#98FB98"],[81,"#AFEEEE"],[82,"#DB7093"],[83,"#FFEFD5"],[84,"#FFDAB9"],[85,"#CD853F"],[86,"#FFC0CB"],[87,"#DDA0DD"],[88,"#B0E0E6"],[89,"#800080"],[90,"#663399"],[91,"#FF0000"],[92,"#BC8F8F"],[93,"#4169E1"],[94,"#8B4513"],[95,"#FA8072"],[96,"#F4A460"],[97,"#FFF5EE"],[98,"#A0522D"],[99,"#C0C0C0"],[100,"#87CEEB"],[101,"#6A5ACD"],[102,"#708090"],[103,"#00FF7F"],[104,"#4682B4"],[105,"#D2B48C"],[106,"#008080"],[107,"#D8BFD8"],[108,"#FF6347"],[109,"#40E0D0"],[110,"#EE82EE"],[111,"#F5DEB3"],[112,"#FFFF00"]], columns=["id","color"])
# The exception color should be easy distinguisable from any color in df_colorspace, this still needs to be checked!
exception_color = '#33cc33'
df_custom_track_colors = pd.DataFrame([[0, "#FFA82E"], [1, '#FF4A2E'], [2, '#DBC500'], [3, '#96E100'], [4, '#009914'], [5, '#00DAD2'], [6, '#0066DA'], [7, '#16048B'], [8, '#910DCE'], [9, '#F442BC']], columns=["id","color"])

# The ID of the public group
public_group_id = 1

# The maximum number of geneplots for a single request
max_geneplots = 50

# Available text sizes
text_sizes = ['8px', '9px', '10px', '11px', '12px', '13px', '14px', '15px', '16px', '17px', '18px', '19px', '20px']

# The color of not-significant hits:
color_ns = '#D2D2D2'
color_sig_non_colored = '#4d4d4d'

# The color of significant hits on the top of the graph
color_st = '#FEC026'

# The color of significant hit on the bottom of the graph
color_sb = '#4C86C6'

# The color of the 'low' channel reads
color_low_rr = '#a00808' # Raw reads
color_low_ur = '#ff6666' # Unique reads
color_low_mr = '#ffb342' # Unique reads

# The color of the 'high' channel reads
color_high_rr = '#400877' # Raw reads
color_high_ur = '#9933ff' # Unique reads
color_high_mr = '#874848' # Unique reads

title_raw_reads_graph = 'Total number of sequence reads in low and high channel'
title_unique_reads_graph = 'Total number of unique sequence reads and mapped reads in low and high channel'

pss_highlight_color = '#8c1aff'


standard_legend = pd.DataFrame([['pos. regulator', color_sb],['neg. regulator', color_st], ['not significant', color_ns]], columns=['desc', 'color'])

# The default p-value cutoff, p-value-default-cutoff
pvdc = 0.05

# The transparancy of the non-selected hits when one or multiple hits are selected
# The transparancy of the line surrount the hit
transp_nsel_l = 0.4

# The (inside of the circle) fill of the hit
transp_nsel_f = 0.4

bubbleplotwidth=1440
bubbleplotheight=900

pss_color_s = '#B4045F'
pss_color_ns = '#BDBDBD'

standard_text_size = '12px'

small_geneplot_width = 800
normal_geneplot_width = 1440
wide_geneplot_width = 2120
dynamic_geneplot_width = 30

max_graphs = 50

publicuser = 'public'

# Make sure both color palelletes are of the same length!
unique_finder_arrow_less_sign = pd.Series(Blues9[::-1])
unique_finder_arrow_more_sign = pd.Series(Reds9[::-1])
minimal_logmi_difference = 1.5

#
# Error messages
#
coloroverlay_mi_error= 'Please select only 1 screen to compare against in the color-overlay and MI-arrows function'
max_graphs_warning = 'Go draw your own plots, I am not drawing more than 50 plots on one page!'
formerror = "<i>Please fill in all required fields of the form</i>"
failed_track_upload = 'Failed to store your track, please check the input forms'
succes_track_upload = 'Your track was succesfully stored in the database!'
gene_not_found_error = 'Could not find these genes in the database: '
genome_browser_link_text = '(click on names to see them in the USCS genome browser)'
suggested_genes_text = 'You might be looking for these gene(s): '
delete_track_validation_succes = 'You successfully deleted the following tracks'
delete_track_validation_error = 'You little bastard! It seems you trying to fool me by changing the URL and either trying the remove a track that had already been removed or trying to remove someone else track. Ill watch you!'
compare_screen_against_itself_error = 'Some people say stupid questions do not exists. Well you just asked one. I refuse do go through a lot of calculations to find out that you are comparing a screen against itself. You do not need me to visualize the resulting plot'
request_screen_authorization_error = 'OK well this is serious. YOU and I have a problem. It seems you have modified the URL to see data that is not yours. I dont like it at all. Instead of using a POST request I provide you with a GET request so you can easily bookmark, share and quickly modify your complex queries and this is what I get? Just don\'t. I have logged this mischievous attempt and your IP-address.'
geneplot_no_data = "In our reference database an annotation for the gene(s) %s exists but none of the screens you requested yielded information about them. Possibly the associated genomic region shows too much homology with other regions to be able to unambiguously align insertions to this region, alternatively the genetrap never landed in the region or the knockout is lethal. Click the name of the gene to see it in the UCSC genome browser."

#
# Links
#
ucsc_link = 'https://genome.ucsc.edu/cgi-bin/hgTracks?position='
