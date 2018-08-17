#!/bin/bash

cd "$(dirname "$0")"
exec pipenv run celery -A base worker -l info --concurrency 1 --autoreload
