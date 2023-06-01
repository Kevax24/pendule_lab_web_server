#!/bin/sh

pip install -r requirements.txt

export FLASK_APP=app
export FLASK_DEBUG=false
export FLASK_ENV=production
export FLASK_RUN_PORT=8000
export FLASK_RUN_HOST=0.0.0.0

flask run
