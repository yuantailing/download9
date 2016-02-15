from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import *
from django.template import RequestContext, loader
from django.views import generic

# Create your views here.
def login(request):
    return render(request, 'offDown/login.html');