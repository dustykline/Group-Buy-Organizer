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
            categorized_items.append(group[0])
        self.group_lists.append(GroupList(current_category, categorized_items))


class GroupList:
    def __init__(self, category_name, items):
        self.category_name = category_name
        self.items = items


class MergedItemAttributes:
    def __init__(self):
        pass