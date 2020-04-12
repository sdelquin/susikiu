#!/bin/bash

source ~/.virtualenvs/susikiu/bin/activate
cd $(dirname $0)
exec gunicorn -c gunicorn.conf.py base.wsgi:application
