from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer

from datetime import datetime

from groupbuyorganizer import database, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(database.Model, UserMixin):

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    password = database.Column(database.String(60), nullable=False)
    email = database.Column(database.String(120), unique=True, nullable=False)
    disabled = database.Column(database.Boolean, nullable=False, default=False)
    is_admin = database.Column(database.Boolean, nullable=False, default=False)
    is_root = database.Column(database.Boolean, nullable=False, default=False)
    date_created = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    def get_reset_token(self, expires_seconds=3600):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_seconds)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        serializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Instance(database.Model):

    id = database.Column(database.Integer, primary_key=True)
    root_created = database.Column(database.Boolean, nullable=False, default=False)
    registration_enabled = database.Column(database.Boolean, nullable=False, default=True)


class Category(database.Model):
    ''''''

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=False, unique=True)
    items = database.relationship('Item', backref='category', lazy=True)