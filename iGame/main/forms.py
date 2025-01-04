from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerRangeField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from ..models import User


class FilterForm(FlaskForm):
    submit = SubmitField('search')
    pass

class RatingForm(FlaskForm):
    gameRating = IntegerRangeField('Rating Number', validators=[DataRequired()])
    submit = SubmitField('RATE')


class LoginForm(FlaskForm):
    email = StringField('SET EMAIL', validators=[DataRequired(message="Choose a login method.")])
    remember = BooleanField('SET LOGIN DURATION: 1 year')
    submit = SubmitField('submit request')


class GameForm(FlaskForm):
    game1 = StringField('Game 1', validators=[DataRequired(message='Enter a game to search')])
    game2 = StringField('Game 2', validators=[DataRequired(message='Enter a game to search')])
    game3 = StringField('Game 3', validators=[DataRequired(message='Enter a game to search')])
    game4 = StringField('Game 4', validators=[DataRequired(message='Enter a game to search')])
    game5 = StringField('Game 5', validators=[DataRequired(message='Enter a game to search')])
    submit = SubmitField('Find my Games')


class GameSelections(FlaskForm):
    game1sel = SelectField('Select Game 1', choices=[])
    game2sel = SelectField('Select Game 2', choices=[])
    game3sel = SelectField('Select Game 3', choices=[])
    game4sel = SelectField('Select Game 4', choices=[])
    game5sel = SelectField('Select Game 5', choices=[])
    submit = SubmitField('Confirm Selections')


# class RegistrationForm(FlaskForm):
#     username = StringField('A Username',
#                            validators=[DataRequired(message="iGames requires a username for user identification."),
#                                        Length(3, 50, message="Enter a username with 3 <= length <= 50"), Regexp('\w',
#                                                                                                                 message="Username must contain only Latin letters and whole numbers.")])
#     password = PasswordField('A Password', validators=[
#         InputRequired(message="Enter a desired password in this field and the next field."),
#         Regexp('[^<>*]', message="Use letters, numbers and punctuation marks."),
#         EqualTo('password_confirm', message='Passwords must match.')])
#     password_confirm = PasswordField('Confirm Password',
#                                      validators=[InputRequired(message="Re-enter desired password."),
#                                                  EqualTo('password', message='Passwords do not match.')])
#     email = StringField('Email Address', validators=[DataRequired(message="iGames registration requires email input."),
#                                                      Regexp('[^<>*]',
#                                                             message="Re-type email like: name@domain.whatever"),
#                                                      Email(message="Invalid email input.")])
#     submit = SubmitField('Register Me!')

    def validate_username(self, user):
        if User.query.filter(User.user_name == user.data).first():
            raise ValidationError('Username is taken.')
