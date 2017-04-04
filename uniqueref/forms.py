# Import Django related libraries and functions
from django.contrib.auth.decorators import login_required
from django_pandas.io import read_frame
from django.shortcuts import render
from django.forms import ModelForm
from django.db.models import Q
from django import forms

# Import other custom phenosaurus functions
import globalvars as gv
import models as db

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

class SingleIPSPlotForm(forms.Form):
	def __init__(self, *args, **kwargs):
		input = kwargs.pop('input')
		authorized_screens = map(int, input.strip("[]").replace(' ', '').split(','))
		super(SingleIPSPlotForm, self).__init__(*args, **kwargs)
		self.fields['screen'].queryset = db.Screen.objects.filter(id__in=authorized_screens).filter(screentype='IP').order_by('name')

	screen = forms.ModelChoiceField(required=True, queryset=db.Screen.objects.all(), label='Choose screen')
	pvalue = forms.DecimalField(required=False, label='P-value cutoff (can also be written as 1E-xx)', initial=gv.pvdc, widget=forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 1}))
	textsize = forms.ChoiceField(label='Textsize (px)', choices=textsize, initial='11px')
	oca = forms.ChoiceField(required=True, label='Select action on click', choices=ocao, initial='gc')
	sag = forms.BooleanField(required=False, label='Label all significant hits')
	showtable = forms.BooleanField(required=False, label="List all significant genes in table")

	
class OpenGeneFinderForm(forms.Form):
	def __init__(self, *args, **kwargs):
		input = kwargs.pop('input')
		authorized_screens = map(int, input.strip("[]").replace(' ', '').split(','))
		super(OpenGeneFinderForm, self).__init__(*args, **kwargs)
		self.fields['screens'].queryset = db.Screen.objects.filter(id__in=authorized_screens).filter(screentype='IP').order_by('name')

	screens = forms.ModelMultipleChoiceField(required=True, queryset=db.Screen.objects.all(), widget=forms.SelectMultiple(attrs={'size': '15'}), label="Select screen(s)")
	genes = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': '160'}), label='Enter genename(s), space separated')
	pvalue = forms.DecimalField(required=True, label='P-value cutoff (can also be written as 1E-xx)', initial=gv.pvdc, widget=forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 1}))
	plot_width = forms.ChoiceField(required=True, label='Plot width', choices=plot_widths, initial='small')

