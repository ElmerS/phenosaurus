"""
Definition of views.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    context = {
        'title':'Home page',
        'year':datetime.now().year,
    }
    return render(request, 'app/home.html', context)


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    context = {
	'title':'Contact',
	'message':'Brummelkamp Lab',
	'year':datetime.now().year,
    }
    return render(request, 'app/contact.html', context)


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    context = {
	'title':'About',
	'message':'Phenosaurus: a visualization platform for human haploid screens',
	'descr':'<p>The Phenosaurus platform is under active development of the Brummelkamp group in the Netherlands Cancer Institute</p><p>Lead developer: Elmer Stickel e.stickel [at] nki.nl</p><p>Other people involved in the development of the platform: Vincent Blomen</p><p>We are here to help you with any support aspect of Phenosaurus, feel free to contact us by email. If you would like to obtain private access to the platform to upload your own data and/or access experimental analysis features, please contact us.</p><p><h3>Thanks to the developers of the following libraries:</h3><ul><li><a href="https://www.djangoproject.com/">Django</a></li><li><a href="http://bokeh.pydata.org/en/latest/">Bokeh</a></li><li><a href="http://gunicorn.org/">Gunicorn</a></li><li><a href="https://www.nginx.com/">Nginx</a></li></ul>',
 	'year':datetime.now().year,
    }
    return render(request, 'app/about.html', context)


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            #return redirect('accounts:change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'app/password_change.html', {
        'form': form
    })

@login_required
def edit_account(request):
   return render(request, 'app/edit_account.html', {})

def bad_request(request):
    context= {'year': datetime.now().year}
    response = render(request, 'app/400.html', context)
    response.status_code = 400
    return response

def permission_denied(request):
    context= {'year': datetime.now().year}
    response = render(request, 'app/403.html', context)
    response.status_code = 403
    return response

def page_not_found(request):
    context= {'year': datetime.now().year}
    response = render(request, 'app/404.html', context)
    response.status_code = 404
    return response

def server_error(request):
    context= {'year': datetime.now().year}
    response = render(request, 'app/500.html', context)
    response.status_code = 500
    return response
