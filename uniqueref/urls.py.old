# Import Django related libraries and functions
from django.conf.urls import url
import django.contrib.auth.views

# Import other custom phenosaurus functions
import views as cv # cv = custom views

urlpatterns = [
	url(r'^$', cv.landing, name='landing'),
	url(r'^simpleplot/', cv.IPSFishtail, name='Fishtail plot of intracellular phenotype screen'),
	url(r'^listgenes/', cv.listgenes, name='List of all genes and their genomic coordinates in the database'),
	url(r'^opengenefinder/', cv.opengenefinder, name='Plot the effect of a gene on multiple phenotypes'),
	url(r'^help/', cv.help, name='Documentation'),
	url(r'^updates/', cv.updates, name='Update History'),
]