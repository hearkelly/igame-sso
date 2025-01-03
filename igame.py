"""
HEROKU-22 DYNO RUNS *THIS* FILE
STACK INFO: https://devcenter.heroku.com/articles/heroku-22-stack
"""

import os
# from dotenv import load_dotenv

# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)

from iGame import create_app

print(os.environ.get('FLASK_CONFIG') )
app = create_app(os.environ.get('FLASK_CONFIG') or 'default')

"""
MOVE TO PROCFILE command -> release: flask db upgrade (head?)
also need to re-configure models, db 
"""
# @app.cli.command()
# def deploy():
#     from flask_migrate import upgrade
#     from iGame.models import db
#
#     # migrate database to latest revision
#     upgrade()
#
#     # create or update
#     db.create_all()
