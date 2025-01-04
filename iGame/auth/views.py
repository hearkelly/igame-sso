from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db,User
from ..main.forms import LoginForm
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
        'scope': 'https://www.googleapis.com/auth/userinfo.email'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@auth.route('/login')
def login():
    """
    view for user sso choices
    """
    # form = LoginForm()
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
    redirect_uri = url_for('auth._auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth.route('/auth', methods=['GET','POST'])
def _auth():
    """
    create and set user object
    after auth token returned from google
    and checked in db
    """
    # token = oauth.google.authorize_access_token()
    # print(token)
    # get user email
    form = LoginForm()
    # hash input
    # compare to stored hash in db for username/email

    email_hash = form.email.data
    if form.validate_on_submit():
        try:
            user = db.session.query(User).filter(User.user_name == email_hash).first()
        except Exception as e:  # to collect db errors
            print(e)
            user = None
        if user:
            login_user(user,remember = form.remember.data)
        return redirect(url_for('main.home'))
    return render_template('login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect((url_for('main.index')))




# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     # if current_user.is_authenticated:
#     #     flash('Seems like you are registered and logged in. Log out to register a new account.')
#     #     return redirect(url_for('main.home'))
#     #
#     # try:
#     #     new = User(username, password, email)
#     # except Exception as err:
#     #     flash(message=f"Object Creation Error: {err}",category='error')  # log as error
#     #     return render_template('404.html'), 404
#     # try:
#     #     db.session.add(new)
#     #     db.session.commit()
#     #     flash("Registered!")
#     #     return redirect(url_for('main.index'))
#     # except Exception as e:
#     #     print(e)  # log as error
#     #     flash("Registration failed. Please try again.")
#     # return render_template('register.html', title="iGame - Registration")
#     return redirect(url_for('main.home'))
