#!/bin/sh
exec python3 /srv/download9/Download9/mysite/manage.py runserver 127.0.0.1:8001 >> /srv/download9/Download9/mysite/log.txt 
