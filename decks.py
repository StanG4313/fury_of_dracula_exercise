import json


class Deck:
    def __init__(self, file_path):
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

    #  TODO: add methods: shuffle, take_first, take_last, add_item, get_items_amount, create child classes for tickets,
    #   items, Dracula battle cards and events (stock and discard for all types)
