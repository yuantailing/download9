import os,sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from offDown.models import *
from pyaria2 import *
import time
import mysite.settings

con = PyAria2();

while True:
    Ts = Tasks.objects.filter(taskActive=1);
    for T in Ts:
        if T.was_outdated():
            T.taskActive = 0;
            continue;
            #Todo delete file
        if T.taskCompletsedTime == None:
            Gid = T.taskGid;
            try:
                status = con.tellStatus(gid = Gid);
            except:
                pass
            try:
                status = con.tellStatus(gid = Gid);
                T.taskRate = int(int(status['completedLength']) * 100 / int(status['totalLength']));
                T.taskSpeed = int(int(status['downloadSpeed']) / 1024);
                if not T.taskFilesize:
                    T.taskFilesize = int(int(status['totalLength']) / 1048576);
                if status['status'] == 'complete':
                    T.taskCompletedTime=timezone.now();
                T.save()
            except:
                pass
    time.sleep(5);        
            
            
                
