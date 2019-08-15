from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, User
from groupbuyorganizer.admin.utilities import admin_check
from groupbuyorganizer.events.forms import CreateItemForm, CreateEventForm, CaseQuantityOrderForm, EditItemForm, \
    EventExtraChargeForm
from groupbuyorganizer.events.models import Event, Item
from groupbuyorganizer.events.utilities import StructuredItemList


events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>', methods=['GET', 'POST'])
@events.route('/events/<int:event_id>/items', methods=['GET', 'POST'])
@login_required
def event(event_id):

    # Form Setup
    event = Event.query.get_or_404(event_id)
    available_categories = Category.query.order_by('name')
    categories_list = [(piece.id, piece.name) for piece in available_categories]
    form = CreateItemForm()
    form.category_id.choices = categories_list

    #Items Setup
    items = database.session.query(Item, Category.name).filter_by(event_id=event.id).join(Category, Item.category_id
                                                            == Category.id).order_by(Category.name, Item.name).all()
    structured_item_list = StructuredItemList(items)

    if form.validate_on_submit():
        item = Item(name=form.item_name.data, price=form.price.data, packing=form.packing.data,
                    category_id=form.category_id.data, added_by=current_user.get_id(), event_id=event_id)
        database.session.add(item)
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    return render_template('event.html', event=event, form=form, title=f'{event.name} Overview',
                           structured_item_list=structured_item_list)


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

@events.route('/events/<int:event_id>/items/<int:item_id>/', methods=['GET', 'POST'])
@login_required
def item(event_id, item_id):
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)

    # Item edit form
    available_categories = Category.query.order_by('name')
    categories_list = [(piece.id, piece.name) for piece in available_categories]
    edit_item_form = EditItemForm()
    edit_item_form.category_id.choices = categories_list

    # Added by name
    added_by_user = User.query.filter_by(id=item.added_by).first()

    # Case Quantity Form
    order_case_form = CaseQuantityOrderForm()

    if edit_item_form.validate_on_submit():
        item.name = edit_item_form.item_name.data
        item.category_id = edit_item_form.category_id.data
        item.price = edit_item_form.price.data
        item.packing = edit_item_form.packing.data
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    elif request.method == 'GET':
        edit_item_form.category_id.choices = categories_list
        edit_item_form.item_name.data = item.name
        edit_item_form.category_id.data = item.category_id
        edit_item_form.price.data = item.price
        edit_item_form.packing.data = item.packing

    return render_template('item.html', added_by_user=added_by_user, form=edit_item_form,
                           order_case_form=order_case_form, event=event, item=item,
                           title=f'{item.name} Overview')

@events.route('/events/<int:event_id>/items/<int:item_id>/remove/', methods=['GET'])
@login_required
def remove_item(event_id, item_id):
    print('fired!')
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    flash('placeholder text until db wired in here, no actions taken', 'primary')
    return redirect(url_for('events.event', event_id=event_id))