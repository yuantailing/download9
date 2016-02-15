from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import *
from django.template import RequestContext, loader
from django.views import generic
from django.utils import timezone
import hashlib

def get_md5(my_str):
    md5 = hashlib.md5();
    md5.update(my_str.encode('utf-8'));
    return md5.hexdigest();

def checkLogin(request):
    if 'userid' in request.session :
        return 1;
    if 'keepaliveHash' in request.COOKIES :
        HttpResponse('ok');
        hash_v = request.COOKIES['keepaliveHash'];
        print('hash=', hash_v);
        try:
            User = Users.objects.get(keepaliveHash = hash_v);
        except(Users.DoesNotExist):
            return 0;
        request.session['userid'] = User.id;
        return 1;
    return 0;
    
    
def logout(request):
    response = HttpResponseRedirect(reverse('offDown:login'));
    if not checkLogin(request):
        return response;
    User = Users.objects.get(id = request.session['userid']);
    User.keepaliveHash = None;
    User.save();
    try:
        response.delete_cookie('keepaliveHash');
    except:
        pass;
    
    try:
        del request.session['userid'];
    except:
        pass;
        
    return response;
    
def login(request):
    if checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:index'));
    try:
        User = Users.objects.get(username=request.POST['username']);
    except(Users.DoesNotExist):
        return render(request, 'offDown/login.html',{
            'error_message': "用户不存在!",
        });
    except(KeyError):
        return render(request, 'offDown/login.html');
    
    if request.POST['password'] != User.password:
        return render(request, 'offDown/login.html',{
            'error_message': "密码错误!",
        });
    request.session['userid'] = User.id;
    
    response = HttpResponseRedirect(reverse('offDown:index'));
    
    if 'remember' in request.POST and request.POST['remember'] == '1':
        hash_v = get_md5(str(timezone.now()));
        response.set_cookie('keepaliveHash', hash_v, 2592000);
        User.keepaliveHash = hash_v;
    else:
        User.keepaliveHash = None;
    
    User.save();
        
    return response;

def index(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    return HttpResponse("success");