from flask import abort,flash, redirect, render_template, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import OperationalError,TimeoutError,DBAPIError
from ..models import db,User
from ..main.forms import LoginForm
from iGame import oauth, serializer
import os
from . import auth
import requests
import json
from utilities import hash_email,get_jwt_claims,get_email_from_claims, validate_email


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
        'scope': 'https://www.googleapis.com/auth/userinfo.email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@auth.route('/login', methods=['GET','POST'])
def login():
    """
    form view for user-sso options and redirects
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # if form.validate_on_submit():
    #     user = db.session.query(User) \
    #         .filter(User.user_name == form.username.data) \
    #         .first()
    #     if user is not None and user.verify_password(form.password.data):
    #         """
    #         the user query returns a Python object of the .first() user
    #         it finds in db
    #         """
    #         login_user(user, form.remember.data)
    #         session['bag'] = [g.to_dict() for g in db.session.query(Game).filter(and_(Game.user_id == current_user.id),
    #                                                                              Game.likes == True).all()]
    #
    #         session['unbag'] = [g.to_dict() for g in
    #                             db.session.query(Game).filter(and_(Game.user_id == current_user.id),
    #                                                           Game.likes == False).all()]
    #
    #     flash('Invalid username or password.')\
    """
    form with google / github options, plus REMEMBER ME
    once form is submitted:
    update set_remember cookie
    generate the redirect uri, and return oauth for selected sso
    if not submitted:
    render_template(login)
    """
    form=LoginForm()

    if form.validate_on_submit():
        session['set_remember']: bool= form.remember.data or False
        redirect_uri = url_for('auth._auth', _external=True)
        if form.github.data:
            return redirect(redirect_uri)  # TODO: configure github sso
        else:
            return oauth.google.authorize_redirect(redirect_uri)

    return render_template('login.html',form=form)

@auth.route('/auth', methods=['GET','POST'])
def _auth():
    """
    create and set user object
    after auth token returned from google
    and checked in db
    """
    token = oauth.google.authorize_access_token()
    claims = get_jwt_claims(os.environ.get('GOOGLE_ID'),token['id_token'])
    email = get_email_from_claims(claims)    # return string or None otherwise

    if email and validate_email(email):
        email_hash = hash_email(email)
    else:
        email_hash,email = None,None

    if email_hash:
        try:
            user = db.session.query(User).filter(User.email_hash == email_hash).first()
            login_user(user, remember=session.get('set_remember') or False)
            return redirect(url_for('main.home'))
        except (OperationalError, TimeoutError, DBAPIError) as e:
            flash(f"{e}",category='connection error')
            return render_template('404.html')
            # TODO: create route/views/error handlers for 404,500
        except Exception as e:
            print(e)
            flash('Email verified but not registered with us.')
            session['email'] = email_hash
            return redirect(url_for('auth.register'))
    flash('Submitted email address is unverified and/or invalid.')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect((url_for('main.index')))
# TODO: work on main.index splash



@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Seems like you are registered and logged in. Log out to register a new account.')
        return redirect(url_for('main.home'))

    email = session['email']
    if email:
        try:
            new = User(email)
        except Exception as err:
            flash(message=f"Object Creation Error: {err}",category='error')  # log as error
            return render_template('404.html'), 404
        try:
            db.session.add(new)
            db.session.commit()
            login_user(new, remember=session.get('set_remember') or False)
            return redirect(url_for('main.home'))
        except Exception as e:
            print(e)  # log as error
            flash("Registration failed. Please try again.")
            abort(500)
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))
