#!/bin/bash
# Script to launch RQ (Redis Queue) service

cd "$(dirname "$0")"
REDIS_PORT=$(grep REDIS_PORT .env | sed 's/.*= *//')
exec pipenv run rq worker --url redis://localhost:$REDIS_PORT
