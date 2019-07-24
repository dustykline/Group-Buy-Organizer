from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from groupbuyorganizer.models import User


class RegistrationForm(FlaskForm):
    '''This field is used to register new accounts'''

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    '''This form is used to log into the web app.'''
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class CreateEvent(FlaskForm):
    pass

class CreateItem(FlaskForm):
    pass

class CreateCategory(FlaskForm):
    pass

class UserOptions(FlaskForm):
    pass

class AdminConfig(FlaskForm):
    pass