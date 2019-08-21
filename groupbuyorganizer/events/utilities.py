from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import Category, User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Event, Item

class StructuredItemList:

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


class GroupList:
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

        # {% set form.piece_quantity.choices = x.form_choices %}
        # {% set form.case_split_id = x.case_split.id %}


    def _get_structured_commits(self):
        reversed_list = sorted(self.case_split.commits, key=lambda x: x.id, reverse=True)
        commit_list = []
        for commit in reversed_list:
            commit_id_username = database.session.query(User.id, User.username).filter(CasePieceCommit.id ==
                                                                    self.event_id, User.id == commit.user_id).first()
            commit_list.append((commit_id_username, commit))
        return commit_list

    def check_if_current_user_involved(self):
        for commit in self.commits:
            if current_user.id == commit[1].user_id:
                return True
        return False


def get_pieces_available_split_item(case_split, packing):
    '''This iterates over open case splits, and based off of the total commits, will return a remainder of how many
    items are left.  This is used in the CaseSplitItem class, and in the event route to properly render forms.
    '''

    pieces_left = packing

    for commit in case_split:
        pieces_left -= commit.pieces_committed
    return pieces_left