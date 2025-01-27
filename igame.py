"""
ENTERS HERE
HEROKU ROUTER HTTP1.1: https://doi.org/10.17487/RFC9112
HEROKU STACK INFO: https://devcenter.heroku.com/articles/heroku-22-
WAITRESS: https://docs.pylonsproject.org/projects/waitress/en/latest/runner.html#waitress-serve
[CMD] 'waitress-serve': https://docs.pylonsproject.org/projects/waitress/en/latest/arguments.html#arguments

FLASK version 3.1.0
[INFO](https://flask.palletsprojects.com/en/stable/changes/)
"""

import os
from dotenv import load_dotenv

# generates path to .env file and loads if present
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from iGame import create_app

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

# TODO: MOVE TO PROCFILE command -> release: flask db upgrade (head?)

@app.cli.command()
def deploy():
    from flask_migrate import upgrade
    from iGame.models import db

    # migrate
    upgrade()
    # create or update
    db.create_all()
