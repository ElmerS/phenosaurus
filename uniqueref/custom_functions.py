# Import Django related libraries and functions
from django_pandas.io import read_frame
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.db.models import Q, Avg, Max, Min

# Import other custom phenosaurus functions
import plots
import globalvars as gv
import models as db

# Other general libraries
from collections import Counter
import pandas as pd
import numpy as np
import operator
import requests
import sys
import ast
import math


##########################################################
# 1. Querysets                                           #
##########################################################

####################################################################################################################
#                            !!!! QUERYSETS ARE EXCLUSIVELY ALLOWED HERE !!!!                                      #
####################################################################################################################

# Use the gids argument to list which screens a user is allowed to see
# The information is stored in the ScreenPermissions model
# Although the authorization is not required for the public version, it is still used because it
# renders the code future proof when at some point authetication is required

def get_authorized_screens_from_gids(gids):
    authorized_screens =  db.Screen.objects.filter(groups__in=gids).distinct().values_list('id',flat=True)
    return authorized_screens

def authorized_qs_screen(authorized_screens):
    qs_screen = db.Screen.objects.filter(id__in=authorized_screens)
    return qs_screen

def authorized_qs_IPSDatapoint(authorized_screens):
    qs_IPSDatapoint = db.IPSDatapoint.objects.filter(relscreen_id__in=authorized_screens)
    return qs_IPSDatapoint

# Query the genes and create dataframe, always needed, no authorization required
def get_qs_gene():
    qs_gene = db.Gene.objects.all()
    return qs_gene

def get_qs_updates():
    qs_updates = db.UpdateHistory.objects.all()
    return qs_updates


####################################################################################################################
#                                !!!!     NO QUERYSETS ALLOWED BELOW THIS LINE!!!                                  #
####################################################################################################################

##########################################################
# 2. General Functions                                   #
##########################################################

def create_df_gene():
    df_gene=get_qs_gene().to_dataframe() #Create a dataframe from all genes
    return df_gene

# Find max mi value of current dataframe
def findmax(df):
    max = df['mi'].max()
    max = max*1.1
    return max

# Find min mi value of current dataframe
def findmin(df):
    min = df['mi'].min()
    min = min*1.1
    return min


# A general function for splitting arrays, use as split(array, new arraylength)
def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arr
 
 # Convert values to log, we do it here because it makes it easy to change the log-value app-wide at once 
def logconversion(val):
    logval = np.log2(val)
    return logval

# A function to determine the size of text-labels
def set_textsize(giventextsize):
    if giventextsize in gv.text_sizes:
        textsize = giventextsize
    else:                                   # Return default value if input could not be converted into a float
        textsize = gv.standard_text_size       # (ie. someone has changed the textsize in URL to something like 'HOI'
    return textsize                         # rather than <int>px)

# A fuctions to set the p-value cutoff
def set_pvalue(givenpvalue):
    try:
        pvcutoff = float(givenpvalue)
    except:                                 # Return default value if input could not be converted into a float
        pvcutoff = gv.pvdc                     # (ie. someone has changed the pvalue in URL to something like 'HOI'
    return pvcutoff                         # rather than number)

def set_screenids(screenids):
    try:                                    # Test the list if given screen-id's can be converted into a list of ints
        screenids_int = map(int, screenids) # if that's not the case the user may have manually changed the URL to
    except:                                 # something like 'HOI'. If that's the case an empty list is returned
        screenids_int = []
    return screenids_int

# Function to generate the title for a plot displaying a single screen
def title_single_screen_plot(screenid, authorized_screens):
    df_screenname = authorized_qs_screen(authorized_screens).filter(id=screenid).to_dataframe()
    title = df_screenname.get_value(0, 'description') # Extract the description of the screen
    return title

