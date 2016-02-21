from django.db import models
from django.utils import timezone
import datetime
'''
用户一张表，包括用户ID，用户名，总空间配额，总任务数配额，已使用空间，已使用任务数，用户任务最多存在时间。

下载任务一张表，包括任务ID，任务类型, 下载地址, 任务添加时间，文件大小，文件存储路径，文件hash值，目前下载进度，完成下载时间，ForeignKey是用户ID
'''
# Create your models here.

class Users(models.Model):
    username = models.CharField(max_length=200);
    password = models.CharField(max_length=200);
    keepaliveHash = models.CharField(max_length=200, null = True);
    diskSpaceLimit = models.IntegerField(default=20480);
    taskNumberLimit = models.IntegerField(default=10);
    usedDiskSpace = models.IntegerField(default=0);
    usedTaskNumber = models.IntegerField(default=0);
    savetimeLimit = models.IntegerField(default=72);
    def __str__(self):
        return self.username

class Tasks(models.Model):
    taskName = models.CharField(max_length=200);
    taskActive = models.IntegerField(default=0);#有效 = 1, 无效 = 0;
    taskType = models.IntegerField();#HTTP = 1, torrent = 2, magnet = 3;
    taskUrl = models.CharField(max_length = 10240, null = True);
    taskStartTime = models.DateTimeField(null = True);
    taskFilesize = models.IntegerField(default=0);
    taskFilename = models.CharField(max_length = 200, null = True);
    taskHash = models.CharField(max_length = 200, null = True);
    taskRate = models.IntegerField(default=0);
    taskSpeed = models.IntegerField(default=0);
    taskCompletedTime = models.DateTimeField(null = True);
    taskGid = models.CharField(max_length = 200, null = True);
    taskStatus = models.CharField(max_length = 200, default=b'');
    user = models.ForeignKey(Users);
    def __str__(self):
        return self.taskName;
    def was_completed(self):
        return self.taskCompletedTime != None;
    def was_outdated(self):
        return self.taskStartTime < timezone.now() - datetime.timedelta(hours = self.user.savetimeLimit);
