from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Item

'''All repetitive functions used in display objects go in this module.  /events/utilities.py was split into these two
pieces because it was growing a bit messy.'''

def get_pieces_available_split_item(case_split, packing):
    '''This iterates over open case splits, and based off of the total commits, will return a remainder of how many
    items are left.  This is used in the CaseSplitItem class, and in the event route to properly render forms.
    '''

    pieces_left = packing

    for commit in case_split:
        pieces_left -= commit.pieces_committed
    return pieces_left


def return_qty_price_select_field(max_pieces, item_price, item_packing, whole_cases=False):
    '''Taking in the item price, item packing, and maximum allowable pieces, this will return a nicely formatted list
    for flask-wtf's SelectField, which displays the total piece sum next to the piece count.'''

    choices_list = []
    if whole_cases == False:
        for i in range(max_pieces):
            choices_list.append((i + 1, f'{i + 1}/{item_packing} - ${round((i + 1) * (item_price / item_packing), 2)}'))
    else:
        for i in range(max_pieces):
            choices_list.append((i , f'{i} - ${round(i * item_price, 2)}'))
    return choices_list


def get_case_list(event_id):
    '''This query is used several times, so this function exists to reduce redundant code.  It returns a list of both
    case buys, and completed case splits.
    '''

    case_buys = CaseBuy.query.filter_by(event_id=event_id).all()
    case_splits = CaseSplit.query.filter_by(event_id=event_id, is_complete=True).all()
    return case_buys, case_splits


def get_event_total(case_list):
    total_cost = 0
    for case_order in case_list[0]:
        item = Item.query.filter_by(id=case_order.item_id).first()
        total_cost += (case_order.quantity * item.price)

    for case_split in case_list[1]:
        if case_split.is_complete == True:
            item = Item.query.filter_by(id=case_split.item_id).first()
            total_cost += item.price
    return total_cost


def get_active_participants(event_id, return_length):
    '''This gets a list of usernames who have partipicant in a particular event.  Depending on what you want the
    function to do, it can either return the length of the list, or the list by itself.
    '''

    case_order_user_ids = database.session.query(User.username).filter(CaseBuy.event_id == event_id,
                                                                 User.id == CaseBuy.user_id).all()
    case_split_user_ids = database.session.query(User.username).filter(CasePieceCommit.event_id == event_id,
                                                                 CasePieceCommit.user_id == User.id).all()

    total_user_set = set()
    for user in case_order_user_ids:
        total_user_set.add(user)
    for user in case_split_user_ids:
        total_user_set.add(user)

    if return_length == True:
        return len(total_user_set)
    else:
        untupled_list = []
        to_list = list(total_user_set)
        for user_name in to_list:
            untupled_list.append(user_name[0])
        untupled_list.sort()
        return untupled_list

def is_user_active(user_id, event_id):
    '''This returns a boolean value on whether this particular user ID is active in the group buy event or not.'''

    case_buys = CaseBuy.query.filter_by(user_id=user_id, event_id=event_id).first()
    split_commits = CasePieceCommit.query.filter_by(user_id=user_id, event_id=event_id).first()
    if case_buys or split_commits:
        return True

    return False


def fetch_user_items(user_id, event_id):
    '''Returns a list of items that the '''