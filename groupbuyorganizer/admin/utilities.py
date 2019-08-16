from flask import flash, redirect, url_for
from flask_login import current_user

from groupbuyorganizer import database
from groupbuyorganizer.admin.models import User
from groupbuyorganizer.events.models import CaseBuy, Item, Event

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
        '''This function '''
        case_list = []
        case_buys = CaseBuy.query.filter_by(event_id=self.event.id).all()
        if case_buys is not None:
            case_list.append(case_buys)

        #todo same with splits
        case_splits = []

        return case_buys, case_splits

    def get_added_by(self):
        user = User.query.filter_by(id=Event.added_by).first()
        return user.username

    def get_active_participants(self):
        total_participants = 0
        # for case_order in self._case_list[0]:
        #     users = User.query.filter_by(id=case_order.item_id).first()
        #     total_participants += len(users) #todo

        # todo include committed full cases
        return total_participants


    def get_active_case_splits(self):
        return 0

    def get_total_cases(self):
        total_count = 0
        for case_order in self._case_list[0]:
            total_count += case_order.quantity

        #todo include committed full cases
        return total_count

    def get_event_total(self):
        total_cost = 0
        for case_order in self._case_list[0]:
            item = Item.query.filter_by(id=case_order.item_id).first()
            total_cost += (case_order.quantity * item.price)

        # todo include committed full cases
        return total_cost