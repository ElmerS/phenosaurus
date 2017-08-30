# Import Django related libraries and functions
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, HttpRequest
from django.db.models import Q, Avg, Max, Min	# To find min and max values in QS
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django import forms

# Import other custom phenosaurus functions
import models as db
import custom_functions as cf
import plots
import globalvars as gv
import forms

# Other general libraries
from datetime import datetime
import operator
from .models import *
import pandas as pd
import numpy as np
import operator
from collections import namedtuple

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Home page',
        'year':datetime.now().year,
    }
    return render(request, 'uniqueref/home.html', context)


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    context = {
	'title':'Contact',
	'message':'Brummelkamp Lab',
	'year':datetime.now().year,
    }
    return render(request, 'uniqueref/contact.html', context)


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    context = {
	'title':'About',
	'message':'Phenosaurus: a visualization platform for human haploid screens',
	'descr':'<p>The Phenosaurus platform is under active development of the Brummelkamp group in the Netherlands Cancer Institute</p><p>Lead developer: Elmer Stickel e.stickel [at] nki.nl</p><p>Other people involved in the development of the platform: Vincent Blomen</p><p>We are here to help you with any support aspect of Phenosaurus, feel free to contact us by email. If you would like to obtain private access to the platform to upload your own data and/or access experimental analysis features, please contact us.</p><p><h3>Thanks to the developers of the following libraries:</h3><ul><li><a href="https://www.djangoproject.com/">Django</a></li><li><a href="http://bokeh.pydata.org/en/latest/">Bokeh</a></li><li><a href="http://gunicorn.org/">Gunicorn</a></li><li><a href="https://www.nginx.com/">Nginx</a></li></ul>',
 	'year':datetime.now().year,
    }
    return render(request, 'uniqueref/about.html', context)

def updates(request):
	"""Renders the updates page."""
	assert isinstance(request, HttpRequest)
	context = {
		'updates': cf.get_qs_updates().order_by('-date'),
		'year': datetime.now().year,
	}
	return render(request, "uniqueref/updates.html", context)

def listgenes(request):
	"""Renders the list of genes page."""
	assert isinstance(request, HttpRequest)
	context = {
		'data': cf.list_genes(), # Call custom fucnction to draw the table
		'year': datetime.now().year,
	}
	return render(request, "uniqueref/listgenes.html", context)

def help(request):
	return render(request, "uniqueref/help.html", {})

@login_required
def password_change(request):
	"""The password change form"""
	assert isinstance(request, HttpRequest)
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	context = {
		'form': form,
		'year': datetime.now().year,
	}
	return render(request, 'uniqueref/account/password_change.html', context)

@login_required
def edit_account(request):
	"""The page where one can change some stuff related to their account"""
	assert isinstance(request, HttpRequest)
	context = {
		'year': datetime.now().year,
	}
	return render(request, 'uniqueref/account/edit_account.html', context)

def bad_request(request):
    context= {'year': datetime.now().year}
    response = render(request, 'uniqueref/error/400.html', context)
    response.status_code = 400
    return response

def permission_denied(request):
    context= {'year': datetime.now().year}
    response = render(request, 'uniqueref/error/403.html', context)
    response.status_code = 403
    return response

def page_not_found(request):
    context= {'year': datetime.now().year}
    response = render(request, 'uniqueref/error/404.html', context)
    response.status_code = 404
    return response

def server_error(request):
    context= {'year': datetime.now().year}
    response = render(request, 'uniqueref/error/500.html', context)
    response.status_code = 500
    return response

def get_authorized_screens(request):
	# Because all data is public in this version of Phenosaurs, rather than quering the group ID's (gids) of the
	# current user we, the gids variable is assigned the public group to which all the public screens belong
	gids = [gv.public_group_id]
	# For user identification replace it with the following line
	#gids = request.user.groups.values_list('id',flat=True)
	authorized_screens = cf.get_authorized_screens_from_gids(gids)
	return authorized_screens

