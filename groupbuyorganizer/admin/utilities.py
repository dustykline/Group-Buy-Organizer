from flask import flash, redirect, url_for
from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, CasePieceCommit, CaseSplit, Item, Event

def admin_check(user):
    '''This protects against logged in users from accessing the admin pages, even if they know the direct URL.'''

    if user.is_admin == False:
        flash('Access denied.', 'danger')
        return redirect(url_for('general.home'))


def admin_protector(user):
    '''This function protects against those with admin power from manually inputting valid route commands to user
    functions, even when the buttons are disabled.
    '''

    if user.is_admin and current_user.is_admin and current_user.is_root == False:
        flash('Access denied.', 'danger')


class HomeEvent:
    def __init__(self, event):
        self.event = event
        self._case_list = self._get_case_list()
        self.added_by = self.get_added_by()
        self.active_participants = self.get_active_participants()
        self.active_case_splits = self.get_active_case_splits()
        self.total_cases = self.get_total_cases()
        self.event_total = self.get_event_total()

    def _get_case_list(self):
        '''This query is used twice, so this function exists to reduce redundant operations.  It returns a list of both
        case buys, and completed case splits.'''

        case_buys = CaseBuy.query.filter_by(event_id=self.event.id).all()
        case_splits = CaseSplit.query.filter_by(event_id=self.event.id).all()

        return case_buys, case_splits

    def get_added_by(self):
        user = User.query.filter_by(id=Event.added_by).first()
        return user.username

    def get_active_participants(self):

        case_order_user_ids = database.session.query(User.id).filter(CaseBuy.event_id == self.event.id,
                                                                     User.id == CaseBuy.user_id).all()
        case_split_user_ids = database.session.query(User.id).filter(CasePieceCommit.id == self.event.id,
                                                                     CasePieceCommit.user_id == User.id).all()

        total_user_set = set()
        for user in case_order_user_ids:
            total_user_set.add(user)
        for user in case_split_user_ids:
            total_user_set.add(user)

        return len(total_user_set)


    def get_active_case_splits(self):

        active_case_splits = database.session.query(CaseSplit.id).filter(CaseSplit.event_id == self.event.id,
                                                        CaseSplit.is_complete == False).all()
        return len(active_case_splits)

    def get_total_cases(self):
        total_count = 0
        for case_order in self._case_list[0]:
            total_count += case_order.quantity
        for case_split in self._case_list[1]:
            if case_split.is_complete == True:
                total_count += 1
        return total_count

    def get_event_total(self):
        total_cost = 0
        for case_order in self._case_list[0]:
            item = Item.query.filter_by(id=case_order.item_id).first()
            total_cost += (case_order.quantity * item.price)

        for case_split in self._case_list[1]:
            if case_split.is_complete == True:
                item = Item.query.filter_by(id=case_split.item_id).first()
                total_cost += item.price
        return total_cost