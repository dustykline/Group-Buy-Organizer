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
    items = database.relationship('Item', backref='event', cascade='all, delete-orphan', lazy='dynamic')
    # case_buys = database.relationship('CaseBuy', backref='event', lazy='dynamic')


class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Numeric(precision=2), nullable=False)
    packing = database.Column(database.Integer, nullable=False)
    category_id = database.Column(database.Integer, database.ForeignKey('category.id'), nullable=False)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    added_by = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    case_buys = database.relationship('CaseBuy', backref='item', cascade='all, delete-orphan', lazy='dynamic')
    case_splits = database.relationship('CaseSplit', backref='item', cascade='all, delete-orphan', lazy='dynamic')


class CaseBuy(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    item_id = database.Column(database.Integer, database.ForeignKey('item.id'), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)


class CaseSplit(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    started_by = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    item_id = database.Column(database.Integer, database.ForeignKey('item.id'), nullable=False)
    is_complete = database.Column(database.Boolean, nullable=False, default=False)
    commits = database.relationship('CasePieceCommit', backref='case_split', cascade='all, delete-orphan')


class CasePieceCommit(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    committed_on = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
    case_split_id = database.Column(database.Integer, database.ForeignKey('case_split.id'), nullable=False)
    user_id = database.Column(database.Integer, database.ForeignKey('item.id'), nullable=False)
    pieces_committed = database.Column(database.Integer, nullable=False)


# class HasPaid(database.Model):
#     user_id = database.Column(database.Integer, database.ForeignKey('item.id'), nullable=False)
#     event_id = database.Column(database.Integer, database.ForeignKey('event.id'), nullable=False)
#     has_paid = database.Column(database.Boolean, nullable=False, default=False)