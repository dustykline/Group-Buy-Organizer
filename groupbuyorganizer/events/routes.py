from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required
import pdfkit

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, Instance, User
from groupbuyorganizer.events.forms import CreateItemForm, CreateCaseSplitForm, CreateEventForm, CaseQuantityOrderForm,\
    EditItemForm, EventExtraChargeForm, EventNotesForm, RemoveUserFromEventForm
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Event, Item
from groupbuyorganizer.events.utilities import CaseSplitGroup, EventItem, return_qty_price_select_field, \
    StructuredEventItemList


events = Blueprint('events', __name__)

@events.route('/events/<int:event_id>/items/', methods=['GET', 'POST'])
@events.route('/events/<int:event_id>/', methods=['GET', 'POST'])
@login_required
def event(event_id):

    # Item add form setup
    instance = Instance.query.first()
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
        structured_item_list = StructuredEventItemList(items, event_id)

    if form.validate_on_submit() and form.item_name.data:
        item = Item(name=form.item_name.data, price=form.price.data, packing=form.packing.data,
                    category_id=form.category_id.data, added_by=current_user.get_id(), event_id=event_id)
        database.session.add(item)
        database.session.commit()
        flash('Item successfully added!', 'success')
        return redirect(url_for('events.event', event_id=event_id))

    if remove_user_from_event_form.validate_on_submit():
        if current_user.is_admin == False:
            flash('Access denied', 'danger')
            return redirect(url_for('general.home'))
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

        database.session.commit()
        flash(f'All transactions for {active_user.username} successfully removed from event!', 'info')
        return redirect(url_for('events.event', event_id=event_id))

    return render_template('event.html', event=event, form=form, title=f'{event.name} Overview',
                           structured_item_list=structured_item_list,
                           remove_user_from_event_form=remove_user_from_event_form,
                           users_can_see_master_overview=instance.users_can_see_master_overview)


@events.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
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
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    event = Event.query.get_or_404(event_id)
    database.session.delete(event)
    database.session.commit()
    flash('Event deleted!', 'info')
    return redirect(url_for('general.home'))