def IPSFishtail(request):
	# To render the form, send it the data to display the right options based on the user and use a GET request to obtain the results
	authorized_screens = list(get_authorized_screens(request)) # Check user groups to see which screen are allowed to be seen
	strigefied_authorized_screens=','.join(str(i) for i in authorized_screens)	# Convert list if screens that user is allowed to see to string
	filter = forms.SingleIPSPlotForm(input=strigefied_authorized_screens) # First load the filter from .form

	# Pull the data from the URL upon submission of the form
	screenid = request.GET.get('screen', '') 		# Screenid is parsed as a number packed in a string
	oca = request.GET.get('oca', '')				# Gather on-click-action
	giventextsize = request.GET.get('textsize', '')	# This is for determining the size of labels next to a gene
	givenpvalue = request.GET.get('pvalue', '') 	# The p-value cutoff for coloring
	sag = request.GET.get('sag','') 				# Do all genes need to be labeled?
	showtable = request.GET.get('showtable', '')	# Whether a table should be drawn with raw values

	context = {'filter': filter, 'year': datetime.now().year}

	# First check if the user has given a screen as input, otherwise raise an error
	if screenid=='':
		context['error'] = gv.formerror

	# Then check if screen requested by the user is actually a screen that he/she is allowed to see.
	# This may seem a bit over the top but a user may have manually changed the URL and has entered a screenid in it of
	# screen that does not belong to this user. Although it doesn't really matter because validation always occurs too
	# prior to quering the database and not solely by this form, it is nice to know the user isn't trying to sneak around
	elif (int(screenid) in authorized_screens):
		textsize = cf.set_textsize(giventextsize)	# Check the textsize given by the user
		pvcutoff = cf.set_pvalue(givenpvalue)		# Check the p-value given by the user
		title = cf.title_single_screen_plot(screenid, authorized_screens)
		df,legend = cf.generate_df_pips(screenid, pvcutoff, authorized_screens)
		context['script'], context['div'] = plots.fishtail(title, df, sag, oca, textsize, authorized_screens) # The script and div that is generated by the pfishtailplot function and contains all plotting info
		# If the user want's to display a table of all datapoints call generate_ips_tophits function to make the table
		if showtable == "on":
			context['negreg'], context['posreg'] = cf.generate_ips_tophits_list(df)

	# If previous statement returns false, the user has manually modified the GET request in an illegal way. Serve an error.
	elif (screenid in authorized_screens)==False:
		context['error'] = gv.request_screen_authorization_error

	# And finally, just show the filter in case the user just arrived on this page and hasn't submitted the form yet
	else:
		context['error'] = gv.formerror
	return render(request, "uniqueref/singlescreen.html", context)


def opengenefinder(request):
	# Call the search- and customization form
	# Check user groups to see which screen are allowed to be seen by the user
	authorized_screens = list(get_authorized_screens(request)) # Check user groups to see which screen are allowed to be seen
	strigefied_authorized_screens=','.join(str(i) for i in authorized_screens)	# Convert list if screens that user is allowed to see to string
	filter = forms.OpenGeneFinderForm(input=strigefied_authorized_screens) # First load the filter from .forms

	# Pull the data from the URL upon submission of the form
	screenids = request.GET.getlist('screens', '') 		# The screens for which the MI-values needs to be plotted
	genenamesstring = request.GET.get('genes', '') 		# The given list of genes, presented as a string
	givenpvalue = request.GET.get('pvalue', '') 		# The p-value cutoff for coloring
	description = request.GET.get('description', '')	# Get the description of the results boolean switch

	context = {'filter':filter, 'year': datetime.now().year}
	if not screenids:
		screenids=authorized_screens

	# Then check if screens requested by the user are actually screens that he/she is allowed to see.
	# This may seem a bit over the top but a user may have manually changed the URL and has entered a screenid in it
	# of a screen that does not belong to this user. Although it doesn't really matter because validation always occurs
	# prior to quering the database as well and not solely by this form, it is nice to know the user isn't trying to
	# sneak around. First call set_screenids to test whether the given list can be converted into a list of ints.
	# Finally, also check if the length of the returned array of set_screenids if the list is empty it means
	# the conversion into a list of ints failed
	if set(cf.set_screenids(screenids)).issubset(set(authorized_screens)):
		pvcutoff = cf.set_pvalue(givenpvalue) 								# Check the p-value given by the user
		screenids_array = cf.set_screenids(screenids)					# Convert list of screens to int
		genes_array, context['error'] = cf.create_genes_array(genenamesstring) 		# Check from given genes which are in DB

		# Need some safety mechanism to prevent people plotting more than a certain numer (max_graphs) at the same time... that's just too much work
		if (len(genes_array)>gv.max_geneplots):
			context['error'] = gv.max_graphs_warning		# This may overwrite the error message from cf.create_genes_array but that isn't relevant
		# Besides people trying to plot more than 50 genes at the same time, there might be people who cannot spell or
		# enter a list of genes of which none are in the database. The all the above criteria are met, yet a plot cannot
		# be drawn. Raise an error. The error is already generated by cf.create_genes_array.
		else:
			df, error, context['text'] = cf.df_multiple_geneplot(genes_array, screenids_array, pvcutoff, authorized_screens)
			if not df.empty:
				plotlist = plots.single_gene_plots(df) # Call single_gene_plots to create a list of plotting objects
				context['script'], context['div'] = plots.vertical_geneplots_layout(plotlist)
			if error:
				context['error'] = "".join([context['error'], error])
			if not description: # If decription is not requested, do not parse it
				context['text'] = []
	else:
		context['error'] = gv.request_screen_authorization_error
	return render(request, 'uniqueref/opengenefinder.html', context)