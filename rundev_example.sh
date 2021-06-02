#!/usr/bin/env bash

export FLASK_APP=app.py
export FLASK_ENV=development
export DB_HOST = 'Add connection String here'
export SECRET_KEY = 'Add secret key here'

flask run --host=0.0.0.0