from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired

class CreateEvent(FlaskForm):
    event_name = StringField(validators=[DataRequired()])
    submit = SubmitField('Add Category')

class CreateItem(FlaskForm):
    item_name = StringField(validators=[DataRequired()])
    category = 0
    price = DecimalField()