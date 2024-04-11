import json
import random


class Deck:
    def __init__(self, file_path=None):

        if file_path is None:
            self.content = []

        else:
            with open(file_path) as file:
                templates = json.load(file)

            contents = []
            content_id = 1

            for item in templates:
                for _ in range(item["amount"]):
                    content_element = dict()
                    content_element["id"] = content_id
                    content_id += 1
                    for key in item.keys():
                        if key != "amount":
                            content_element[key] = item[key]
                    contents.append(content_element)

            self.content = contents

    def shuffle(self):
        random.shuffle(self.content)

    def take_first(self):
        if self.content:
            first_element = self.content[0]
            del self.content[0]
            return first_element
        else:
            return None

    def take_last(self):
        if self.content:
            last_element = self.content[-1]
            del self.content[-1]
            return last_element
        else:
            return None

    #  TODO: add methods: add_item, get_items_amount, create child classes for tickets,
    #   items, Dracula battle cards and events (stock and discard for all types)