@events.route("/category_settings/<int:event_id>/lock/", methods=['GET'])
@login_required
def event_lock(event_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    event = Event.query.get_or_404(event_id)
    event.is_locked = True
    database.session.commit()
    flash('Event locked!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/unlock/", methods=['GET'])
@login_required
def event_unlock(event_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    event = Event.query.get_or_404(event_id)
    event.is_locked = False
    database.session.commit()
    flash('Event unlocked!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/close/", methods=['GET'])
@login_required
def event_close(event_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    event = Event.query.get_or_404(event_id)
    event.is_locked = True
    event.is_closed = True
    database.session.commit()
    flash('Event closed!', 'info')
    return redirect(url_for('events.event_edit', event_id=event_id))


@events.route("/category_settings/<int:event_id>/open/", methods=['GET'])
@login_required
def event_open(event_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
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
    order_case_form.quantity.choices = return_qty_price_select_field(100, item.price, item.packing,
                                                                     whole_cases=True)

    # Create Case Splits
    create_case_split_form = CreateCaseSplitForm()
    create_case_split_form.piece_quantity.choices = \
        return_qty_price_select_field(item.packing - 1, item.price, item.packing)

    # Customized item/order view
    event_item = EventItem(item, event_id)

    if edit_item_form.validate_on_submit():
        item.name = edit_item_form.item_name.data
        item.category_id = edit_item_form.category_id.data
        item.price = edit_item_form.price.data
        additional_flash_message = ""
        if item.packing != edit_item_form.packing.data:
            additional_flash_message = 'Because of the change in item packing, all case splits have been removed.'
            case_splits = CaseSplit.query.filter_by(item_id=item.id)
            for case_split in case_splits:
                database.session.delete(case_split)
        item.packing = edit_item_form.packing.data
        database.session.commit()
        flash(f'Item successfully edited!  {additional_flash_message}', 'info')
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
        previous_order = CaseBuy.query.filter_by(user_id=current_user.id, event_id=event.id, item_id=item.id).first()
        if previous_order:
            order_case_form.quantity.data = previous_order.quantity


    return render_template('item.html', added_by_user=added_by_user, form=edit_item_form, item_id=item.id,
                           order_case_form=order_case_form, event=event, item=event_item,
                           create_case_split_form=create_case_split_form, title=f'{item.name} Overview')


@events.route('/events/<int:event_id>/items/<int:item_id>/remove/', methods=['GET'])
@login_required
def remove_item(event_id, item_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    database.session.delete(item)
    database.session.commit()
    flash('Item successfully removed!', 'info')
    return redirect(url_for('events.event', event_id=event_id))


@events.route('/events/<int:event_id>/event_summary/')
@login_required
def event_summary(event_id):
    event = Event.query.get_or_404(event_id)
    instance = Instance.query.first()
    if instance.users_can_see_master_overview == False:
        if current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    items = database.session.query(Item, Category.name).filter_by(event_id=event.id).join(Category, Item.category_id
                                                          == Category.id).order_by(Category.name, Item.name).all()
    structured_item_list = None
    if items:
        structured_item_list = StructuredEventItemList(items, event_id)

    return render_template('event_summary.html', event=event, is_pdf=False, structured_item_list=3,
                           users_can_see_master_overview=instance.users_can_see_master_overview, title=f'{event.name} '
        f'Summary')


@events.route('/events/<int:event_id>/event_summary/pdf')
@login_required
def event_summary_pdf(event_id):
    event = Event.query.get_or_404(event_id)
    instance = Instance.query.first()
    if instance.users_can_see_master_overview == False:
        if current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    config = pdfkit.configuration(wkhtmltopdf=instance.wkhtmltopdf_path)
    rendered = render_template('event_summary.html', is_pdf=True, event=event, title=f'{event.name} Order Overview')
    pdf = pdfkit.from_string(rendered, False, configuration=config, options={'quiet': ''})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Order_Summary.pdf'
    return response


@events.route('/events/<int:event_id>/event_total_user_breakdown/', methods=['GET'])
@login_required
def event_total_user_breakdown(event_id):
    event = Event.query.get_or_404(event_id)
    instance = Instance.query.first()

    if instance.users_can_see_master_overview == False:
        if current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    return render_template('user_breakdown.html', event=event, is_pdf=False,
                           users_can_see_master_overview=instance.users_can_see_master_overview, title=f'{event.name} '
        f'- Case Breakdown')


@events.route('/events/<int:event_id>/event_total_user_breakdown/pdf/', methods=['GET'])
@login_required
def event_total_user_breakdown_pdf(event_id):
    event = Event.query.get_or_404(event_id)
    instance = Instance.query.first()

    if instance.users_can_see_master_overview == False:
        if current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    config = pdfkit.configuration(wkhtmltopdf=instance.wkhtmltopdf_path)
    rendered = render_template('user_breakdown.html', is_pdf=True, event=event,
                               title=f'{event.name} - Case Breakdown')
    pdf = pdfkit.from_string(rendered, False, configuration=config, options={'quiet': ''})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Event Overview - User Breakdown.pdf'
    return response


@events.route('/events/<int:event_id>/user_order/<int:user_id>/', methods=['GET', 'POST'])
@login_required
def my_order(event_id, user_id):
    event = Event.query.get_or_404(event_id)
    user = User.query.get_or_404(user_id)
    instance = Instance.query.first()

    if user_id != current_user.id:
        if instance.users_can_see_master_overview == False and current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    return render_template('my_order.html', event=event, is_pdf=False, user_name = user.username,
                           users_can_see_master_overview=instance.users_can_see_master_overview,
                           title=f"{user.username}'s order")


@events.route('/events/<int:event_id>/user_order/<int:user_id>/pdf/', methods=['GET', 'POST'])
@login_required
def my_order_pdf(event_id, user_id):
    event = Event.query.get_or_404(event_id)
    user = User.query.get_or_404(user_id)
    instance = Instance.query.first()

    if instance.users_can_see_master_overview == False and current_user.id != user.id:
        if current_user.is_admin == False:
            flash('Access denied', 'warning')
            return redirect(url_for('general.home'))

    config = pdfkit.configuration(wkhtmltopdf=instance.wkhtmltopdf_path)
    rendered = render_template('my_order.html', is_pdf=True, event=event,
                               title=f"{user.username}'s order")
    pdf = pdfkit.from_string(rendered, False, configuration=config, options={'quiet': ''})
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Order_Overview.pdf'
    return response


@events.route('/events/<int:event_id>/manage_payments/', methods=['GET'])
@login_required
def manage_payments(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))
    users_case_buy = database.session.query(User.id, User.username).filter(event_id == Item.event_id, CaseBuy.item_id
                                                                           == Item.id).all()
    users_case_split = database.session.query(User.id, User.username).filter(event_id == Item.event_id,
                                                                             CaseSplit.item_id == Item.id,
                                                                             CasePieceCommit.user_id == User.id).all()
    #set
    return render_template('manage_payments.html', event=event, title='Manage Payments')


@events.route('/events/<int:event_id>/items/<int:item_id>/case_splits/<int:case_split_id>/remove/', methods=['GET'])
@login_required
def remove_case_split(event_id, item_id, case_split_id):
    if current_user.is_admin == False:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))

    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    case_split = CaseSplit.query.get_or_404(case_split_id)
    database.session.delete(case_split)
    database.session.commit()
    flash('Case split removed!', 'info')
    return redirect(url_for('events.item', event_id=event.id, item_id=item.id))


@events.route('/events/<int:event_id>/items/<int:item_id>/case_splits/<int:case_split_id>/commits/<int:commit_id>/remove',
    methods=['GET'])
@login_required
def remove_case_split_pledge(event_id, item_id, case_split_id, commit_id):
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    case_split = CaseSplit.query.get_or_404(case_split_id)
    commit = CasePieceCommit.query.get_or_404(commit_id)
    if commit.user_id == current_user.id or current_user.is_admin:
        database.session.delete(commit)
        if case_split.is_complete == True:
            case_split.is_complete = False
        database.session.commit()
        if not case_split.commits:
            database.session.delete(case_split)
            database.session.commit()
        flash('Case split commit removed!', 'info')
        return redirect(url_for('events.item', event_id=event.id, item_id=item.id))
    else:
        flash('Access denied', 'danger')
        return redirect(url_for('general.home'))


@events.route('/events/<int:event_id>/items/<int:item_id>/case_splits/<int:case_split_id>/',
    methods=['GET', 'POST'])
@login_required
def case_split(event_id, item_id, case_split_id):
    event = Event.query.get_or_404(event_id)
    item = Item.query.get_or_404(item_id)
    case_split = CaseSplit.query.get_or_404(case_split_id)
    case_split_group = CaseSplitGroup((case_split,), item.packing, event.id, is_single=True)
    created_by = case_split_group.single_split[1][0]
    case_split_item = case_split_group.single_split[0]

    modify_case_split_form = CreateCaseSplitForm()
    pieces_reserved_so_far = 0

    # This is what prevents a single user from being the sole user of a case split, forcing him to just buy a
    # case.  Aside from that, this doesn't include the user itself in the count for the max items to pledge.
    def how_many_pieces_reserved(commits, current_user_id):
        '''Short function used twice to calculate how many items are already accounted for in this case split.'''
        pieces_reserved_so_far = 0
        if len(commits) == 1 and commits[0].user_id == current_user_id:
            pieces_reserved_so_far = 1
        else:
            for commit in case_split.commits:
                if commit.user_id != current_user_id:
                    pieces_reserved_so_far += commit.pieces_committed
        return pieces_reserved_so_far

    pieces_reserved_so_far = how_many_pieces_reserved(case_split.commits, current_user.id)

    modify_case_split_form.piece_quantity.choices = return_qty_price_select_field(item.packing - pieces_reserved_so_far,
                                                                                  item.price, item.packing)
    case_piece_commit = CasePieceCommit.query.filter_by(case_split_id=case_split.id,
                                                        user_id=current_user.id).first()

    if modify_case_split_form.validate_on_submit():
        case_piece_commit = CasePieceCommit.query.filter_by(case_split_id=case_split.id, user_id=current_user.id).first()
        if case_piece_commit:
            # Validating there are enough pieces left.  Since javascript isn't implemented in this library (yet), the
            # number of pieces in a case split can change without any warning to the user.
            case_split = CaseSplit.query.filter_by(id=case_split_id).first()
            if case_split.is_complete:
                pieces_reserved_so_far = how_many_pieces_reserved(case_split.commits, current_user.id)
                if modify_case_split_form.piece_quantity.data + pieces_reserved_so_far > item.packing:
                    flash('This case split has closed in between you loading the previous page and clicking submit... '
                          ' someone else beat you to it!  Start a new case split instead.', 'warning')
                    return redirect(url_for('events.item', event_id=event.id, item_id=item.id))
            pieces_reserved_so_far = how_many_pieces_reserved(case_split.commits, current_user.id)
            if modify_case_split_form.piece_quantity.data + pieces_reserved_so_far > item.packing:
                flash('Items pledged exceeds what is currently available for this case split.  This occurs when someone'
                      ' else places a pledge right before you.  Please resubmit a pledge with a different quantity, or '
                      'otherwise create a new case split.', 'warning')
                return redirect(url_for('events.case_split', event_id=event.id, item_id=item.id,
                                        case_split_id=case_split.id))

            case_piece_commit.pieces_committed = modify_case_split_form.piece_quantity.data
        else:
            commit = CasePieceCommit(event_id=event.id, case_split_id=case_split.id,
                                                             user_id=current_user.id,
                                                 pieces_committed=modify_case_split_form.piece_quantity.data)
            database.session.add(commit)
        database.session.commit()

        # Evaluate case split is_complete status
        piece_sum = 0
        for commit in case_split.commits:
            piece_sum += commit.pieces_committed
        if case_split.is_complete:
            if piece_sum < item.packing:
                case_split.is_complete = False
                print('Toggle case split False')
        else:
            if piece_sum == item.packing:
                case_split.is_complete = True
                print('Toggle case split True')
        database.session.commit()
        flash('Case split updated!', 'success')
        return redirect(url_for('events.case_split', event_id=event.id, item_id=item.id, case_split_id=case_split.id))

    elif request.method == 'GET':

        if case_piece_commit:
            modify_case_split_form.piece_quantity.data = case_piece_commit.pieces_committed

    return render_template('case_split.html', event=event, item=item, created_by=created_by,
                           form=modify_case_split_form, case_split=case_split_item, is_locked=event.is_locked,
                           title=f'{item.name} Case Split')