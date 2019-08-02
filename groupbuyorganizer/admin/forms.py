from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField

class CreateCategory(FlaskForm):
    pass


class ApplicationSettingsForm(FlaskForm):
    registration_enabled = BooleanField("Registration Enabled?")
    submit = SubmitField('Submit')