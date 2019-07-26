from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temporary' #todo secrets.token_hex(16)... have in config.py file?
web_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
database = SQLAlchemy(web_app)
bcrypt = Bcrypt(web_app)
login_manager = LoginManager(web_app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from groupbuyorganizer import routes