#!/bin/bash

python manage.py migrate
# gunicorn --config gunicorn-cfg.py core.asgi -k uvicorn.workers.UvicornWorker
uvicorn core.asgi:application --host 0.0.0.0 --port 5005 --workers 2 --lifespan off