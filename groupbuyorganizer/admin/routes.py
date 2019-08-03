from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from datetime import timezone

from groupbuyorganizer import database
from groupbuyorganizer.admin.forms import ApplicationSettingsForm
from groupbuyorganizer.admin.models import Instance, User
from groupbuyorganizer.admin.utilities import admin_check, admin_protector

#these two go at each routes, except changing two names
admin = Blueprint('admin', __name__)

#todo- url_for('admin.home') etc prefix.  py, html


@admin.route("/event_settings/", methods=['GET', 'POST'])
@login_required
def event_settings():
    admin_check(current_user)
    return render_template('event_settings.html', title='Event Settings')


@admin.route("/category_settings/", methods=['GET', 'POST'])
@login_required
def category_settings():
    admin_check(current_user)
    return render_template('category_settings.html', title='Category Settings')


@admin.route("/user_settings/")
@login_required
def user_settings():
    admin_check(current_user)
    users = User.query.order_by(User.username.asc()).all()
    for user in users: # Making the DateTime database column human readable and converted to local timezone.
        ugly_string = user.date_created.replace(tzinfo=timezone.utc).astimezone(tz=None)
        user.date_created = ugly_string.strftime("%x %X")

    return render_template('user_settings.html', title='User Settings', users=users)


@admin.route("/user_settings/<int:user_id>/promote", methods=['GET'])
@login_required
def promote_user(user_id):
    admin_check(current_user)
    user = User.query.get_or_404(user_id)
    admin_protector(user)
    user.is_admin = True
    database.session.commit()
    flash(f'{user.username} has been promoted to admin!', 'info')
    return redirect(url_for('admin.user_settings'))


@admin.route("/user_settings/<int:user_id>/demote")
@login_required
def demote_user(user_id):
    admin_check(current_user)
    user = User.query.get_or_404(user_id)
    admin_protector(user)
    user.is_admin = False
    database.session.commit()
    flash(f'{user.username} has been demoted!', 'info')
    return redirect(url_for('admin.user_settings'))


@admin.route("/user_settings/<int:user_id>/disable")
@login_required
def disable_user(user_id):
    admin_check(current_user)
    user = User.query.get_or_404(user_id)
    admin_protector(user)
    user.is_admin = False
    user.disabled = True
    database.session.commit()
    flash(f'{user.username} has been disabled!', 'info')
    return redirect(url_for('admin.user_settings'))


@admin.route("/user_settings/<int:user_id>/enable")
@login_required
def enable_user(user_id):
    admin_check(current_user)
    user = User.query.get_or_404(user_id)
    admin_protector(user)
    user.disabled = False
    database.session.commit()
    flash(f'{user.username} has been re-enabled!', 'info')
    return redirect(url_for('admin.user_settings'))

#####################################################

@admin.route("/app_settings", methods=['GET', 'POST'])
@login_required
def app_settings():
    admin_check(current_user)
    instance = Instance.query.first()
    form = ApplicationSettingsForm()
    #form.registration_enabled.data = instance.registration_enabled
    if form.validate_on_submit():
        print(instance.registration_enabled)
        print(form.registration_enabled.data)
        instance.registration_enabled = form.registration_enabled.data
        print(instance.registration_enabled)
        database.session.commit()
        flash('Changes saved!', 'info')
        return redirect(url_for('admin.app_settings'))
    elif request.method == 'GET':
        form.registration_enabled.data = instance.registration_enabled
    return render_template('app_settings.html', title='Application Settings', form=form)