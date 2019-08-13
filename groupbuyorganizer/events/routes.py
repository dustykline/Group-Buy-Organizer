from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category
from groupbuyorganizer.admin.utilities import admin_check
from groupbuyorganizer.events.forms import CreateItemForm, CreateEventForm, EventExtraChargeForm
from groupbuyorganizer.events.models import Event, Item


events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event(event_id):
    # Form Setup
    event = Event.query.get_or_404(event_id)
    available_categories = Category.query.order_by('name')
    categories_list = [(piece.id, piece.name) for piece in available_categories]
    form = CreateItemForm()
    form.category_id.choices = categories_list

    #Items Setup
    items = Item.query

    if form.validate_on_submit():
        item = Item(name=form.item_name.data, price=form.price.data, packing=form.packing.data,
                    category_id=form.category_id.data, added_by=current_user.get_id(), event_id=event_id)
        database.session.add(item)
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    return render_template('event.html', event=event, form=form, title=f'{event.name} Overview')


@events.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event_name_form = CreateEventForm()
    event_extra_charge_form = EventExtraChargeForm()
    if event_name_form.validate_on_submit():
        event.name = event_name_form.event_name.data
        database.session.commit()
        flash(f'{event.name} has been edited!', 'info')
        return redirect(url_for('events.event_edit', event_id=event_id))
    elif event_extra_charge_form.validate_on_submit():
        event.extra_charges = event_extra_charge_form.extra_charges.data
        database.session.commit()
        flash('Extra charges updated!', 'info')
        return redirect(url_for('events.event_edit', event_id=event_id))
    elif request.method == 'GET':
        event_name_form.event_name.data = event.name
        event_extra_charge_form.extra_charges.data = event.extra_charges

    return render_template('event_edit.html', title=f'{event.name} - Edit', event_name_form=event_name_form,
                           event_extra_charge_form=event_extra_charge_form, event=event)

@events.route("/category_settings/<int:event_id>/remove/", methods=['GET'])
@login_required
def event_remove(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    database.session.delete(event)
    database.session.commit()
    flash('Event deleted!', 'info')
    return redirect(url_for('general.home'))

@events.route("/category_settings/<int:event_id>/lock/", methods=['GET'])
@login_required
def event_lock(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event.is_locked = True
    database.session.commit()
    flash('Event locked!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/unlock/", methods=['GET'])
@login_required
def event_unlock(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event.is_locked = False
    database.session.commit()
    flash('Event unlocked!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/close/", methods=['GET'])
@login_required
def event_close(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event.is_locked = True
    event.is_closed = True
    database.session.commit()
    flash('Event closed!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/open/", methods=['GET'])
@login_required
def event_open(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event.is_closed = False
    database.session.commit()
    flash('Event opened!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))