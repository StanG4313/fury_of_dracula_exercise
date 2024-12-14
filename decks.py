import json
import random


class BaseDeck:
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

    def add(self, items):
        items.extend(self.content)
        self.content = items

    def empty(self):
        contents = self.content
        self.content = []

        return contents

    def get_items_amount(self):
        return len(self.content)


class Discard(BaseDeck):
    def take_by_attribute(self, key, value):
        pass

    def take_by_id(self, element_id):
        for i, element in enumerate(self.content):
            if element.get('id') == int(element_id):
                return self.content.pop(i)
        return None

    # Use take_by_id as a base


class Inventory(Discard):
    def enumerate(self):
        pass  # add fields needed to be enumerated


class Deck(BaseDeck):
    def __init__(self, related_discard:Discard, file_path=None, ):
        super().__init__(file_path)
        self.related_discard = related_discard

    def shuffle(self):
        random.shuffle(self.content)

    def take_first(self):
        if not self.content:
            print("Deck refilled")
            self.refill()

        first_element = self.content[0]
        del self.content[0]
        return first_element

    def refill(self):
        self.content = self.related_discard.empty()

    def add(self, items):
        super().add(items)
        self.shuffle()


class EventsDeck(Deck):
    def add_to_the_end(self, items):
        self.content.extend(reversed(items))

    def take_last(self):
        if self.content:
            last_element = self.content[-1]
            del self.content[-1]
            return last_element
        else:
            return None
