from groupbuyorganizer import database, login_manager, web_app

from datetime import datetime

class Event(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(120), unique=True, nullable=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    notes = database.Column(database.Text, nullable=True)
    is_locked = database.Column(database.Boolean, nullable=False, default=False)
    is_closed = database.Column(database.Boolean, nullable=False, default=False)
    extra_charges = database.Column(database.Numeric(precision=2), nullable=False, default=0.00)
    added_by = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    items = database.relationship('Item', backref='event', cascade='all, delete-orphan')


class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Numeric(precision=2), nullable=False)
    packing = database.Column(database.Integer, nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey('category.id'), nullable=False)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    added_by = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    case_buys = database.relationship('CaseBuy', backref='item', cascade='all, delete-orphan')


class CaseBuy(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    item_id = database.Column(database.Integer, database.ForeignKey('item.id'), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)


# haspaid = database.Table('has_paid',
#              database.Column
#                          )
#
# class HasPaid: #table
#     user_id = 0
#     event_id = 0


class CaseSplit: #table?
    id = 0
    user_id = 0
    event_id = 0
    item_id = 0
    quantity = 0
    is_complete = bool