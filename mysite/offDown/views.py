from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import *
from django.template import RequestContext, loader
from django.views import generic
from django.utils import timezone
import hashlib
from offDown.pyaria2 import *
import os, sys
import urllib
import json

A9ClientID = 'dIKjGHUcbe8mu2TRU5V0xu4XeQk';
A9ClientSecret = 'qWvQZAxXnirkufMGB8Ij';

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
        #print('hash=', hash_v);
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

def oauth(request):
    
    try:
        code = request.GET['code'];
        a9url = 'https://accounts.net9.org/api/access_token?client_id=' + A9ClientID + '&client_secret=' + A9ClientSecret + '&code=' + code;
        res = urllib.request.urlopen(a9url);
        token = json.loads(res.read().decode('utf-8'))['access_token'];
        info_url = 'https://accounts.net9.org/api/userinfo?access_token=' + token;
        res = urllib.request.urlopen(info_url);
        User_info = json.loads(res.read().decode('utf-8'));
        a9_username = User_info['user']['name'] + '__a9';
    except:
        HttpResponseRedirect(reverse('offDown:login'));
    
    try:
        User = Users.objects.get(username = a9_username);    
    except(Users.DoesNotExist):
        User = Users(username = a9_username, password = get_md5(str(timezone.now())));
        User.save();
    request.session['userid'] = User.id;
    print(User.id);
    return HttpResponseRedirect(reverse('offDown:index'));

def index(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    if(not('show' in request.GET) or (request.GET['show']=='all')):
        tasks = User.tasks_set.filter(taskActive = 1);
        return render(request, 'offDown/index.html', {
            'show': 'all',
            'User': User,
            'tasks': tasks,
        });
    elif request.GET['show']=='completed' :
        tasks = User.tasks_set.filter(taskActive = 1).exclude(taskCompletedTime = None)
        return render(request, 'offDown/index.html', {
            'show': 'completed',
            'User': User,
            'tasks': tasks,
        });
    elif request.GET['show']=='incompleted' :
        tasks = User.tasks_set.filter(taskActive = 1, taskCompletedTime = None)
        return render(request, 'offDown/index.html', {
            'show': 'incompleted',
            'User': User,
            'tasks': tasks,
        });
    
def new_byurl(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    
    return render(request, 'offDown/newByurl.html', {
        'User': User,
    })

def new(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    if not('url' in request.POST) or not('name' in request.POST):
        return HttpResponseRedirect(reverse('offDown:index'));
    try:
        con = PyAria2();
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "服务器出错，请与Blink联系",
        });
        
    try:
        outFilename = get_md5(str(timezone.now()));
        Gid = con.addUri(uris=[request.POST['url']], options={'out':outFilename, 'dir':DEFAULT_DIR});
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "添加任务失败或URL无效，请重试",
        });
    User = Users.objects.get(id = request.session['userid']);
    try:
        T = Tasks(taskName = request.POST['name'], taskActive = 1, taskType = 1, taskUrl=request.POST['url'], taskStartTime=timezone.now(), taskFilename=outFilename, taskGid=Gid, user=User);
        T.save();
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "添加任务失败或URL无效，请重试!",
        });
    
    return HttpResponseRedirect(reverse('offDown:index'));
    

def deleteTask(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    if not ('taskID' in request.GET):
        return HttpResponseRedirect(reverse('offDown:index'));
    
    task = Tasks.objects.get(id = int(request.GET['taskID']));
    if task.user.id != request.session['userid']:
        return HttpResponseRedirect(reverse('offDown:index'));
    task.taskActive = 0;
    task.save();
    os.remove(os.path.join(DEFAULT_DIR, task.taskFilename));
    return HttpResponseRedirect(reverse('offDown:index'));