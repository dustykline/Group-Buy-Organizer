from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from groupbuyorganizer.config import Configuration

web_app = Flask(__name__)
web_app.config.from_object(Configuration)

database = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'general.login'
login_manager.login_message_category = 'info'
mail = Mail()

from groupbuyorganizer import routes #del
from groupbuyorganizer.models import Instance #del?

def create_app(config_class=Configuration):
    web_app = Flask(__name__)
    web_app.config.from_object(Configuration)

    database.init_app(web_app)
    bcrypt.init_app(web_app)
    login_manager.init_app(web_app)
    mail.init_app(web_app)

    from groupbuyorganizer.admin.routes import admin  # todo do with other routes +2

    web_app.register_blueprint(general)
    web_app.register_blueprint(events)
    web_app.register_blueprint(admin)  # todo rinse and repeat +2

    database.create_all()
    database.session.commit()

    if Instance.query.get(1) is None:
        database.session.add(Instance())
        database.session.commit()

    return web_app