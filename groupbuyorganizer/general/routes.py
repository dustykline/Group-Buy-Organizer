from flask import Blueprint

general = Blueprint('general', __name__)

@web_app.route("/events/")
@web_app.route("/")
def home():
    instance = Instance.query.first()
    return render_template('home.html', root_created = instance.root_created,
                           registration_enabled = instance.registration_enabled)


@web_app.route("/about/")
def about():
    return render_template('about.html', title='About')


@web_app.route("/register/", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        instance = Instance.query.first()
        if instance.root_created == False:
            user.is_root = True
            user.is_admin = True
            instance.root_created = True

        database.session.add(user)
        database.session.commit()
        flash(f'Your account has been created, you can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@web_app.route("/login/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.disabled:
                flash('This account has been disabled.', 'danger')
                return redirect(url_for('home'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@web_app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))


@web_app.route("/account/", methods=['GET', 'POST'])
@login_required
def account():
    form = UserOptionsForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        database.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account Settings', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Group Buy Organizer - Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    # todo configure sender
    msg.body = f'''To reset your password, please visit the following link:
    {url_for('reset_token', token=token, _external=True)}

    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send()


@web_app.route("/reset_password/", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@web_app.route("/reset_password/<token>/", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        database.session.commit()
        flash(f'Your password has been updated, you can now log in!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@web_app.route("/userhelp/")
def userhelp():
    return render_template('userhelp.html', title='User Help')

@web_app.route("/adminhelp/")
def adminhelp():
    return render_template('adminhelp.html', title='Admin Help')