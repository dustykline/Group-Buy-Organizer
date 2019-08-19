from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, User
from groupbuyorganizer.admin.utilities import admin_check
from groupbuyorganizer.events.forms import CreateItemForm, CaseSplitForm, CreateEventForm, CaseQuantityOrderForm,\
    EditItemForm, EventExtraChargeForm, EventNotesForm, RemoveUserFromEventForm
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Event, Item
from groupbuyorganizer.events.utilities import EventItem, StructuredItemList


events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>/items/', methods=['GET', 'POST'])
@events.route('/events/<int:event_id>/', methods=['GET', 'POST'])
@login_required
def event(event_id):

    # Item add form setup
    event = Event.query.get_or_404(event_id)
    available_categories = Category.query.order_by('name')
    categories_list = [(piece.id, piece.name) for piece in available_categories]
    form = CreateItemForm()
    form.category_id.choices = categories_list

    # Remove user from event form
    remove_user_from_event_form = RemoveUserFromEventForm()
    case_buy_users = database.session.query(User.id, User.username).filter(CaseBuy.event_id == event.id, User.id == CaseBuy.user_id).all()
    case_split_users = database.session.query(User.id, User.username).filter(CaseSplit.event_id == event.id, CasePieceCommit.case_split_id == CaseSplit.id,
                        User.id == CasePieceCommit.user_id).all()
    case_buy_set = set(case_buy_users)
    case_split_set = set(case_split_users)
    total_user_set = set()
    for user in case_buy_set:
        total_user_set.add(user)
    for user in case_split_set:
        total_user_set.add(user)
    total_event_users = list(total_user_set)
    total_event_users.sort(key=lambda x: x[1])
    remove_user_from_event_form.user_to_remove.choices = total_event_users

    #Items Setup
    items = database.session.query(Item, Category.name).filter_by(event_id=event.id).join(Category, Item.category_id
                                                            == Category.id).order_by(Category.name, Item.name).all()
    structured_item_list = None
    if items:
        structured_item_list = StructuredItemList(items)

    if form.validate_on_submit() and form.item_name.data:
        item = Item(name=form.item_name.data, price=form.price.data, packing=form.packing.data,
                    category_id=form.category_id.data, added_by=current_user.get_id(), event_id=event_id)
        database.session.add(item)
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    # previous_order = CaseBuy.query.filter_by(user_id=current_user.id, event_id=event_id, item_id=item.id).first()
    if remove_user_from_event_form.validate_on_submit():
        active_user = User.query.filter_by(id=remove_user_from_event_form.user_to_remove.data).first()
        case_buys = CaseBuy.query.filter_by(event_id=event_id, user_id=active_user.id).all()
        for case_buy in case_buys:
            database.session.delete(case_buy)
        case_piece_commits = CasePieceCommit.query.filter_by(user_id=active_user.id, event_id=event_id).all()
        case_piece_commit_ids = []
        for case_piece_commit in case_piece_commits:
            case_piece_commit_ids.append(case_piece_commit.id)
            database.session.delete(case_piece_commit)
            database.session.commit()
        affected_case_splits = database.session.query(CaseSplit).filter(CaseSplit.id.in_(case_piece_commit_ids)).all()

        # Removing case splits when user was only partipants, and changing the rest to is_complete=False if they were
        # initially marked as complete.
        for case_split in affected_case_splits:
            if not case_split.commits:
                database.session.delete(case_split)
            else:
                if case_split.is_complete == True:
                    case_split.is_complete = False

        database.session.commit()
        flash(f'All transactions for {active_user.username} successfully removed from event!', 'info')
        return redirect(url_for('events.event', event_id=event_id))

    return render_template('event.html', event=event, form=form, title=f'{event.name} Overview',
                           structured_item_list=structured_item_list,
                           remove_user_from_event_form=remove_user_from_event_form)


