#!/usr/bin/env bash

export FLASK_APP=app.py
export FLASK_ENV=development
export db_host = 'Add connection String here'
export secret_key = 'Add secret key here'

flask run --host=0.0.0.0