#!/bin/bash
export FLASK_APP=FlaskMain.py
flask run --reload --debugger --host 0.0.0.0 --port 443 &

python broker.py 