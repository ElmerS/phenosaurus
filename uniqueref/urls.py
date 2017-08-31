from django.conf.urls import url
import django.contrib.auth.views
from .views import *
from .admin import phenosaurusadmin

urlpatterns = [
	url(r'^$', home, name='home'),
	url(r'^simpleplot/', IPSFishtail, name='Single Intracellular Fixed Screen'),
	url(r'^listgenes/', listgenes, name='List all Genes'),
	url(r'^opengenefinder/', opengenefinder, name='Find gene'),
	url(r'^help/', help, name='Documentation'),
	url(r'^updates/', updates, name='Update History'),
]
