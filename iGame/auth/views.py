from flask import abort, flash, redirect, render_template, session, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import OperationalError, TimeoutError, DBAPIError
from sqlalchemy import and_, func
from ..models import User, Game, db
from ..main.forms import LoginForm
from iGame import oauth
import os
from . import auth
import requests
from utilities import hash_email, get_jwt_claims, get_email_from_claims, validate_email

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


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    form view for user-sso options and redirects
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    """
    form with google / github options, plus REMEMBER ME
    once form is submitted:
    update set_remember cookie
    generate the redirect uri, and return oauth for selected sso
    if not submitted:
    render_template(login)
    """
    form = LoginForm()

    if form.validate_on_submit():
        session['set_remember']: bool = form.remember.data or False
        redirect_uri = url_for('auth._auth', _external=True)
        if form.github.data:
            return redirect(redirect_uri)  # TODO: configure github sso
        elif form.google.data:
            return oauth.google.authorize_redirect(redirect_uri)
    return render_template('index.html', form=form)


@auth.route('/auth', methods=['GET', 'POST'])
def _auth():
    """
    create and set user object
    after auth token returned from google
    and checked in db
    """
    token = oauth.google.authorize_access_token()
    claims = get_jwt_claims(os.environ.get('GOOGLE_ID'), token['id_token'])
    email = get_email_from_claims(claims)  # return string or None otherwise

    if email and validate_email(email):
        email_hash = hash_email(email)
    else:
        email_hash, email = None, None

    if email_hash:
        try:
            user = db.session.query(User).filter(User.email_hash == email_hash).first()
            login_user(user, remember=session.get('set_remember') or False)
            return redirect(url_for('main.home'))
        except (OperationalError, TimeoutError, DBAPIError) as e:
            flash(f"{e}", category='connection error')
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
            flash(message=f"Object Creation Error: {err}", category='error')  # log as error
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


@auth.route('/_games/<_id>')
def get_users(_id=0):
    # rq = db.session.query(Game.game_id, Game.rating).filter(
    #     and_(Game.user_id == _id, Game.likes == True)).all()
    rq_scalars = db.session.execute(db.select(Game.game_id).where(Game.user_id == _id)).scalars()
    print(list(rq_scalars))
    # bag_count = db.session.query(func.count(Game)).filter(
    #     and_(Game.user_id == _id, Game.likes == True)).scalar()
    # rq_scalars = db.session.query(Game.game_id, Game.rating).filter(
    #     and_(Game.user_id == _id, Game.likes == True)).scalars()
    return render_template('t_.html', data=rq_scalars)
