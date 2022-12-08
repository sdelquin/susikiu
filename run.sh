#!/bin/bash

source ~/.pyenv/versions/susikiu/bin/activate
cd $(dirname $0)
exec gunicorn -c gunicorn.conf.py base.wsgi:application
