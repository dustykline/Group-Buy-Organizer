from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

from groupbuyorganizer.admin.models import Category

class CreateEventForm(FlaskForm):
    event_name = StringField(validators=[DataRequired()])
    submit = SubmitField('Add Category')

class CreateItemForm(FlaskForm):
    item_name = StringField('Item name', validators=[DataRequired()])
    price = DecimalField('Price of item', validators=[DataRequired()])
    packing = IntegerField('Case packing for item', validators=[DataRequired()])
    category = SelectField('Select item category')

    def add_item(self):
        form = CreateItemForm()
        form.category.choices = [(category.name) for category in Category.query.order_by(Category.name.asc()).all()]
        #todo add None option here or on html?