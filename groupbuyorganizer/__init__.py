from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temporary' #todo secrets.token_hex(16)... have in config.py file?
web_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
database = SQLAlchemy(web_app)
bcrypt = Bcrypt(web_app)

from groupbuyorganizer import routes