from flask import abort,flash, redirect, render_template, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
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
    print("got to auth")
    token = oauth.google.authorize_access_token()
    claims = get_jwt_claims(os.environ.get('GOOGLE_ID'),token)
    email = get_email_from_claims(claims)    # return string or None otherwise
    print(email)
    if email and validate_email(email):
        hashed = hash_email(email)
    else:
        hashed,email = None,None

    if hashed:
        try:
            user = db.session.query(User).filter(User.user_email == email).first()
        except Exception as e:  # to collect db errors
            user = None
        if user is None:  # valid sso but not in db, so add and login
            session['email'] = serializer.dumps(email)
            return redirect(url_for('auth.register'))
        login_user(user,remember=session.get('set_remember') or False)
        return redirect(url_for('main.home'))
    flash('Email invalid')
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

    try:
        email = serializer.loads(session.get('email'))
    except:
        flash('could not load verified email. verify through sso')
        email = None
        return redirect(url_for('auth.login'))
    if email:
        try:
            new = User(email)
        except Exception as err:
            flash(message=f"Object Creation Error: {err}",category='error')  # log as error
            return render_template('404.html'), 404
        try:
            db.session.add(new)
            db.session.commit()
        except Exception as e:
            print(e)  # log as error
            flash("Registration failed. Please try again.")
            abort(500)
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))
