#!/bin/bash
# Script to launch RQ (Redis Queue) service

exec pipenv run rq worker
