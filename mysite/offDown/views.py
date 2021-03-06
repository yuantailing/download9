# -*- coding:utf-8 -*- 
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import *
from django.template import RequestContext, loader
from django.views import generic
from django.utils import timezone
from django.utils.encoding import filepath_to_uri
import hashlib
from pyaria2 import *
import os, sys
import urllib
import json
import re
import requests
from offDown.getFilename import *


A9ClientID = 'dIKjGHUcbe8mu2TRU5V0xu4XeQk';
A9ClientSecret = 'qWvQZAxXnirkufMGB8Ij';
reCAPTCHAsecret = '6LfA3BgTAAAAANQ7oSvENM-4T0aA7-A-dwxvfxUU';

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

def regist(request):
    if not ('username' in request.POST and 'password' in request.POST and 'g-recaptcha-response' in request.POST):
        return render(request, 'offDown/regist.html');
        
    reCAPTCHAurl = 'https://www.google.com/recaptcha/api/siteverify';
    postdata = urllib.parse.urlencode({'secret': reCAPTCHAsecret, 'response': request.POST['g-recaptcha-response']});
    postdata = postdata.encode('utf-8')
    res = urllib.request.urlopen(reCAPTCHAurl, postdata);
    if json.loads(res.read().decode('utf-8'))['success'] == False:
        return render(request, 'offDown/regist.html', {
            'error_message': "你是人类吗?",
        });
    
    pattern = re.compile('([^a-z0-9A-Z])+')
    if(pattern.findall(request.POST['username'])):
        return render(request, 'offDown/regist.html', {
            'error_message': "用户名非法",
        });
    try:
        User = Users.objects.get(username = request.POST['username']);
        return render(request, 'offDown/regist.html', {
            'error_message': "用户名已存在"
        });
    except(Users.DoesNotExist):
        User = Users(username = request.POST['username'], password = request.POST['password']);
        User.save();
        return render(request, 'offDown/login.html', {
            'error_message': "注册成功"
        });

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

def github_oauth_authorize(request):
    return HttpResponseRedirect('https://github.com/login/oauth/authorize?client_id={:s}&redirect_uri={:s}'.format(settings.GITHUB_CLIENT_ID, filepath_to_uri('https://cg.cs.tsinghua.edu.cn{:s}?host={:s}'.format(reverse('offDown:oauth'), filepath_to_uri(request.get_host())))))

