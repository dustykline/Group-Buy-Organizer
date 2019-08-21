from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from groupbuyorganizer import database, bcrypt
from groupbuyorganizer.admin.models import Instance, User
from groupbuyorganizer.admin.utilities import HomeEvent
from groupbuyorganizer.events.forms import CreateEventForm
from groupbuyorganizer.events.models import Event
from groupbuyorganizer.general.forms import LoginForm, RegistrationForm, UserOptionsForm

general = Blueprint('general', __name__)

@general.route("/events/")
@general.route("/", methods=['GET', 'POST'])
def home():
    form = CreateEventForm()
    instance = Instance.query.first()
    events = Event.query.order_by(Event.date_created.desc()).all()

    home_event_list = []
    for event in events:
        home_event_list.append(HomeEvent(event))

    if form.validate_on_submit():
        event = Event(name=form.event_name.data, added_by=current_user.id)
        database.session.add(event)
        database.session.commit()
        flash('Event created!', 'success')
        return redirect(url_for('general.home'))
    return render_template('home.html', root_created = instance.root_created, home_event_list=home_event_list,
                           registration_enabled = instance.registration_enabled, events=events, form=form, c=5)


@general.route("/about/")
def about():
    return render_template('about.html', title='About')


@general.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('general.home'))
    instance = Instance.query.first()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        instance = Instance.query.first()
        if instance.root_created == False:
            user.is_root = True
            user.is_admin = True
            instance.root_created = True
            flash('Your account has been created!', 'success')
        else:
            flash(f'Your account has been created, you can now log in', 'success')

        database.session.add(user)
        database.session.commit()
        return redirect(url_for('general.login'))
    return render_template('register.html', title='Join Today', form=form,
                           registration_enabled=instance.registration_enabled)


@general.route("/login/", methods=['GET', 'POST'])
def login():
    instance = Instance.query.first()
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.disabled:
                flash('This account has been disabled.', 'danger')
                return redirect(url_for('general.home'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('general.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Log In', form=form, registration_enabled=instance.registration_enabled)


@general.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('general.home'))


@general.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = UserOptionsForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        database.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('general.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title=f'{current_user.username} Account Settings', form=form)


@general.route("/help/")
def help():
    return render_template('help.html', title='Help')