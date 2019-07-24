from flask import Flask, flash, redirect, render_template, url_for

from gbo.forms import LoginForm, RegistrationForm

web_app = Flask(__name__)
web_app.config['SECRET_KEY'] = 'temporary' #todo secrets.token_hex(16)... have in config.py file?

@web_app.route("/")
def home():
    return render_template('home.html')

@web_app.route("/about")
def about():
    return render_template('about.html')

@web_app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@web_app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

#todo more

web_app.run(debug=True)