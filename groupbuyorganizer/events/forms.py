from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from groupbuyorganizer.events.models import Event

class CreateEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_event_name(self, event_name):
        event = Event.query.filter_by(name=event_name.data).first()
        if event:
            raise ValidationError('That event name is taken. Please choose a different one.')

class CreateItemForm(FlaskForm):
    item_name = StringField('Item name', validators=[DataRequired()])
    price = DecimalField('Price of item', validators=[DataRequired()])
    packing = IntegerField('Case packing for item', validators=[DataRequired()])
    category = SelectField('Select item category')

    # def add_item(self):
    #     form = CreateItemForm()
    #     form.category.choices = [(category.name) for category in Category.query.order_by(Category.name.asc()).all()]
    #     #todo add None option here or on html?