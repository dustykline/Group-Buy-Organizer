from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from datetime import timezone

from groupbuyorganizer import database
from groupbuyorganizer.admin.forms import ApplicationSettingsForm, CreateCategoryForm
from groupbuyorganizer.admin.models import Category, Instance, User
from groupbuyorganizer.admin.utilities import admin_check, admin_protector
from groupbuyorganizer.events.models import Event


admin = Blueprint('admin', __name__)

@admin.route("/category_settings/", methods=['GET', 'POST'])
@login_required
def category_settings():
    admin_check(current_user)
    form = CreateCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.category_name.data)
        database.session.add(category)
        database.session.commit()
        flash('Category successfully added!', 'success')
        return redirect(url_for('admin.category_settings'))
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('category_settings.html', title='Category Settings', categories=categories, form=form)


@admin.route("/category_settings/<int:category_id>/edit/", methods=['GET', 'POST'])
@login_required
def category_edit(category_id):
    admin_check(current_user)
    category = Category.query.get_or_404(category_id)
    form = CreateCategoryForm()
    if form.validate_on_submit():
        category.name = form.category_name.data
        database.session.commit()
        flash(f'{category.name} has been edited!', 'info')
        return redirect(url_for('admin.category_settings'))
    elif request.method == 'GET':
        form.category_name.data = category.name
    return render_template('category_edit.html', title='Edit Category Name', form=form)


@admin.route("/categories/<int:category_id>/remove/", methods=['GET'])
@login_required
def category_remove(category_id):
    admin_check(current_user)
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('Access denied', 'danger')
        return redirect(url_for('admin.category_settings'))

    flash_message = 'Category deleted! '
    if category.items:
        flash_message += " Item(s) in this category have been moved to 'Uncategorized.'"
        for item in category.items:
            item.category_id = 1
            database.session.commit()
    database.session.delete(category)
    database.session.commit()
    flash(f'{flash_message}', 'info')
    return redirect(url_for('admin.category_settings'))


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
    if form.validate_on_submit():
        instance.registration_enabled = form.registration_enabled.data
        database.session.commit()
        flash('Changes saved!', 'info')
        return redirect(url_for('admin.app_settings'))
    elif request.method == 'GET':
        form.registration_enabled.data = instance.registration_enabled
    return render_template('app_settings.html', title='Application Settings', form=form)

#todo - temporary for dev purposes
@admin.cli.command('bootstrap')
@admin.route("/bootstrap", methods=['GET', 'POST'])
def bootstrap():
    # database.drop_all()
    # database.create_all()

    # database.session.add(Instance())

    # database.session.add(Category(name='Uncategorized'))
    database.session.add(Category(name='Dog Toys'))
    database.session.add(Category(name='Cat Toys'))
    database.session.add(Category(name='Fish Supplies'))
    database.session.add(Category(name='Dog Food'))

    database.session.add(Event(name='Test Session 1', added_by=1))
    database.session.add(Event(name='Test Session 2', added_by=1))
    database.session.commit()

    flash('Success!', 'primary')
    return redirect(url_for('general.home'))