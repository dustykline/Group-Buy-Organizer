from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, User
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


def get_case_list(event_id, item_id=None):
    '''This query is used several times, so this function exists to reduce redundant code.  It returns a list of both
    case buys, and completed case splits.
    '''

    if item_id == None:
        case_buys = CaseBuy.query.filter_by(event_id=event_id).all()
        case_splits = CaseSplit.query.filter_by(event_id=event_id, is_complete=True).all()
    else:
        case_buys = CaseBuy.query.filter_by(event_id=event_id, item_id=item_id).all()
        case_splits = CaseSplit.query.filter_by(event_id=event_id, item_id=item_id, is_complete=True).all()
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


def is_event_active(event_id):
    '''This returns a boolean value on whether this particular event is active or not.'''

    case_buys = CaseBuy.query.filter_by(event_id=event_id).first()
    split_commits = CasePieceCommit.query.filter_by(event_id=event_id).first()
    if case_buys or split_commits:
        return True

    return False


def fetch_user_items(user_id, event_id):
    '''Returns a list of items that the '''
    item_set = set()

    # Getting case buys
    case_buy_items = database.session.query(CaseBuy) \
        .filter(CaseBuy.user_id == user_id, CaseBuy.event_id == event_id).all()

    # Getting case splits
    split_commit_items = CasePieceCommit.query.filter_by(user_id=user_id, event_id=event_id).all()
    filtered_commits = []
    for commit in split_commit_items:
        case_split = CaseSplit.query.filter_by(id=commit.case_split_id).first()
        if case_split.is_complete == True:
            filtered_commits.append((case_split.item_id,))

    # Extracting items and category names out of case buys
    for case_buy in case_buy_items:
        item = Item.query.filter_by(id=case_buy.item_id).first()
        category_name = database.session.query(Category.name).filter_by(id=item.category_id).first()
        item_set.add((item, category_name[0]))

    # Extracting items and category names out of case split commits
    for item_id in filtered_commits:
        item = Item.query.filter_by(id=item_id[0]).first()
        category_name = database.session.query(Category.name).filter_by(id=item.category_id).first()
        item_set.add((item, category_name[0]))

    # Final formatting
    to_list = list(item_set)
    to_list = sorted(to_list, key=lambda x: x[0].name)
    return to_list

def fetch_active_event_items(event_id):
    '''Taking in the event ID, it returns all items that were involved in case buys or completed case splits in the
    given event.
    '''

    item_set = set()
    case_buy_items = database.session.query(Item).filter(CaseBuy.event_id == event_id, CaseBuy.item_id == Item.id).all()
    case_split_items = database.session.query(Item).filter(CaseSplit.event_id == event_id,
                                                           CaseSplit.item_id == Item.id,
                                                           CaseSplit.is_complete == True).all()
    for item in case_buy_items:
        item_set.add(item)
    for item in case_split_items:
        item_set.add(item)
    item_category_pair = []
    for item in item_set:
        category_name = database.session.query(Category.name).filter(Category.id == item.category_id).first()[0]
        item_category_pair.append((item, category_name))
    sorted_list = sorted(item_category_pair, key=lambda x: x[1])
    return sorted_list


def get_cases_reserved_for_item(item_id, user_id):
    '''This will return how many cases a user has purchased of a given item, otherwise it returns zero.'''

    cases_reserved = CaseBuy.query.filter_by(item_id=item_id, user_id=user_id).first()
    if cases_reserved is None:
        return 0
    return cases_reserved.quantity

def generate_active_user_select_field(event_id):

    case_buy_users = database.session.query(User.id, User.username).filter(CaseBuy.event_id == event_id, User.id == CaseBuy.user_id).all()
    case_split_users = database.session.query(User.id, User.username).filter(CaseSplit.event_id == event_id, CasePieceCommit.case_split_id == CaseSplit.id,
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
    return total_event_users


def how_many_pieces_locked_in(event_id, item_id, user_id):
    '''This will return how many case pieces a given user has locked in (aka, the case split is "complete").'''

    count = 0
    splits = CaseSplit.query.filter(CaseSplit.is_complete == True, CaseSplit.event_id == event_id,
                                    CaseSplit.item_id == item_id).all()
    for split in splits:
        commits = CasePieceCommit.query.filter(CasePieceCommit.event_id == event_id,
                                               CasePieceCommit.case_split_id == split.id, CasePieceCommit.user_id ==
                                               user_id).all()
        for commit in commits:
            count += commit.pieces_committed
    return count


def get_user_total_tuple(user, event_id, event_total=0, event_extra_charges=0):
    item_total_cost = 0

    # Getting total for case buys
    case_buys = CaseBuy.query.filter_by(user_id=user.id, event_id=event_id).all()
    for case_buy in case_buys:
        item_price = database.session.query(Item.price).filter(Item.id == case_buy.item_id).first()[0]
        item_total_cost += case_buy.quantity * item_price

    # Getting total for case splits
    commits = database.session.query(CasePieceCommit).filter(CaseSplit.event_id == event_id,
                                                             CaseSplit.is_complete == True,
                                                             CasePieceCommit.case_split_id == CaseSplit.id,
                                                             CasePieceCommit.user_id == user.id).all()
    for commit in commits:
        case_split_item_id = database.session.query(CaseSplit.item_id).filter(CaseSplit.id ==
                                                                              commit.case_split_id).first()[0]
        item_price_packing = database.session.query(Item.price, Item.packing) \
            .filter(Item.id == case_split_item_id).first()
        split_total = (item_price_packing[0] / item_price_packing[1]) * commit.pieces_committed
        item_total_cost += split_total

    # Extra fee split
    extra_fee_percentage = round(item_total_cost / event_total, 2)
    extra_fee_split = round(event_extra_charges * extra_fee_percentage, 2)
    grand_total = round(item_total_cost + extra_fee_split, 2)

    user_total_tuple = (user.username, item_total_cost, extra_fee_percentage, extra_fee_split, grand_total)
    return user_total_tuple