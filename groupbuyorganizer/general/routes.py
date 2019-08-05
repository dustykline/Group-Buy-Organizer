from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from groupbuyorganizer import database, bcrypt, mail
from groupbuyorganizer.admin.models import Instance, User
from groupbuyorganizer.events.forms import CreateEventForm
from groupbuyorganizer.events.models import Event
from groupbuyorganizer.general.forms import LoginForm, RegistrationForm, RequestResetForm, \
    ResetPasswordForm, UserOptionsForm

general = Blueprint('general', __name__)

@general.route("/events/")
@general.route("/", methods=['GET', 'POST'])
def home():
    form = CreateEventForm()
    instance = Instance.query.first()
    events = Event.query.order_by(Event.name.asc()).all()
    if form.validate_on_submit():
        event = Event(name=form.event_name.data)
        database.session.add(event)
        database.session.commit()
        flash('Event created!', 'success')
        return redirect(url_for('general.home'))
    return render_template('home.html', root_created = instance.root_created,
                           registration_enabled = instance.registration_enabled, events=events, form=form)


@general.route("/about/")
def about():
    return render_template('about.html', title='About')


@general.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
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
    return render_template('register.html', title='Register', form=form)


@general.route("/login/", methods=['GET', 'POST'])
def login():
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
    return render_template('login.html', title='Login', form=form)


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
    return render_template('account.html', title='Account Settings', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Group Buy Organizer - Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    # todo configure sender
    msg.body = f'''To reset your password, please visit the following link:
    {url_for('general.reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send()


@general.route("/reset_password/", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('general.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@general.route("/reset_password/<token>/", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('general.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return redirect(url_for('general.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        database.session.commit()
        flash(f'Your password has been updated, you can now log in!', 'success')
        return redirect(url_for('general.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@general.route("/userhelp/")
def userhelp():
    return render_template('userhelp.html', title='User Help')

@general.route("/adminhelp/")
def adminhelp():
    return render_template('adminhelp.html', title='Admin Help')