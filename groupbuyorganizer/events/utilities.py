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
        self.active_case_splits = self.get_active_case_splits()
        self.cases_reserved = self.get_cases_reserved()
        self.pieces_locked_in = self.get_pieces_locked_in()

    def get_active_case_splits(self):
        return 0 #todo

    def get_cases_reserved(self):
        cases_reserved = CaseBuy.query.filter_by(item_id=self.item.id).first()
        if cases_reserved is None:
            return 0
        return cases_reserved.quantity

    def get_pieces_locked_in(self):
        return 0 #todo


# class MergedItemAttributes:
#     def __init__(self):
#         pass