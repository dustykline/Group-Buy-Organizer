from gbo.webapp.forms import LoginForm, RegistrationForm

from flask import Flask, render_template

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'asd' #todo secrets.token_hex(16)... have in config.py file?

@web_app.route("/")
def home():
    return None

@web_app.route("/register")
def register():
    form = RegistrationForm() #todo add if here, whether to send validated one or not... hmm
    return render_template('register.html', title='Register', form=form)

@web_app.route("/login")
def login():
    form = RegistrationForm()
    return render_template('login.html', title='Login', form=form)

#todo more

web_app.run(debug=True)

