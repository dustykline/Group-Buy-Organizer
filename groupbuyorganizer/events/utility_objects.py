from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Item
from groupbuyorganizer.events.utility_functions import fetch_active_event_items, get_active_participants, \
    get_case_list, how_many_pieces_locked_in, get_cases_reserved_for_item, get_event_total, \
    get_pieces_available_split_item, get_user_total_tuple

'''All repetitive functions used in display objects go in this module.  /events/utilities.py was split into these two
pieces because it was growing a bit messy.'''


class StructuredEventItemList:
    '''This is the main object that jinja pulls data from for the event page.  It organizes items into GroupList items
    by category.
    '''
    def __init__(self, item_list, event_id):
        self.item_list = item_list
        self.event_id = event_id
        self.group_lists = generate_group_lists(self.item_list, item_to_instantiate='event_item',
                                                event_id=self.event_id)


class MyOrderObject:
    def __init__(self, user, item_list, event):
        self.user = user
        self.item_list = item_list
        self.event = event
        self.extra_charges = event.extra_charges
        self.case_list = get_case_list(self.event.id)
        self.event_total = get_event_total(self.case_list)
        self.group_lists = generate_group_lists(item_list=self.item_list, item_to_instantiate='my_order_item',
                                                event_id=self.event.id, user_id=self.user.id, current_user_view=True)
        self.splits = self.get_user_involved_splits()
        self.total_tuple = get_user_total_tuple(self.user, self.event.id, event_total=self.event_total,
                                                event_extra_charges=self.extra_charges)


    def get_user_involved_splits(self):
        split_list = []
        commits = database.session.query(CasePieceCommit).filter(CaseSplit.event_id == self.event.id,
                                                                 CaseSplit.is_complete == True,
                                                                 CasePieceCommit.case_split_id == CaseSplit.id,
                                                                 CasePieceCommit.user_id == self.user.id).all()
        for commit in commits:
            case_split = database.session.query(CaseSplit).filter(CaseSplit.id ==
                                                                                  commit.case_split_id).first()
            if case_split.is_complete == True:
                split_list.append(case_split)

        final_list = []
        reversed_list = sorted(split_list, key=lambda x: x.id, reverse=True)
        for case_split in reversed_list:
            item = database.session.query(Item).filter(Item.id == case_split.item_id).first()
            object_wrapper = CaseSplitItem(case_split, item.packing, self.event.id, item)
            created_by = database.session.query(User.username).filter_by(id=case_split.started_by).first()
            final_list.append((object_wrapper, created_by))
        return final_list


class SummaryObject:
    def __init__(self, event):
        self.event = event
        self.items = fetch_active_event_items(self.event.id)
        self.group_lists = generate_group_lists(self.items, 'summary_item', event_id=self.event.id)
        self.case_list = get_case_list(self.event.id)
        self.total = get_event_total(self.case_list)



class BreakdownObject:
    def __init__(self, event):
        self.event = event
        self.items = fetch_active_event_items(self.event.id)
        self.group_lists = generate_group_lists(self.items, 'user_breakdown_item', event_id=self.event.id)
        self.case_list = get_case_list(self.event.id)
        self.total = get_event_total(self.case_list)


class GroupList:
    '''These are nothing but containers for items with a specific category name.  This helps Jinja loop through lists
    of lists.
    '''
    def __init__(self, category_name, items):
        self.category_name = category_name
        self.items = items
        self.sort()


    def sort(self):
        self.items = sorted(self.items, key=lambda x: x.name)


class EventItem:
    def __init__(self, item, event_id):
        self.item = item
        self.event_id = event_id
        self.name = self.item.name
        self.price = self.item.price
        self.packing = self.item.packing
        self.price = self.item.price
        self.id = self.item.id
        self.case_splits = CaseSplitItemGroup(self.item.case_splits, self.packing, self.event_id)
        self.active_case_splits = self.case_splits.how_many_active_cases()
        self.cases_reserved = get_cases_reserved_for_item(self.item.id, current_user.id)
        self.pieces_locked_in = how_many_pieces_locked_in(self.event_id, self.item.id, current_user.id)
        self.your_total = self.get_total()

    def get_total(self):
        return (self.cases_reserved * self.price) + (self.pieces_locked_in * (self.price / self.packing))