def oauth(request):
    code = request.GET.get('code')
    host = request.GET.get('host')
    if host == 'www.thucg.com' and request.get_host() == 'cg.cs.tsinghua.edu.cn':
        return redirect('https://www.thucg.com{:s}'.format(request.get_full_path()))
    if not code:
        return HttpResponseBadRequest('no verification code')
    res = requests.post(
        'https://github.com/login/oauth/access_token',
        data=urllib.parse.urlencode({
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
        }).encode(),
        headers={'Accept': 'application/json'},
    )
    if not res.ok:
        return HttpResponseBadRequest('bad verification code')
    res = res.json()
    if not res.get('access_token'):
        return HttpResponseBadRequest('bad verification code')
    access_token = res['access_token']
    guser = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': 'token {:s}'.format(access_token)}
    )
    guser = guser.json()
    a9_username = 'github_id__{:d}'.format(guser['id'])

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
def new2(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    if not('url' in request.POST) or not('name' in request.POST):
        return HttpResponseRedirect(reverse('offDown:index'));
    User = Users.objects.get(id = request.session['userid']);
    if User.usedTaskNumber >= User.taskNumberLimit:
        res = {'status': 'error', 'content': "超过用户任务数限制"};
        return HttpResponse(json.dumps(res));
        
    if User.usedDiskSpace >= User.diskSpaceLimit:
        res = {'status': 'error', 'content': "超过用户空间限制"};
        return HttpResponse(json.dumps(res));
    if 'magnet:?xt=urn:btih' in request.POST['url']:
        res = {'status': 'error', 'content': "暂不支持磁力链接，请将磁力链接转换成种子用BT下载"};
        return HttpResponse(json.dumps(res));
    
    try:
        con = PyAria2();
    except:
        res = {'status': 'error', 'content': "服务器出错，请与管理员联系"};
        return HttpResponse(json.dumps(res));    
    try:
        realurl, realFilename = getDownloadFilename(request.POST['url']);
        outFilename = get_md5(str(timezone.now()))[0:5] + '_' + realFilename;
        if len(outFilename) > 70:
            outFilename = get_md5(str(timezone.now()));
        Gid = con.addUri(uris=[realurl], options={'out': outFilename, 'dir':DEFAULT_DIR});
        #Gid = con.addUri(uris=[realurl], options={'dir':DEFAULT_DIR});
        
        print(Gid);
    except:
        res = {'status': 'error', 'content': "添加任务失败或URL无效，请重试"};
        return HttpResponse(json.dumps(res));
    
    try:
        T = Tasks(taskName = request.POST['name'], taskActive = 1, taskType = 1, taskUrl=request.POST['url'], taskStartTime=timezone.now(), taskGid=Gid, user=User);
        T.save();
    except:
        res = {'status': 'error', 'content': "添加任务失败或URL无效，请重试"};
        return HttpResponse(json.dumps(res));
    User.usedTaskNumber += 1;
    User.save();
    res = {'status': 'success', 'content': "success"};
    return HttpResponse(json.dumps(res));
    
    
    
    
'''        
def new(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    if not('url' in request.POST) or not('name' in request.POST):
        return HttpResponseRedirect(reverse('offDown:index'));
    
    User = Users.objects.get(id = request.session['userid']);
    if User.usedTaskNumber >= User.taskNumberLimit:
        return render(request, 'offDown/newByurl.html', {
            'error_message': "超过用户任务数限制"
        });
    if User.usedDiskSpace >= User.diskSpaceLimit:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "超过用户空间限制" 
        });
    if 'magnet:?xt=urn:btih' in request.POST['url']:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "暂不支持磁力链接，请将磁力链接转换成种子用BT下载"
        });
    
    try:
        con = PyAria2();
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "服务器出错，请与Blink联系",
        });    
    try:
        realurl, realFilename = getDownloadFilename(request.POST['url']);
        outFilename = get_md5(str(timezone.now()))[0:5] + '_' + realFilename;
        if len(outFilename) > 50:
            outFilename = get_md5(str(timezone.now()));
        Gid = con.addUri(uris=[realurl], options={'out': outFilename, 'dir':DEFAULT_DIR});
        #Gid = con.addUri(uris=[realurl], options={'dir':DEFAULT_DIR});
        
        print(Gid);
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "添加任务失败或URL无效，请重试",
        });
    
    try:
        T = Tasks(taskName = request.POST['name'], taskActive = 1, taskType = 1, taskUrl=request.POST['url'], taskStartTime=timezone.now(), taskGid=Gid, user=User);
        T.save();
    except:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "添加任务失败或URL无效，请重试!",
        });
    User.usedTaskNumber += 1;
    User.save();
    return HttpResponseRedirect(reverse('offDown:index'));
'''
    
def actDelete(taskID):
    task = Tasks.objects.get(id = taskID);
    task.taskActive = 0;
    task.save();
    con = PyAria2();
    try:
        con.tellActive();
    except:
        pass;
        
    if task.taskType == 1:
        try:
            taskStatus = con.tellStatus(task.taskGid)['status'];
            if taskStatus == 'error':
                task.taskDelFailed = 0;
                task.save();
                return ;
            #if task.taskStatus == 'active':
            #    con.forcePause(task.taskGid);
            filelist = con.tellStatus(task.taskGid)['files'];
            '''
            if len(filelist) == 0:
                task.taskDelFailed = True;
                task.save();
                return ;
            '''
            #for file in con.tellStatus(task.taskGid)['files']:
            #    os.remove(file['path']);
            
            if taskStatus == 'active':
                con.forceRemove(task.taskGid);
            if taskStatus == 'complete':
                con.removeDownloadResult(task.taskGid);
            for file in filelist:
                os.remove(file['path']);
            
        except FileNotFoundError:
            task.taskDelFailed = 0;
            
        except :
            task.taskDelFailed += 1;
            
        else :
            task.taskDelFailed = 0;
            
    if task.taskType == 2:
        try:
            con = PyAria2();
            if task.taskStatus == 'complete':
                os.remove(os.path.join(DEFAULT_DIR, task.taskFilename));
            if len(Tasks.objects.filter(taskActive=1).filter(taskHash=task.taskHash)) == 0:
                filelist = con.tellStatus(task.taskGid)['files'];
                if len(filelist) == 0:
                    task.taskDelFailed += 1;
                    task.save();
                    return ;
                con.forceRemove(task.taskGid);
                for file in filelist:
                    os.remove(file['path']);
        except FileNotFoundError:
            task.taskDelFailed = 0;
        except :
            task.taskDelFailed += 1;
        else :
            task.taskDelFailed = 0;
    task.save();            
            

def deleteTask(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    if not ('taskID' in request.GET):
        return HttpResponseRedirect(reverse('offDown:index'));
    
    task = Tasks.objects.get(id = int(request.GET['taskID']));
    if task.taskActive == 0:
        return HttpResponseRedirect(reverse('offDown:index'));
    if task.user.id != request.session['userid']:
        return HttpResponseRedirect(reverse('offDown:index'));
    task.taskActive = 0;
    task.taskDelFailed = 1;
    User = task.user;
    User.usedTaskNumber -= 1;
    User.usedDiskSpace -= task.taskFilesize;
    User.save();
    #print(task.taskGid);
    task.save();
    #actDelete(task.id);
    '''
    task.taskActive = 0;
    task.save();
    try:
        con = PyAria2();
        if task.taskStatus == 'active':
            con.forcePause(task.taskGid);
        for file in con.tellStatus(task.taskGid)['files']:
            os.remove(file['path']);
        con.forceRemove(task.taskGid);
        os.remove(os.path.join(DEFAULT_DIR, task.taskFilename));
    except:
        pass;
    '''
    return HttpResponseRedirect(reverse('offDown:index'));
    
def search(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    if('taskName' in request.GET):
        tasks = User.tasks_set.filter(taskActive = 1).filter(taskName__contains=request.GET['taskName']);
        return render(request, 'offDown/index.html', {
            'show': 'all',
            'User': User,
            'tasks': tasks,
        });
    return HttpResponseRedirect(reverse('offDown:index'));

def new_bytorrent(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    
    return render(request, 'offDown/newBytorrent.html', {
        'User': User,
    })    

def newTorrent2(request):
    from pyaria2 import DEFAULT_DIR
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    if User.usedTaskNumber >= User.taskNumberLimit:
        res = {'status': 'error', 'content': "超过用户任务数限制"};
        return HttpResponse(json.dumps(res));
        
    if User.usedDiskSpace >= User.diskSpaceLimit:
        res = {'status': 'error', 'content': "超过用户空间限制"};
        return HttpResponse(json.dumps(res));
    #save the torrent file
    try:
        f = request.FILES['torrentfile'];
        #print(f);
        fname = User.username + '_' + f.name;
        with open(os.path.join(DEFAULT_DIR , fname), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk);
    except:
        res = {'status': 'error', 'content': "存储种子文件失败，请重试或请与管理员联系"};
        return HttpResponse(json.dumps(res));
    #try to connect aria2
    try:
        con = PyAria2();
    except:
        res = {'status': 'error', 'content': "服务器出错，请与管理员联系"};
        return HttpResponse(json.dumps(res));    
        
    try:
        Gid = con.addTorrent(torrent=os.path.join(DEFAULT_DIR , fname), uris=[], options={'dir': DEFAULT_DIR});
    except:
        res = {'status': 'error', 'content': "添加任务失败或种子解析失败，请重试"};
        return HttpResponse(json.dumps(res));
        
    try:
        T = Tasks(taskName = request.POST['name'], taskActive = 1, taskType = 2, taskUrl = fname, taskStartTime=timezone.now(), taskFilename = None, taskGid=Gid, user=User);
        T.save();
    except:
        res = {'status': 'error', 'content': "添加任务失败，请重试或与管理员联系"};
        return HttpResponse(json.dumps(res));
        
    User.usedTaskNumber += 1;
    User.save();
    res = {'status': 'success', 'content': "success"};
    return HttpResponse(json.dumps(res));

'''
def newTorrent(request):
    if not checkLogin(request):
        return HttpResponseRedirect(reverse('offDown:login'));
    User = Users.objects.get(id=int(request.session['userid']));
    if User.usedTaskNumber >= User.taskNumberLimit:
        return render(request, 'offDown/newByurl.html', {
            'error_message': "超过用户任务数限制"
        });
    if User.usedDiskSpace >= User.diskSpaceLimit:
        return render(request, 'offDown/newByurl.html',{
            'error_message': "超过用户空间限制" 
        });
    #save the torrent file
    try:
        f = request.FILES['torrentfile'];
        #print(f);
        fname = User.username + '_' + f.name;
        with open(os.path.join(DEFAULT_DIR , fname), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk);
    except:
        return render(request, 'offDown/newBytorrent.html',{
            'error_message': "存储种子文件失败，请重试或请与管理员联系",
        });
    
    #try to connect aria2
    try:
        con = PyAria2();
    except:
        return render(request, 'offDown/newBytorrent.html',{
            'error_message': "服务器出错，请与管理员联系",
        });
        
    try:
        Gid = con.addTorrent(torrent=os.path.join(DEFAULT_DIR , fname), uris=[], options={'dir': DEFAULT_DIR});
    except:
        return render(request, 'offDown/newBytorrent.html',{
            'error_message': "添加任务失败或种子解析失败，请重试",
        });
        
    try:
        T = Tasks(taskName = request.POST['name'], taskActive = 1, taskType = 2, taskUrl = fname, taskStartTime=timezone.now(), taskFilename = None, taskGid=Gid, user=User);
        T.save();
    except:
        return render(request, 'offDown/newBytorrent.html',{
            'error_message': "添加任务失败，请重试或与管理员联系!",
        });
    User.usedTaskNumber += 1;
    User.save();
    return HttpResponseRedirect(reverse('offDown:index'));
'''    
    
def getStatus(request):
    if not checkLogin(request):
        return HttpResponse(json.dumps({'status': 'failed'}));
    if not ('id' in request.GET):
        return HttpResponse(json.dumps({'status': 'failed'}));
    task = Tasks.objects.get(id = int(request.GET['id']));
    if task.user.id != request.session['userid']:
        return HttpResponse(json.dumps({'status': 'failed'}));
        
    res = task.toDict();
    res['status'] = 'success';
    res['taskStartTime'] = str(res['taskStartTime']);
    res['taskCompletedTime'] = str(res['taskCompletedTime']);
    res['user'] = None;
    try:
        res['realFilename'] = urllib.parse.quote(res['taskFilename'])
    except:
        pass
    return HttpResponse(json.dumps(res));
    