# This function takes the list of genes that a user provides and checks it against the genes in the database.
# Doing so allows to reporting an error if a gene wasn't found and (in case custom tracks are implemented in the
# public function guarentees tracks without errors.
def create_genes_array(input_string, upload=False):
    # First receive the list of genes given by the user as a string and split that string into an array, values are space separated
    input_list = input_string.split()
    qs_gene = get_qs_gene()
    # Before parsing back the list as array it is really essential to check if the genes actually exist in the database, otherwise we may run into NaN errors
    # Therefore, use the list to query the gene-table return whatever matched the gene-names in the table
    # We may want to raise an error....?
    validated_list = qs_gene.filter(name__in=input_list).to_dataframe()['name'].tolist()
    validated_array = np.asarray(validated_list)
    if (len(input_list) != len(validated_list)):
        non_match_list = list(set(input_list) - set(validated_list)) # Find the items that do not match the databse
        url_list = []
        for x in non_match_list:
            url_list.append(''.join(('<a href=\"', gv.ucsc_link, x.split("@")[0], '\"', '>', x, '</a>'))) # The quotation marks before join are the separator, ie. theres is no separator
        url_list_join = ','.join(url_list) # The genes themself we want to separate by a comma
        suggested_genes = find_somewhat_matching_gene_names(non_match_list)
        error = "%s %s %s<br>%s %s<p>" %(gv.gene_not_found_error, url_list_join, gv.genome_browser_link_text, gv.suggested_genes_text, suggested_genes)
    else:
        error = ''
    return validated_array, error

# If the user has provided a genename that was not found in the database (using create_genes_array) return a link to
# the USCS genome browser so the user may find the refseq name or identify why it is not in the database
def find_somewhat_matching_gene_names(non_match_list):
    qs_gene = get_qs_gene()
    contains_list = []
    for x in non_match_list:
        contains_list = np.concatenate((contains_list, qs_gene.filter(name__icontains=x).to_dataframe()['name'].tolist()), axis=0)
    suggestedlist = ', '.join(contains_list)
    return suggestedlist

def convert_geneids_to_genenames(geneids_array):
    qs_gene = get_qs_genes()
    genes_array = qs_gene.filter(id__in=geneids_array).to_dataframe()['name'].tolist()
    return genes_array


def create_gene_plot_url(relgenestring, authorized_screens):
    screenids = authorized_qs_screen(authorized_screens).filter(screentype='IP').to_dataframe()['id'].values.tolist()
    screen_part_url = ''
    for i in screenids:
        curr_scr = 'screens='+str(i)+'&'
        screen_part_url = ''.join([screen_part_url, curr_scr])
    genes = '+'.join(relgenestring.split())
    url = '../opengenefinder/?'+screen_part_url+'genes='+genes+'&pgh=on&oca=gc&pvalue=&pvaluepss=&cb=cbpv&textsize=11px&plot_width=small'
    return url



#############################################################
# 3. Functions specific for intracellular phenotype screens #
#############################################################

# 3.1 This function generates the DataFrame for a Plotting a Intracellular Phenotype Screen (pips)
def generate_df_pips(screenid, pvcutoff, authorized_screens):

    # Query the datapoints from the database and get all datapoints that match screenid from the QuerySet and create a Dataframe
    qs_datapoint=authorized_qs_IPSDatapoint(authorized_screens).filter(relscreen_id=screenid).only('relgene', 'fcpv', 'mi', 'insertions')
    df_datapoint=qs_datapoint.to_dataframe() #
    df_gene = create_df_gene()

    # Create a new column in the dataframe datapoint that functions as the colorlabel, depending on the cutoff p-value 
    df_datapoint['color'] = np.where(df_datapoint['fcpv']<=pvcutoff, np.where(df_datapoint['mi']<1, gv.color_sb, gv.color_st), gv.color_ns)
    df_datapoint['linecolor'] = df_datapoint['color']

    # Convert raw data into 10log values
    df_datapoint['loginsertions'] = np.log10(df_datapoint['insertions'])
    df_datapoint['logmi'] = np.log2(df_datapoint['mi'])
    # Create an extra column in the dataframe that 
    df_datapoint['signame'] = np.where(df_datapoint['fcpv']<=pvcutoff, df_datapoint['relgene'], "")
    # Merge the dataframe holding all genes and datapoints, as the gene-descriptions in the genes tables is not yet filled, this has no function yet.... except for slowing down everything
    df = pd.merge(df_gene, df_datapoint, left_on='name', right_on='relgene')
    legend = pd.DataFrame()
    return df, legend