class CaseSplitItemGroup:
    def __init__(self, case_splits, packing, event_id, is_single=False):
        self.case_splits = case_splits
        self.packing = packing
        self.event_id = event_id
        self.is_single = is_single
        self.active_splits = []
        self.complete_splits = []
        self.single_split = None
        self.structure_lists()

    def structure_lists(self):
        reversed_list = sorted(self.case_splits, key=lambda x: x.id, reverse=True)
        for case_split in reversed_list:
            object_wrapper = CaseSplitItem(case_split, self.packing, self.event_id)
            created_by = database.session.query(User.username).filter_by(id=case_split.started_by).first()
            list_tuple = (object_wrapper, created_by)
            if case_split.is_complete == True:
                self.complete_splits.append(list_tuple)
            else:
                self.active_splits.append(list_tuple)
        if self.is_single == True:
            if self.complete_splits:
                self.single_split = self.complete_splits[0]
            else:
                self.single_split = self.active_splits[0]

    def how_many_active_cases(self):
        return len(self.active_splits)


class CaseSplitItem:
    def __init__(self, case_split, item_packing, event_id, item=None):
        self.case_split = case_split
        self.packing = item_packing
        self.event_id = event_id
        self.item = item
        self.name = None
        self.commits = self._get_structured_commits()
        self.is_current_user_involved = self.check_if_current_user_involved()
        self.pieces_available = get_pieces_available_split_item(self.case_split.commits, self.packing)
        if self.item:
            self.name = self.item.name


    def _get_structured_commits(self):
        reversed_list = sorted(self.case_split.commits, key=lambda x: x.id, reverse=True)
        commit_list = []
        for commit in reversed_list:
            commit_id_username = database.session.query(User.id, User.username).filter(CasePieceCommit.event_id ==
                                                                    self.event_id, User.id == commit.user_id).first()
            value = None
            if self.item:
                value = float(self.item.price) * (float(commit.pieces_committed) / float(self.packing))
            commit_list.append((commit_id_username, commit, value))
        return commit_list

    def check_if_current_user_involved(self):
        for commit in self.commits:
            if current_user.id == commit[1].user_id:
                return True
        return False


class UserTotalItem:
    '''This object is used to help present data on the user breakdown page.'''
    def __init__(self, event):
        self.event = event
        self.extra_charges = event.extra_charges
        self.case_list = get_case_list(self.event.id)
        self.event_total = get_event_total(self.case_list)
        self.event_partipicants = get_active_participants(self.event.id, return_length=False)
        self.user_totals_table = self.create_user_table()


    def create_user_table(self):
        table_list = []
        for username in self.event_partipicants:
            item_total_cost = 0
            user = User.query.filter_by(username=username).first()

            # Getting total for case buys
            case_buys = CaseBuy.query.filter_by(user_id=user.id, event_id=self.event.id).all()
            for case_buy in case_buys:
                item_price = database.session.query(Item.price).filter(Item.id == case_buy.item_id).first()[0]
                item_total_cost += float(case_buy.quantity * item_price)

            # Getting total for case splits
            commits = database.session.query(CasePieceCommit).filter(CaseSplit.event_id == self.event.id,
                                                                     CaseSplit.is_complete == True,
                                                                     CasePieceCommit.case_split_id == CaseSplit.id,
                                                                     CasePieceCommit.user_id == user.id).all()
            for commit in commits:
                case_split_item_id = database.session.query(CaseSplit.item_id).filter(CaseSplit.id ==
                                                                                      commit.case_split_id).first()[0]
                item_price_packing = database.session.query(Item.price, Item.packing)\
                                                                        .filter(Item.id == case_split_item_id).first()
                split_total = (float(commit.pieces_committed) / float(item_price_packing[1])) \
                              * float(item_price_packing[0])
                item_total_cost += float(split_total)

            # Extra fee split
            extra_fee_percentage = round(float(item_total_cost)/float(self.event_total), 2)
            extra_fee_split = round(float(self.event.extra_charges) * float(extra_fee_percentage), 2)
            grand_total = round(item_total_cost + extra_fee_split, 2)

            tuple_to_be_appended = (username, item_total_cost, extra_fee_percentage, extra_fee_split, grand_total)
            table_list.append(tuple_to_be_appended)

        return table_list


