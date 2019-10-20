#!/bin/bash
# Script to launch RQ (Redis Queue) service

cd $(dirname $0)
exec pipenv run rq worker
