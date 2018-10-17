import os,sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from offDown.models import *
from pyaria2 import *
import time
import mysite.settings
import zipfile 
from offDown.views import get_md5, actDelete
from django.utils import timezone
import hashlib
import os
con = PyAria2();

def compress(filesInfo):
    zipFilename = get_md5(str(timezone.now())) + '.zip';
    
    with zipfile.ZipFile(os.path.join(DEFAULT_DIR + zipFilename), 'w', zipfile.ZIP_STORED) as zipf:
        for f in filesInfo:
            zipf.write(f['path'], arcname=os.path.relpath(f['path'], DEFAULT_DIR));
    
    
    #for f in filesInfo:
    #    os.remove(f['path']);
    #Todo compress to zip and return the zip filename
    return zipFilename;

while True:
    os.system("ping6 a.net9.org -c 2");
    Ts = Tasks.objects.filter(taskActive=1);
    for T in Ts:
        if T.was_outdated():
            T.taskActive = 0;
            T.taskDelFailed = 1;
            User = T.user;
            User.usedTaskNumber -= 1;
            User.usedDiskSpace -= T.taskFilesize;
            User.save();
            #print(task.taskGid);
            T.save();
            continue;
            
        if T.taskCompletedTime == None:
            Gid = T.taskGid;
            if T.taskType == 1:
                try:
                    status = con.tellStatus(gid = Gid);
                except:
                    pass
                try:
                    status = con.tellStatus(gid = Gid);
                    if T.taskStatus == 'complete' or T.taskStatus == 'error':
                        continue;
                    T.taskStatus = status['status'];
                    if int(status['totalLength']) != 0:
                        T.taskRate = int(int(status['completedLength']) * 100 / int(status['totalLength']));
                    T.taskSpeed = int(int(status['downloadSpeed']) / 1024);
                    if not T.taskFilesize:
                        T.taskFilesize = int(int(status['totalLength']) / 1048576);
                        User = T.user;
                        User.usedDiskSpace += T.taskFilesize;
                        User.save();
                    
                    if T.taskStatus == 'complete':
                        T.taskFilename = os.path.split(status['files'][0]['path'])[1];
                        T.taskCompletedTime=timezone.now();
                    T.save()
                except:
                    pass
                    
            elif T.taskType == 2:
                try:
                    status = con.tellStatus(gid = Gid);
                except:
                    pass
                try:
                    status = con.tellStatus(gid = Gid);
                    if T.taskStatus == 'complete' or T.taskStatus == 'error':
                        continue;
                    T.taskStatus = status['status'];
                    T.taskHash = status['infoHash'];
                    lastT = Tasks.objects.filter(taskActive=1).filter(taskHash=T.taskHash).exclude(id=T.id).exclude(taskGid=T.taskGid);
                    if len(lastT) != 0:
                        T.taskGid = lastT[0].taskGid;
                        T.taskStatus = 'exist';
                        T.save();
                        continue;
                    T.taskSpeed = int(int(status['downloadSpeed']) / 1024);
                    if int(status['totalLength']) != 0:
                        T.taskRate = int(int(status['completedLength']) * 100 / int(status['totalLength']));
                    
                    if not T.taskFilesize:
                        T.taskFilesize = int(int(status['totalLength']) / 1048576);
                        User = T.user;
                        User.usedDiskSpace += T.taskFilesize;
                        User.save();
                    
                    if status['totalLength'] == status['completedLength'] and T.taskStatus == 'active':
                        T.taskStatus = 'complete';
                    
                    if T.taskStatus == 'complete':
                        T.taskFilename = compress(status['files']);
                        T.taskSpeed = 0;
                        print(T.taskStatus);
                        T.taskCompletedTime = timezone.now();
                    T.save();
                except:
                    pass;
    Ts = Tasks.objects.filter(taskDelFailed__gt=0).filter(taskDelFailed__lt=5)
    for T in Ts:
        actDelete(T.id);                
    time.sleep(2);        
            
            
                
