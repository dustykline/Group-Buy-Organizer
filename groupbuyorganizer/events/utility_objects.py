from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Item
from groupbuyorganizer.events.utility_functions import get_active_participants, get_case_list, get_event_total, \
    get_pieces_available_split_item

'''All repetitive functions used in display objects go in this module.  /events/utilities.py was split into these two
pieces because it was growing a bit messy.'''


class StructuredEventItemList: #todo dissolve
    '''This is the main object that jinja pulls data from.  It organizes items into GroupList items by category.'''

    def __init__(self, item_list, event_id):
        self.item_list = item_list
        self.event_id = event_id
        self.group_lists = []
        self.generate_group_lists()

    def generate_group_lists(self):
        current_category = ''
        categorized_items = []
        for group in self.item_list:
            if group[1] != current_category: #reset
                if categorized_items:
                    self.group_lists.append(GroupList(current_category, categorized_items))
                current_category = group[1]
                categorized_items = []
            categorized_items.append(EventItem(group[0], self.event_id))
        self.group_lists.append(GroupList(current_category, categorized_items))


class MyOrderObject:
    def __init__(self, user_id):
        pass


class SummaryObject:
    def __init__(self):
        pass


class BreakdownObject:
    def __init__(self):
        pass

class GroupList:
    '''These are nothing but containers for items with a specific category name.  This helps Jinja loop through lists
    of lists.
    '''
    def __init__(self, category_name, items):
        self.category_name = category_name
        self.items = items


class EventItem:
    def __init__(self, item, event_id):
        self.item = item
        self.event_id = event_id
        self.name = self.item.name
        self.price = self.item.price
        self.packing = self.item.packing
        self.price = self.item.price
        self.id = self.item.id
        self.case_splits = CaseSplitGroup(self.item.case_splits, self.packing, self.event_id)
        self.active_case_splits = self.case_splits.how_many_active_cases()
        self.cases_reserved = self.get_cases_reserved()
        self.pieces_locked_in = self.how_many_pieces_locked_in()
        self.your_total = self.get_total()

    def get_cases_reserved(self):
        cases_reserved = CaseBuy.query.filter_by(item_id=self.item.id, user_id=current_user.id).first()
        if cases_reserved is None:
            return 0
        return cases_reserved.quantity #todo

    def get_total(self):
        return (self.cases_reserved * self.price) + (self.pieces_locked_in * (self.price / self.packing))

    def how_many_pieces_locked_in(self):
        count = 0
        splits = CaseSplit.query.filter(CaseSplit.is_complete == True, CaseSplit.event_id == self.event_id,
                                        CaseSplit.item_id == self.item.id).all()

        for split in splits:
            commits = CasePieceCommit.query.filter(CasePieceCommit.event_id == self.event_id,
                                                   CasePieceCommit.case_split_id == split.id, CasePieceCommit.user_id ==
                                                   current_user.id).all()
            for commit in commits:
                count += commit.pieces_committed
        return count


class CaseSplitGroup:
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
    def __init__(self, case_split, item_packing, event_id):
        self.case_split = case_split
        self.packing = item_packing
        self.event_id = event_id
        self.commits = self._get_structured_commits()
        self.is_current_user_involved = self.check_if_current_user_involved()
        self.pieces_available = get_pieces_available_split_item(self.case_split.commits, self.packing)

    def _get_structured_commits(self):
        reversed_list = sorted(self.case_split.commits, key=lambda x: x.id, reverse=True)
        commit_list = []
        for commit in reversed_list:
            commit_id_username = database.session.query(User.id, User.username).filter(CasePieceCommit.event_id ==
                                                                    self.event_id, User.id == commit.user_id).first()
            commit_list.append((commit_id_username, commit))
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
                item_total_cost += case_buy.quantity * item_price

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
                split_total = (item_price_packing[0] / item_price_packing[1]) * commit.pieces_committed
                item_total_cost += split_total

            # Extra fee split
            extra_fee_percentage = round(item_total_cost/self.event_total, 2)
            extra_fee_split = round(self.event.extra_charges * extra_fee_percentage, 2)
            grand_total = round(item_total_cost + extra_fee_split, 2)

            tuple_to_be_appended = (username, item_total_cost, extra_fee_percentage, extra_fee_split, grand_total)
            table_list.append(tuple_to_be_appended)

        return table_list


class MyOrderItem:
    def __init__(self, item, user_id):
        self.item = item
        self.user_id = user_id

        self.item_name = self.item.name
        self.packing = self.item.packing
        self.case_price = self.item.price
        self.piece_price = round(self.case_price / self.packing, 2)
        self.cases_you_bought = 0 #todo take from event
        self.case_splits_you_were_in = 0 #todo
        self.pieces_reserved = 0 #todo taker from event


class SummaryItem:
    def __init__(self, item):
        self.item = item

        self.name = self.item.name
        self.packing = self.item.packing
        self.case_price = self.item.price
        self.piece_price = round(self.case_price / self.packing, 2)
        self.from_case_buy = 0 #todo global +v
        self.from_case_split = 0 #todo
        self.cases_bought = self.from_case_buy + self.from_case_split
        self.item_total = self.case_price * self.cases_bought



class UserBreakdownItem:
    def __init__(self, item_id):
        self.item_id = item_id
        self.case_list = None

        self.case_buy_table = [] #func username, qty
        self.case_split_cards = [] #func username, qty

# def generate_group_lists(item_list):
#     current_category = ''
#     categorized_items = []
#     for group in item_list:
#         if group[1] != current_category: #reset
#             if categorized_items:
#                 group_lists.append(GroupList(current_category, categorized_items))
#             current_category = group[1]
#             categorized_items = []
#         categorized_items.append(EventItem(group[0], event_id))
#     self.group_lists.append(GroupList(current_category, categorized_items)) #todo