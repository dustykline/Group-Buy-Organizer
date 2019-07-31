from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temporary' #todo secrets.token_hex(16)... have in config.py file?
web_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
database = SQLAlchemy(web_app)
bcrypt = Bcrypt(web_app)
login_manager = LoginManager(web_app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
web_app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
web_app.config['MAIL_PORT'] = 587
web_app.config['MAIL_USE_TLS'] = True
web_app.config['MAIL_USERNAME'] = None #os.environ.get('EMAIL_USER') #todo merge into model
web_app.config['MAIL_PASSWORD'] = None # ^same
mail = Mail(web_app)

from groupbuyorganizer import routes
from groupbuyorganizer.models import Instance