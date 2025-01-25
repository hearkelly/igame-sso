"""
ENTERS HERE
HEROKU STACK INFO: https://devcenter.heroku.com/articles/heroku-22-

FLASK version 3.1.0
[INFO](https://flask.palletsprojects.com/en/stable/changes/)
"""

import os
from dotenv import load_dotenv
from flask import request, redirect
# generates path to .env file and loads if present
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from iGame import create_app

# beloved app object, context?
# with factory pattern, app has no explicit context
app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

@app.before_request
def force_https():
    print("enforcing")
    if not request.is_secure and not app.debug:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)

# @app.before_request
# def log_request_info():
#     print(f"Request headers: {request.headers}")
#     print(f"Request scheme: {request.scheme}")
#     print(f"Full URL: {request.url}")

#
# TODO: MOVE TO PROCFILE command -> release: flask db upgrade (head?)
#  also need to re-configure models, db

@app.cli.command()
def deploy():
    from flask_migrate import upgrade
    from iGame.models import db

    # migrate
    upgrade()
    # create or update
    db.create_all()
