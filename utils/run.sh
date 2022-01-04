#!/bin/bash
set -e
: ${PORT:=80}

python ./manage.py migrate --noinput
gunicorn macaroonBackend.wsgi:application --bind 0.0.0.0:"$PORT"
