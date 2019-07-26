from datetime import datetime
from groupbuyorganizer import database, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(database.Model, UserMixin): #todo restructure
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    password = database.Column(database.String(60), nullable=False)  # todo changed to hashed_pw
    email = database.Column(database.String(120), unique=True, nullable=False)
    disabled = database.Column(database.Boolean, nullable=False, default=False)
    is_admin = database.Column(database.Boolean, nullable=False, default=False)
    is_root = database.Column(database.Boolean, nullable=False, default=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Instance(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    root_created = database.Column(database.Boolean, nullable=False, default=False)
    registration_enabled = database.Column(database.Boolean, nullable=False, default=True)
    login_required = database.Column(database.Boolean, nullable=False, default=True)


class Category(database.Model):
    ''''''
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False, unique=True)


class Event(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(120), unique=True, nullable=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    notes = database.Column(database.Text, nullable=True)
    is_locked = database.Column(database.Boolean, nullable=False, default=False)
    extra_charges = database.Column(database.Numeric(precision=2))


class Item:
    id = database.Column(database.Integer, primary_key=True)
    name = 0
    price = 0
    packing = 0
    category_id = 0


class CaseBuy:
    user_id = 0
    event_id = 0
    item_id = 0
    quantity = 0


class HasPaid:
    user_id = 0
    event_id = 0


class CaseSplit:
    id = 0
    user_id = 0
    event_id = 0
    item_id = 0
    quantity = 0

database.create_all()
database.session.commit() #temporary location