@events.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    event_name_form = CreateEventForm()
    event_extra_charge_form = EventExtraChargeForm()
    event_notes_form = EventNotesForm()
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
    elif event_notes_form.validate_on_submit():
        event.notes = event_notes_form.event_notes.data
        database.session.commit()
        flash('Event notes updated!', 'info')
        return redirect(url_for('events.event_edit', event_id=event_id))
    elif request.method == 'GET':
        event_name_form.event_name.data = event.name
        event_extra_charge_form.extra_charges.data = event.extra_charges
        if event.notes:
            event_notes_form.event_notes.data = event.notes

    return render_template('event_edit.html', title=f'{event.name} - Edit', event_name_form=event_name_form,
                           event_extra_charge_form=event_extra_charge_form, event_notes_form=event_notes_form,
                           event=event)

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

    # Create Case Splits
    create_case_split_form = CaseSplitForm()
    choicesList = []
    for i in range(item.packing - 1):
        choicesList.append((i + 1, i + 1))
    create_case_split_form.piece_quantity.choices = choicesList

    # Customized item/order view
    event_item = EventItem(item)

    # Modify item quantity in case split form
    modify_split_qty_form = CaseSplitForm()


    if edit_item_form.validate_on_submit():
        item.name = edit_item_form.item_name.data
        item.category_id = edit_item_form.category_id.data
        item.price = edit_item_form.price.data
        if item.packing != edit_item_form.packing.data:
            pass #todo clear all splits
        item.packing = edit_item_form.packing.data
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    elif order_case_form.validate_on_submit():
        previous_order = CaseBuy.query.filter_by(user_id=current_user.id, event_id=event_id, item_id=item.id).first()
        if not previous_order:
            case_buy = CaseBuy(user_id=current_user.id, event_id=event_id, item_id=item_id,
                               quantity=order_case_form.quantity.data)
            database.session.add(case_buy)
            database.session.commit()
            flash('Case order for item added!', 'success')
            return redirect(url_for('events.item', event_id=event_id, item_id=item.id))
        else:
            if order_case_form.quantity.data == 0:
                database.session.delete(previous_order)
                database.session.commit()
                flash('Case(s) removed from your order!', 'info')
                return redirect(url_for('events.item', event_id=event_id, item_id=item.id))
            else:
                previous_order.quantity = order_case_form.quantity.data
                database.session.commit()
                flash('Case quantity updated!', 'info')
                return redirect(url_for('events.item', event_id=event_id, item_id=item.id))

    elif create_case_split_form.validate_on_submit():
        case_split = CaseSplit(started_by=current_user.id, event_id=event.id, item_id=item.id, is_complete=False)
        database.session.add(case_split)
        database.session.commit()
        case_piece_commit = CasePieceCommit(case_split_id=case_split.id, user_id=current_user.id, event_id=event_id,
                                            pieces_committed=create_case_split_form.piece_quantity.data)
        database.session.add(case_piece_commit)
        database.session.commit()
        flash('Case split created!', 'success')
        return redirect(url_for('events.item', event_id=event.id, item_id=item.id))

    elif request.method == 'GET':
        edit_item_form.category_id.choices = categories_list
        edit_item_form.item_name.data = item.name
        edit_item_form.category_id.data = item.category_id
        edit_item_form.price.data = item.price
        edit_item_form.packing.data = item.packing

        #populating current case buy quantity, if any
        previous_order = CaseBuy.query.filter_by(user_id=current_user.id, event_id=event_id, item_id=item.id).first()
        if previous_order:
            order_case_form.quantity.data = previous_order.quantity


    return render_template('item.html', added_by_user=added_by_user, form=edit_item_form,
                           order_case_form=order_case_form, event=event, item=event_item,
                           create_case_split_form=create_case_split_form, title=f'{item.name} Overview')

@events.route('/events/<int:event_id>/items/<int:item_id>/remove/', methods=['GET'])
@login_required
def remove_item(event_id, item_id):
    admin_check(current_user)
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    database.session.delete(item)
    database.session.commit()
    flash('Item successfully removed!', 'info')
    return redirect(url_for('events.event', event_id=event_id))

@events.route('/events/<int:event_id>/event_total/')
@login_required
def event_total(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_total.html', event=event, title='Event Total')

@events.route('/events/<int:event_id>/event_total_user_breakdown/', methods=['GET'])
@login_required
def event_total_user_breakdown(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_total_user_breakdown.html', event=event, title='Event Total')

@events.route('/events/<int:event_id>/items/<int:item_id>/case_split/<int:case_split_id>/remove/')
@login_required
def remove_case_split(event_id, item_id, case_split_id):
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    case_split = CaseSplit.query.get_or_404(case_split_id)
    if case_split.started_by == current_user.id or current_user.is_admin:
        database.session.delete(case_split)
        database.session.commit()
        flash('Case split!', 'info')
        return redirect(url_for('events.item', event_id=event.id, item_id=item.id))
    else:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))

@events.route('/events/<int:event_id>/items/<int:item_id>/case_split/<int:case_split_id>/commit/<int:commit_id>/remove',
    methods=['GET'])
@login_required
def remove_case_split_commit(event_id, item_id, case_split_id, commit_id):
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    case_split = CaseSplit.query.get_or_404(case_split_id)
    commit = CasePieceCommit.query.get_or_404(commit_id)
    if commit.user_id == current_user.id or current_user.is_admin:
        database.session.delete(commit)
        database.session.commit()
        flash('Case split commit removed!', 'info')
        return redirect(url_for('events.item', event_id=event.id, item_id=item.id))
    else:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))