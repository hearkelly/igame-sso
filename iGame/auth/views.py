from flask import flash, redirect, render_template, url_for
from flask_login import current_user
from ..models import db,User
from iGame import oauth
import os
from . import auth

"""

"""
google = oauth.register(
    # building our flask client
    name='google',
    client_id=os.environ.get('GOOGLE_ID'),
    client_secret=os.environ.get('GOOGLE_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/user.birthday.read'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@auth.route('/login')
def login():
    """
    view for user sso choices
    """
    redirect_uri = url_for('auth.auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    print(token)
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     flash('Seems like you are registered and logged in. Log out to register a new account.')
    #     return redirect(url_for('main.home'))
    #
    # try:
    #     new = User(username, password, email)
    # except Exception as err:
    #     flash(message=f"Object Creation Error: {err}",category='error')  # log as error
    #     return render_template('404.html'), 404
    # try:
    #     db.session.add(new)
    #     db.session.commit()
    #     flash("Registered!")
    #     return redirect(url_for('main.index'))
    # except Exception as e:
    #     print(e)  # log as error
    #     flash("Registration failed. Please try again.")
    # return render_template('register.html', title="iGame - Registration")
    pass
