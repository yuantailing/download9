#!/bin/sh
nohup python3 /srv/download9/Download9/mysite/manage.py runserver 127.0.0.1:8001 >> /srv/download9/Download9/mysite/log.txt 
nohup python3 /srv/download9/Download9/mysite/update.py >> /srv/download9/Download9/mysite/update_log.txt 
aria2c --conf-path /srv/download9/aria2/aria2.conf -D
