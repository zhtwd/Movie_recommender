#!/bin/bash
pip install -r requirements.txt
gunicorn -w4 -b0.0.0.0:8000 server:app &
mkdir -p logs
echo 'server started: 0.0.0.0:8000'
