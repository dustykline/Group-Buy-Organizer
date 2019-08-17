from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, User
from groupbuyorganizer.events.models import CaseBuy, Event, Item

class StructuredItemList:

    def __init__(self, item_list):
        self.item_list = item_list
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
            categorized_items.append(EventItem(group[0]))
        self.group_lists.append(GroupList(current_category, categorized_items))


class GroupList:
    def __init__(self, category_name, items):
        self.category_name = category_name
        self.items = items


class EventItem:
    def __init__(self, item):
        self.item = item
        self.name = self.item.name
        self.price = self.item.price
        self.packing = self.item.packing
        self.price = self.item.price
        self.id = self.item.id
        self.case_splits = CaseSplitGroup(self.item.case_splits, self.packing)
        self.active_case_splits = self.case_splits.how_many_active_cases()
        self.cases_reserved = self.get_cases_reserved()
        self.pieces_locked_in = self.case_splits.how_many_pieces_locked_in()
        self.your_total = self.get_total()

    def get_cases_reserved(self):
        cases_reserved = CaseBuy.query.filter_by(item_id=self.item.id).first()
        if cases_reserved is None:
            return 0
        return cases_reserved.quantity

    def get_total(self):
        return (self.cases_reserved * self.price) + (self.pieces_locked_in * (self.price / self.packing))


class CaseSplitGroup:
    def __init__(self, case_splits, packing):
        self.case_splits = case_splits
        self.packing = packing
        self.active_splits = []
        self.complete_splits = []
        self.structure_lists()

    def structure_lists(self):
        reversed_list = sorted(self.case_splits, key=lambda x: x.id, reverse=True)
        for case_split in reversed_list:
            object_wrapper = CaseSplitItem(case_split, self.packing)
            created_by = database.session.query(User.username).filter_by(id=case_split.id).first()
            list_tuple = (object_wrapper, created_by)
            if case_split.is_complete == True:
                self.complete_splits.append(list_tuple)
            else:
                self.active_splits.append(list_tuple)

    def how_many_active_cases(self):
        return len(self.active_splits)

    def how_many_pieces_locked_in(self):
        if self.complete_splits:
            for complete_split in self.complete_splits:
                if complete_split.commits.user_id == 1: #todo
                    return 4
            return 7
        else:
            return 0


class CaseSplitItem:
    def __init__(self, case_split, item_packing):
        self.case_split = case_split
        self.packing = item_packing
        self.commits = self._get_structured_commits()
        self.pieces_available = get_pieces_available_split_item(self.case_split.commits, self.packing)

    def _get_structured_commits(self):
        reversed_list = sorted(self.case_split.commits, key=lambda x: x.id, reverse=True)
        commit_list = []
        for commit in reversed_list:
            commit_username = database.session.query(User.username).filter_by(id=commit.id).first()
            commit_list.append((commit_username, commit))


def get_pieces_available_split_item(case_split, packing):
    '''This iterates over open case splits, and based off of the total commits, will return a remainder of how many
    items are left.  This is used in the CaseSplitItem class, and in the event route to properly render forms.
    '''

    pieces_left = packing
    for commit in case_split:
        packing -= commit.pieces_committed
    return pieces_left