# 3.3: A tiny wee little function to generate a table from all significant hits in the dataframe
# As this file is actually all about data manipulation and the generate_ps_tophits is more about displaying data, is should be moved at some point to another file dedicated to displaying data
def generate_ips_tophits_list(df):
    df_top = df[(df['signame'] != "")][['relgene', 'low', 'high', 'fcpv', 'logmi']]
    df_top.rename(columns={'logmi': 'log2(MI)'}, inplace=True)
    # Change the relgene column to a url (and remove the part after the @ in case of extended genenames)
    df_top['relgene'] = '<a href=\"' + gv.ucsc_link + df_top['relgene'].str.split("@", 1).str[0] + '\"' + 'target=\"_blank\"' + '>' + df_top['relgene'] + '</a>'
    if (not df_top.empty):  # We need this because if someone plots a track of which none of the genes is present in the screen it will crash
        with pd.option_context('display.max_colwidth', -1):
            negreg = df_top[df_top['log2(MI)']>=0].sort_values(by='log2(MI)', ascending=False).to_html(index=False, justify='left', escape=False)
            posreg = df_top[df_top['log2(MI)']<0].sort_values(by='log2(MI)').to_html(index=False, justify='left', escape=False)
    else:
        negreg, posreg = ""
    return negreg, posreg


#############################################################
# 4. Functions specific for GenePlots                       #
#############################################################

# This function is once called from single_gene_plots to create a single dataframe containing all genes
def df_multiple_geneplot(genes, screenids_array, pvcutoff, authorized_screens):
    error = ""
    text = []
    genes_without_data = []
    df = pd.DataFrame(columns=['relgene', 'relscreen', 'mi', 'fcpv'])
    for gene in genes:
        current_qs_datapoint = authorized_qs_IPSDatapoint(authorized_screens).filter(relgene__name=gene,
                                                                             relscreen_id__in=screenids_array)
        if not current_qs_datapoint.exists():
            genes_without_data.append(gene)

        else:
            current_df = current_qs_datapoint.to_dataframe()[['relgene', 'relscreen', 'mi', 'fcpv']]
            current_df['logmi'] = np.log2(current_df['mi'])
            current_df['color'] = np.where(current_df['fcpv'] <= pvcutoff, np.where(current_df['mi'] < 1, gv.color_sb, gv.color_st),
                                   gv.color_ns)
            df = pd.concat([df, current_df])
            text.append(create_textual_description(gene, current_df, pvcutoff))

    if len(genes_without_data)>0:
        gene_urls = [''.join(('<a href=\"', gv.ucsc_link, x.split("@")[0], '\"', '>', x, '</a>')) for x in genes_without_data]
        error = gv.geneplot_no_data % " ".join([str(x) for x in gene_urls])

    return df, error, text

def create_textual_description(gene, current_df, pvcutoff):
    # Create a textual description for the effect the requested genes
    pos_screens = current_df[(current_df['fcpv'] <= pvcutoff) & (current_df['mi'] < 1)]['relscreen'].tolist()
    if len(pos_screens) > 1:
        pos_screen_text = " and ".join([", ".join(pos_screens[:-1]), pos_screens[-1]])
    else:
        pos_screen_text = "".join(pos_screens)
    neg_screens = current_df[(current_df['fcpv'] <= pvcutoff) & (current_df['mi'] >= 1)]['relscreen'].tolist()
    if len(neg_screens) > 1:
        neg_screen_text = " and ".join([", ".join(neg_screens[:-1]), neg_screens[-1]])
    else:
        neg_screen_text = "".join(neg_screens)

    current_text = "In %s screen(s) in human haploid (HAP1) cells %s was found to be regulator." % (
    str(len(pos_screens) + len(neg_screens)), gene)
    if ((len(pos_screens) > 0) or len(neg_screens) > 0):
        current_text = " ".join([current_text, "Specifically it was found to"])
        if (len(pos_screens) == 0):
            current_text = " ".join(
                [current_text, "negatively affect the abundance of %s" % neg_screen_text])
        elif (len(neg_screens) == 0):
            current_text = " ".join(
                [current_text, "positively affect the abundance of %s" % pos_screen_text])
        else:
            current_text = " ".join([
                current_text,
                " negatively affect the abundance of %s" % neg_screen_text,
                "and",
                "positively affect the abundance of %s" % pos_screen_text
            ])
    return current_text


def calc_geneplot_width(plot_width, screens):
    if plot_width == 'dynamic':
        width = screens*gv.dynamic_geneplot_width+100
    elif plot_width == 'small':
        width = gv.small_geneplot_width
    elif plot_width == 'normal':
        width = gv.normal_geneplot_width
    elif plot_width == 'wide':
        width = gv.wide_geneplot_width
    else:
        width = gv.normal_geneplot_width
    return width

##########################################################
# 5. Data acquisition for lists (genes, screens and tracks) #
##########################################################

def list_genes():
    df = create_df_gene()[['name','chromosome', 'orientation']]
    data = df.sort_values(by='name').to_html(index=False, justify='left')
    return data
