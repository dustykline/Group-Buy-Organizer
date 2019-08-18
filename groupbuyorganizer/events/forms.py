from flask import request
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, ValidationError

from groupbuyorganizer.events.models import Event, Item

class CreateEventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_event_name(self, event_name):
        event = Event.query.filter_by(name=event_name.data).first()
        if event:
            raise ValidationError('That event name is taken. Please choose a different one.')


class EventNotesForm(FlaskForm):
    event_notes = TextAreaField('Event Notes')
    submit = SubmitField('Submit')


class EventExtraChargeForm(FlaskForm):
    extra_charges = DecimalField('Extra Charges', validators=[DataRequired()])
    submit = SubmitField('Update')


class CreateItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    price = DecimalField('Price of Item ($)', validators=[DataRequired()])
    packing = IntegerField('Case packing For Item', validators=[DataRequired()])
    category_id = SelectField('Select Item Category', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Submit')

    def validate_item_name(self, item_name):
        item = Item.query.filter_by(name=item_name.data).first()
        if item:
            raise ValidationError('That item name is taken. Please choose a different one.')


class EditItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    price = DecimalField('Price of Item ($)', validators=[DataRequired()])
    packing = IntegerField('Case packing For Item', validators=[DataRequired()])
    category_id = SelectField('Select Item Category', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Submit')


class CaseQuantityOrderForm(FlaskForm):
    choicesList = []
    for i in range(100):
        choicesList.append((i, i))
    quantity = SelectField('Cases To Order', coerce=int, choices=choicesList)
    submit = SubmitField('Update')


class CaseSplitForm(FlaskForm):
    piece_quantity = SelectField('Case Pieces Requested', coerce=int)
    submit = SubmitField('Submit')


class RemoveUserFromEventForm(FlaskForm):
    pass