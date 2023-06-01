#!/bin/sh

pip install -r requirements.txt

export FLASK_APP=app
export FLASK_DEBUG=false
export FLASK_ENV=production

flask run --host=0.0.0.0
