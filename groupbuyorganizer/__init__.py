# MIT License
#
# Copyright (c) 2019 - ∞ Mark Michon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Project page:
# https://github.com/MarkMichon1/Group-Buy-Organizer

# Contact:
# markmichon7@gmail.com

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

import binascii
import os


web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temp'#todo remove upon completion binascii.b2a_hex(os.urandom(32))
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