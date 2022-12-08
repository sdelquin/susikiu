#!/bin/bash
# Script to launch RQ (Redis Queue) service

source ~/.pyenv/versions/susikiu/bin/activate
cd $(dirname $0)
exec rq worker
