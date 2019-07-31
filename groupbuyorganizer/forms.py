from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, PasswordField, SubmitField, StringField, TextAreaField #todo notes
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from groupbuyorganizer.models import User


class RegistrationForm(FlaskForm):
    '''This field is used to register new accounts'''

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    '''This form is used to log into the web app.'''
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class CreateEvent(FlaskForm):
    event_name = StringField(validators=[DataRequired()])
    submit = SubmitField('Add Category')

class CreateItem(FlaskForm):
    item_name = StringField(validators=[DataRequired()])
    category = 0
    price = DecimalField()

class CreateCategory(FlaskForm):
    pass

class UserOptionsForm(FlaskForm):
    '''This field is used to register new accounts'''

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.username:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class AdminConfig(FlaskForm):
    pass

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        if email.data != current_user.username:
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError('There is no account associated with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')