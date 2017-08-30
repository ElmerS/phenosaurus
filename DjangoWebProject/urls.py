"""
Definition of urls for DjangoWebProject.
"""
from datetime import datetime
from django.conf.urls import url, handler400, handler403, handler404, handler500
from uniqueref.forms import BootstrapAuthenticationForm
import uniqueref.views as aviews
from django.contrib.auth import views

# Serve static files during development
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

admin.site.site_header = 'Phenosaurus management tool'

handler400 = 'uniqueref.views.bad_request'
handler403 = 'uniqueref.views.permission_denied'
handler404 = 'uniqueref.views.page_not_found'
handler500 = 'uniqueref.views.server_error'

urlpatterns = [
    # Account editing form
    url(r'^edit_account/$', aviews.edit_account, name='edit_account'),
    # Custom change password and reset forms
    url(r'^password_change/$', views.password_change,
	{'template_name': 'uniqueref/account/password_change_form.html'}),
    url(r'^password_change/done/$', views.password_change_done,
	{'template_name': 'uniqueref/account/password_change_done.html'}),
    url(r'^password_reset/$', views.password_reset,
	{'template_name': 'uniqueref/account/password_reset_form.html',
	'email_template_name': 'uniqueref/account/password_reset_email.html',
	'subject_template_name': 'uniqueref/account/password_reset_subject.txt'}),
    url(r'^password_reset/done/$', views.password_reset_done,
	{'template_name': 'uniqueref/account/password_reset_done.html'}),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.password_reset_confirm,
	{'template_name': 'uniqueref/account/password_reset_confirm.html'}),
    url(r'^reset/done/$', views.password_reset_complete,
	{'template_name': 'uniqueref/account/password_reset_complete.html'}),

    # Landing page
    url(r'^$', aviews.home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^contact$', aviews.contact, name='contact'),
    url(r'^about', aviews.about, name='about'),
    url(r'^uniqueref/', include('uniqueref.urls')),
    url(r'^login/$',
        views.login,
        {
            'template_name': 'uniqueref/account/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
               'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        views.logout,
        {
            'next_page': '/',
        },
        name='logout'),
    # Url patterns for password change and reset, see https://docs.djangoproject.com/en/1.10/topics/auth/default/
    url('^', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
