from decks import Inventory


class Player:
    def __init__(self, params):
        self.id = params["id"]
        self.player_class = params["id"]
        self.name_ru = params["name_ru"]
        self.name_en = params["name_en"]
        self.max_wounds = params["max_wounds"]
        self.max_events = params["max_events"]

        self.location = int()
        self.wounds = 0
        self.event_cards = Inventory()

    def get_wound(self, amount: int()):
        self.wounds += amount

    def check_if_dead(self):
        return self.wounds >= self.max_wounds


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

    def check_if_dead(self):
        return super().check_if_dead() or self.bites >= self.max_bites

