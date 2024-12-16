from decks import Inventory


class Player:
    def __init__(self, params):
        self.id = params["id"]
        self.player_class = params["class"]
        self.name_ru = params["name_ru"]
        self.name_en = params["name_en"]
        self.max_wounds = params["max_wounds"]
        self.max_events = params["max_events"]

        self.location = int()
        self.wounds = 0
        self.event_cards = Inventory()

    def get_wound(self, amount: int()):
        self.wounds += amount

    def check_if_dead(self) -> bool:
        return self.wounds >= self.max_wounds

    def get_event_card(self, card) -> list:
        self.event_cards.add([card])

        return self.check_inventory_overload(self.event_cards, self.max_events)

    def heal(self, amount):
        self.wounds -= amount
        if self.wounds < 0:
            self.wounds = 0


    @staticmethod
    def check_inventory_overload(invent: Inventory, max_amount: int()) -> list:
        items_to_discard = list()

        while invent.get_items_amount() > max_amount:
            print("You have too much cards! Choose which one to discard specifying it's ID:")
            for element in invent.content:
                print(element)
            items_to_discard.append(invent.take_by_id(int(input())))

        return items_to_discard


class Dracula(Player):
    def __init__(self, params):
        super().__init__(params)

        self.refill_combat = params["refill_combat"]

        self.combat_cards = Inventory()


class Hunter(Player):
    def __init__(self, params):
        super().__init__(params)

        self.max_bites = params["max_bites"]
        self.max_items = params["max_items"]

        self.bites = 0
        self.knock_down = False
        self.dead = False
        self.item_cards = Inventory()
        self.tickets = Inventory()
        self.disclosed_event = dict()
        self.disclosed_item = dict()


    def get_bite(self):
        self.bites += 1

    def check_if_dead(self) -> bool:
        return super().check_if_dead() or self.bites >= self.max_bites

    def get_item_card(self, get_item_function, repeats) -> list:
        for _ in range(repeats):

            self.item_cards.add([get_item_function()])

        return self.check_inventory_overload(self.item_cards, self.max_items)

    def hunter_knock_down(self):
        self.knock_down = True

    def hunter_rise_up(self):
        self.knock_down = False


