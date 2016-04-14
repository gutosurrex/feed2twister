#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/flask_app")

from app import app as application
application.secret_key = 'gj8293as0gj832plck3uh2h378s88suduhb2bb1vvsg'
