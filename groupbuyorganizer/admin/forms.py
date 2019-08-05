from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, ValidationError

from groupbuyorganizer.admin.models import Category

class CreateCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_category_name(self, category_name):
        category = Category.query.filter_by(name=category_name.data).first()
        if category:
            raise ValidationError('That category name is already being used. Please choose a different one.')


class ApplicationSettingsForm(FlaskForm):
    registration_enabled = BooleanField("Registration Enabled?")
    submit = SubmitField('Submit')