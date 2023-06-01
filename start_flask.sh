#!/bin/sh

pip install -r requirements.txt

export FLASK_APP=app
export FLASK_DEBUG=false
export FLASK_ENV=production
export SERVER_NAME='pendule1.lab:5000'

flask run --host=0.0.0.0
