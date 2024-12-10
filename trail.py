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
            self.hunters_view = None
            self.update_hunters_view()

        else:
            pass  # TODO: add trail import from preset

    def add_new_trail_item(self, new_city, hunters_locations, new_combat_card=None):

        activation_card = self.trail[6]["combat_card"]

        for i in range(6, 1, -1):
            self.trail[i] = self.trail[i - 1]

        self.trail[1] = {
                    "city": new_city,
                    "city_disclosed": True if new_city in hunters_locations else False,
                    "combat_card": None if new_city in hunters_locations else new_combat_card,
                    "combat_card_disclosed": False if new_combat_card else None
                }

        self.update_hunters_view()
        return activation_card

    def get_cities_in_trail(self):
        trail_cities = [city["city"] for city in self.trail.values() if city["city"] is not None]
        return trail_cities

    def check_if_city_in_trail(self, city_id):
        if city_id in self.get_cities_in_trail():
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id:
                    if not city_in_trail["city_disclosed"]:
                        self.trail[city_in_trail_id]["city_disclosed"] = True
                    return True, city_in_trail_id
        else:
            return False, None

    def disclose_city_in_trail(self, city_id):
        if city_id in self.get_cities_in_trail():
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id and not city_in_trail["city_disclosed"]:
                    self.trail[city_in_trail_id]["city_disclosed"] = True
                    self.update_hunters_view()
                    return True
        else:
            return False

    def check_if_trail_city_has_combat_card(self, city_id):
        for city_in_trail_id, city_in_trail in self.trail.items():
            if city_in_trail["city"] == city_id and self.trail[city_in_trail_id]["combat_card"]:
                return True
        return False


    def disclose_combat_card(self, city_id):
        if city_id in self.get_cities_in_trail():
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id:
                    if not self.trail[city_in_trail_id]["combat_card_disclosed"]:
                        self.trail[city_in_trail_id]["combat_card_disclosed"] = True
                        result = True
                        self.update_hunters_view()
                    else:
                        result = False


                    return result, self.trail[city_in_trail_id]["combat_card"]

        else:
            return False

    def clean_combat_card(self, city_id):
        if city_id in self.get_cities_in_trail():
            for city_in_trail_id, city_in_trail in self.trail.items():
                if city_in_trail["city"] == city_id:
                    self.trail[city_in_trail_id]["combat_card"] = None
                    self.trail[city_in_trail_id]["combat_card_disclosed"] = None
                    self.update_hunters_view()
                    return True
        else:
            return False

    def open_city_by_number_in_trail(self, number_in_trail):
        self.trail[number_in_trail]["city_disclosed"] = True
        self.update_hunters_view()
        return

    def clear_trail_cells(self, numbers):
        self.update_hunters_view()
        # TODO will be needed after adding event cards with this functionality

    def update_hunters_view(self):
        result = dict()
        for cell in self.trail:
            location = None
            confront_card = None

            if self.trail[cell]["city_disclosed"]:
                location = self.trail[cell]["city"]

            elif not self.trail[cell]["city_disclosed"]:
                location = "Hidden"

            if self.trail[cell]["combat_card_disclosed"]:
                confront_card = self.trail[cell]["combat_card"]
            elif not self.trail[cell]["combat_card_disclosed"]:
                confront_card = "Hidden"

            result[cell] = (location, confront_card)
            self.hunters_view = result
        return

# TODO: sea locations - you can`t use confront cards, you can't disclose sea locations by moving to them with hunter, you receive dmg as Dracula moving to sea from city or another sea (different amount)