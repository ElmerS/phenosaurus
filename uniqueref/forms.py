# Import Django related libraries and functions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django_pandas.io import read_frame
from django.shortcuts import render
from django.forms import ModelForm
from django.db.models import Q
from django import forms

# Import other custom phenosaurus functions
import globalvars as gv
import models as db
import custom_functions as cf

# Other general libraries
import pandas as pd
import numpy as np
import re

# Different textsizes for labeling the genes, there should be a more sophisticated way, right?
textsize = (
	('8px', '8px'),
	('9px', '9px'),
	('10px', '10px'),
	('11px', '11px'),
	('12px', '12px'),
	('13px', '13px'),
	('14px', '14px'),
	('15px', '15px'),
	('16px', '16px'),
	('17px', '17px'),
	('18px', '18px'),
	('19px', '19px'),
	('20px', '20px'),
)

# oca = on click options
ocao= (
        ('gc', 'Link to Genecards'),
        ('hah', 'Label and highlight datapoint'),
        ('gp', 'Geneplot upon click')
)

plot_widths = (
	('small', "".join(['small: ', str(gv.small_geneplot_width), 'px'])),
	('normal', "".join(['normal: ', str(gv.normal_geneplot_width), 'px'])),
	('wide', "".join(['wide: ', str(gv.wide_geneplot_width), 'px'])),
	('dynamic', "".join(['dynamic: ', str(gv.dynamic_geneplot_width), ' px', ' * n screens']))
)

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class SingleIPSPlotForm(forms.Form):
	def __init__(self, *args, **kwargs):
		input = kwargs.pop('input')
		authorized_screens = map(int, input.strip("[]").replace(' ', '').split(','))
		super(SingleIPSPlotForm, self).__init__(*args, **kwargs)
		self.fields['screen'].queryset = db.Screen.objects.filter(id__in=authorized_screens).filter(screentype='IP').order_by('name')

	screen = forms.ModelChoiceField(queryset=db.Screen.objects.all(), label='Choose screen', widget=forms.Select(attrs={'class': 'form-control'}))
	pvalue = forms.DecimalField(required=False, label='P-value cutoff (can also be written as 1E-xx)', initial=gv.pvdc,
								widget=forms.NumberInput(attrs={'class': 'form-control'}))
	textsize = forms.ChoiceField(label='Textsize (px)', choices=textsize, initial='11px', required=True)
	oca = forms.ChoiceField(label='Select action on click', choices=ocao, initial='gc',
							widget=forms.Select(attrs={'class': 'form-control'}))
	sag = forms.BooleanField(required=False, initial=True, label='Label all significant hits', widget=forms.CheckboxInput(attrs={'class': 'checkbox'}))
	showtable = forms.BooleanField(required=False, label="List all significant genes in table", initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))

	
class OpenGeneFinderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		input = kwargs.pop('input')
		authorized_screens = map(int, input.strip("[]").replace(' ', '').split(','))
		super(OpenGeneFinderForm, self).__init__(*args, **kwargs)
		self.fields['screens'].queryset = db.Screen.objects.filter(id__in=authorized_screens).filter(screentype='IP').order_by('name')

	screens = forms.ModelMultipleChoiceField(queryset=db.Screen.objects.all(),
											 widget=forms.SelectMultiple(attrs={'size': '15', 'class': 'form-control'}),
											 label='Select screen(s)', required=False)
	genes = forms.CharField(widget=forms.TextInput(
											attrs={'class': 'form-control', 'placeholder': 'EZH2 SUZ12 EED', 'style': 'min-width: 100%'}),
											label='Enter genename(s), space separated', required=True)
	pvalue = forms.DecimalField(required=False, label='P-value cutoff (can also be written as 1E-xx)', initial=gv.pvdc,
								widget=forms.NumberInput(attrs={'class': 'form-control'}))
	description = forms.BooleanField(required=False, label="Text description of results", initial=False,
								   widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))
	hidelegend = forms.BooleanField(required=False, label="Hide legend", initial=False,
									 widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}))