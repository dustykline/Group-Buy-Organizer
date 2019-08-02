from datetime import datetime
from groupbuyorganizer import database, login_manager, web_app #todo change to from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer



# Creating an "Instance" model if there is none.
if Instance.query.get(1) is None:
    database.session.add(Instance())
    database.session.commit()