class Trail:
    def __init__(self, situation=None):
        if situation is None:

            template = {
                    "city": None,
                    "city_disclosed": None,
                    "combat_card": None,
                    "combat_card_disclosed": None
                }

            self.trail = {i: template for i in range(1, 7)}

        else:
            pass  # TODO: add trail import from preset

    def add_new_trail_item(self, new_city, new_combat_card=None):

        activation_card = self.trail[6]["combat_card"]

        for i in range(6, 1, -1):
            self.trail[i] = self.trail[i - 1]

        self.trail[1] = {
                    "city": new_city,
                    "city_disclosed": False,
                    "combat_card": new_combat_card,
                    "combat_card_disclosed": False
                }

        return activation_card

    def get_cities_in_trail(self):
        trail_cities = [city["city"] for city in self.trail.values() if city["city"] is not None]
        return trail_cities

    def check_if_city_in_trail(self, city_id):
        if city_id in self.get_cities_in_trail:
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id and not city_in_trail["city_disclosed"]:
                    # self.trail[city_in_trail_id]["city_disclosed"] = True
                    return True, city_in_trail_id
        else:
            return False, None

    def open_city_in_trail(self, city_id):
        if city_id in self.get_cities_in_trail:
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id and not city_in_trail["city_disclosed"]:
                    self.trail[city_in_trail_id]["city_disclosed"] = True
                    return True, city_id
        else:
            return False, None

    def open_combat_card(self, city_id):
        if city_id in self.get_cities_in_trail:
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id:
                    self.trail[city_in_trail_id]["combat_card_disclosed"] = True
                    return True, self.trail[city_in_trail_id]["combat_card"]

        else:
            return False

    def clean_combat_card(self, city_id):
        if city_id in self.get_cities_in_trail:
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id:
                    self.trail[city_in_trail_id]["combat_card"] = None
                    self.trail[city_in_trail_id]["combat_card_disclosed"] = None
                    return True
        else:
            return False

    def open_city_by_number_in_trail(self, number_in_trail):
        pass  # TODO

