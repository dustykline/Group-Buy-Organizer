from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temporary'
web_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

database = SQLAlchemy(web_app)
bcrypt = Bcrypt(web_app)
login_manager = LoginManager(web_app)
login_manager.login_view = 'general.login'
login_manager.login_message_category = 'general.info'

from groupbuyorganizer.admin.models import Category, Instance
import groupbuyorganizer.events.models

from groupbuyorganizer.general.routes import general
from groupbuyorganizer.events.routes import events
from groupbuyorganizer.admin.routes import admin
from groupbuyorganizer.errors.handlers import errors
web_app.register_blueprint(general)
web_app.register_blueprint(events)
web_app.register_blueprint(admin)
web_app.register_blueprint(errors)

database.create_all()
database.session.commit()

# Creating an "Instance" model if there is none.
if Instance.query.get(1) is None:
    database.session.add(Instance(wkhtmltopdf_path="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"))
    database.session.add(Category(name='Uncategorized'))
    database.session.commit()