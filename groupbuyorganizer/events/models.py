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

    # items = database.relationship('Item', backref='event', lazy='') #todo next


class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Numeric(precision=2), nullable=False)
    packing = database.Column(database.Integer, nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey('category.id'), nullable=False)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    added_by = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)


# class CaseBuy(database.Model):
#
#     user_id = database.ForeignKey('user.id', primary_key=True)
#     event_id = database.ForeignKey('event.id')
#     item_id = database.ForeignKey('item.id')
#     quantity = database.Column(database.Integer, nullable=False)


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