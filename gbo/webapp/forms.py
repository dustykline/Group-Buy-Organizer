from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# login, register, item creation

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