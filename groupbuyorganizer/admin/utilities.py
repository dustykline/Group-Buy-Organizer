from flask import flash
from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Item, Event
from groupbuyorganizer.events.utility_objects import get_active_participants, get_case_list


def admin_protector(user):
    '''This function protects against those with admin power from manually inputting valid route commands to user
    functions, even when the buttons are disabled.
    '''

    if user.is_admin and current_user.is_admin and current_user.is_root == False:
        flash('Access denied.', 'danger')


class HomeEvent:
    def __init__(self, event):
        self.event = event
        self.case_list = get_case_list(self.event.id)
        self.added_by = self.get_added_by()
        self.active_participants = get_active_participants(self.event.id, return_length=True)
        self.active_case_splits = self.get_active_case_splits()
        self.total_cases = self.get_total_cases()
        self.event_total = self.get_event_total()

    def get_added_by(self):
        user = User.query.filter_by(id=Event.added_by).first()
        return user.username


    def get_active_case_splits(self):
        active_case_splits = database.session.query(CaseSplit.id).filter(CaseSplit.event_id == self.event.id,
                                                        CaseSplit.is_complete == False).all()
        return len(active_case_splits)

    def get_total_cases(self):
        total_count = 0
        for case_order in self.case_list[0]:
            total_count += case_order.quantity
        for case_split in self.case_list[1]:
            if case_split.is_complete == True:
                total_count += 1
        return total_count

    def get_event_total(self):
        total_cost = 0
        for case_order in self.case_list[0]: #todo
            item = Item.query.filter_by(id=case_order.item_id).first()
            total_cost += (case_order.quantity * item.price)

        for case_split in self.case_list[1]:
            if case_split.is_complete == True:
                item = Item.query.filter_by(id=case_split.item_id).first()
                total_cost += item.price
        return total_cost