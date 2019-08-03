from groupbuyorganizer import database, login_manager, web_app
#todo change to from flask import current_app

# class Event(database.Model):
#     id = database.Column(database.Integer, primary_key=True)
#     name = database.Column(database.String(120), unique=True, nullable=False)
#     date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
#     notes = database.Column(database.Text, nullable=True)
#     is_locked = database.Column(database.Boolean, nullable=False, default=False)
#     extra_charges = database.Column(database.Numeric(precision=2), nullable=False) #todo events model


# class Item:
#     id = database.Column(database.Integer, primary_key=True)
#     name = database.Column(database.Integer, nullable=False)
#     price = database.Column(database.Integer, nullable=False) todo events model
#     packing = database.Column(database.Integer, nullable=False)
#     category_id = database.ForeignKey()
#
#
# class CaseBuy:
#     user_id = 0 #fk
#     event_id = 0 #fk todo events model
#     item_id = 0 #fk
#     quantity = 0
#
#
# class HasPaid: #table
#     user_id = 0
#     event_id = 0 todo events model
#
#
# class CaseSplit: #table?
#     id = 0
#     user_id = 0
#     event_id = 0
#     item_id = 0 todo events model
#     quantity = 0
#     is_complete = bool