class MyOrderItem:
    def __init__(self, item, user_id, current_user_view=False):
        self.item = item
        self.user_id = user_id

        self.item_name = self.item.name
        self.name = self.item.name
        self.packing = self.item.packing
        self.case_price = self.item.price
        self.piece_price = round(self.case_price / self.packing, 2)
        self.cases_you_bought = get_cases_reserved_for_item(self.item.id, self.user_id)
        self.case_splits_you_were_in = self.get_total_case_splits_user_in()
        if current_user_view == True:
            self.pieces_reserved = how_many_pieces_locked_in(self.item.event_id, self.item.id, user_id)
        else:
            self.pieces_reserved = how_many_pieces_locked_in(self.item.event_id, self.item.id, current_user.id)
        self.item_total = (self.cases_you_bought * self.item.price) + (self.pieces_reserved * (self.item.price
                                                                                               / self.item.packing))

    def get_total_case_splits_user_in(self):
        count = 0
        case_split_true = CaseSplit.query.filter_by(event_id=self.item.event_id, item_id=self.item.id,
                                                    is_complete=True).all()
        for case_split in case_split_true:
            for commit in case_split.commits:
                if commit.user_id == self.user_id:
                    count += 1
        return count


class SummaryItem:
    def __init__(self, item, event_id):
        self.item = item
        self.event_id = event_id
        self.case_list = get_case_list(self.event_id, item_id=self.item.id)

        self.name = self.item.name
        self.packing = self.item.packing
        self.case_price = self.item.price
        self.piece_price = round(self.case_price / self.packing, 2)
        self.from_case_buy = self.total_cases_bought()
        self.from_case_split = len(self.case_list[1])
        self.cases_bought = self.from_case_buy + self.from_case_split
        self.item_total = self.case_price * self.cases_bought


    def total_cases_bought(self):
        total = 0
        for case_buy in self.case_list[0]:
            total += case_buy.quantity
        return total


class UserBreakdownItem:
    def __init__(self, item, event_id):
        self.item = item
        self.event_id = event_id
        self.case_list = get_case_list(self.event_id, item_id=self.item.id)

        self.name = self.item.name
        self.packing = self.item.packing
        self.case_price = self.item.price
        self.piece_price = round(self.case_price / self.packing, 2)
        self.cases_bought = self.total_cases_bought()
        self.cases_split = len(self.case_list[1])
        self.total_cases = self.cases_bought + self.cases_split

        self.case_buy_table = self.format_case_buy_table()
        self.case_split_cards = []

        for case_split in self.case_list[1]:
            self.case_split_cards.append(CaseSplitItem(case_split, self.item.packing, self.event_id, item=self.item))


    def total_cases_bought(self):
        total = 0
        for case_buy in self.case_list[0]:
            total += case_buy.quantity
        return total


    def format_case_buy_table(self):
        table = []
        for case_buy in self.case_list[0]:
            username = database.session.query(User.username).filter(User.id == case_buy.user_id).first()[0]
            table.append((username, case_buy.quantity))
        table.sort()
        return table


def generate_group_lists(item_list, item_to_instantiate, event_id=None, user_id=None, current_user_view=False):
    '''Organizing items by category is a common task in this library.  This will organize items in different categories
    into their own groups, and will instantiate these values into a variety of items (sub-components to display item or
    purchase data on the page).
    '''

    group_lists = []
    current_category = ''
    categorized_items = []
    for group in item_list:
        if group[1] != current_category: #reset
            if categorized_items:
                group_lists.append(GroupList(current_category, categorized_items))
            current_category = group[1]
            categorized_items = []
        if item_to_instantiate == 'event_item':
            categorized_items.append(EventItem(group[0], event_id))
        elif item_to_instantiate == 'my_order_item':
            categorized_items.append(MyOrderItem(group[0], user_id, current_user_view=current_user_view))
        elif item_to_instantiate == 'summary_item':
            categorized_items.append(SummaryItem(group[0], event_id))
        elif item_to_instantiate == 'user_breakdown_item':
            categorized_items.append(UserBreakdownItem(group[0], event_id))
    group_lists.append(GroupList(current_category, categorized_items))
    return group_lists