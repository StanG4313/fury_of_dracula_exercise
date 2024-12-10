import datetime
import json
import pickle
import sys

from display import Display
from decks import Inventory, Deck, EventsDeck, Discard
from trail import Trail
from map import GameMap

default_config_path = "res/default_config.json"
default_preset_path = "res/default_preset.json"


class GameEngine:

    def __init__(self, config_file_path, game_preset_file_path, display):

        self.active_effects = None
        self.phase = None
        self.current_influence = None
        self.show = display
        self.show.phrase("welcome")

        start_time = datetime.datetime.now()

        if not config_file_path:
            self.show.phrase("default_config")
            game_config = {}
        else:
            with open(config_file_path) as config:
                game_config = json.load(config)

        if not game_preset_file_path:
            self.show.phrase("default_preset")
            game_preset = {}
        else:
            with open(game_preset_file_path) as preset:
                game_preset = json.load(preset)


        with open(default_config_path) as config:
            default_config = json.load(config)
        with open(default_preset_path) as config:
            default_preset = json.load(config)

        attributes = [
            ("weeks_passed", "weeks_passed"),
            ("day", "day"),
            ("phase", "starting_phase"),
            ("situation", "starting_phase"),
            ("situation", "starting_phase"),
            ("current_influence", "current_influence"),
            ("active_effects", "active_effects")
        ]

        for attribute, key in attributes:
            setattr(self, attribute, game_preset.get(key, default_preset[key]))

        self.confronts_deck = game_preset.get("confronts_deck", Deck(default_preset["confronts_deck"]))
        self.fight_deck = game_preset.get("fight_deck", Deck(default_preset["fight_deck"]))
        self.events_deck = game_preset.get("events_deck", EventsDeck(default_preset["events_deck"]))
        self.items_discard = game_preset.get("items_discard", Discard(default_preset["items_discard"]))
        self.tickets_discard = game_preset.get("tickets_discard", Discard(default_preset["tickets_discard"]))
        self.confronts_discard = game_preset.get("confronts_discard", Discard(default_preset["confronts_discard"]))
        self.events_discard = game_preset.get("events_discard", Discard(default_preset["events_discard"]))

        self.show.engine_startup_with_timestamp("start", start_time)

        self.items_deck = game_preset.get("items_deck", Deck(default_preset["items_deck"]))
        self.tickets_deck = game_preset.get("tickets_deck", Deck(default_preset["tickets_deck"]))
        self.trail = game_preset.get("Trail", Trail())

        self.map = GameMap(game_preset.get("map", default_preset["map"]))

        with open(game_preset.get("players", default_preset["players"])) as players:
            self.players = json.load(players)

        for i in range(len(self.players)):
            if self.players[i]["class"] == "dracula":
                self.players[i]["dynamic"]["combat_cards"] = Inventory()
                self.players[i]["dynamic"]["event_cards"] = Inventory()
            else:
                self.players[i]["dynamic"]["item_cards"] = Inventory()
                self.players[i]["dynamic"]["event_cards"] = Inventory()
                self.players[i]["dynamic"]["tickets"] = Inventory()

        self.config = default_config
        for key in game_config:
            self.config[key] = game_config[key]

        # TODO: add inventory filling from presets using decks.Inventory class
        # TODO: add trail generation from presets

        end_time = datetime.datetime.now()
        self.show.engine_startup_with_timestamp("end", end_time)

    def play(self):
        result = ""
        while self.phase != "end":
            result = self.check_game_result()

            if self.phase == "game_preparation":
                self.prepare_game()
            elif self.phase == "day":
                self.play_day()
            elif self.phase == "sunset":
                self.play_sunset()
            elif self.phase == "night":
                self.play_night()
            elif self.phase == "sunrise":
                self.play_sunrise()

        self.show.phrase(result)
        self.show.phrase("the_end")

    def check_game_result(self):
        result = "no_result"
        if self.current_influence >= self.config["influence_range"][1]:
            result = "dracula_win"
            self.phase = "end"

        for player in self.players:
            if player["class"] == "dracula":
                if player["dynamic"]["wounds"] >= player["max_wounds"]:
                    result = "hunters_win"
                    self.phase = "end"
        return result

    def check_actions_available(self, player):
        actions = dict()
        i = 1
        current_location = player["dynamic"]["location"] # TODO: Change to .location method when changed to player/hunter class instead of dicts

        if player["dynamic"]["dead"]:
            actions["0"] = "dead"
            return actions
        if player["dynamic"]["knock_down"]:
            actions["1"] = "rise_up"
            return actions  # TODO: check it with active effect of more then one action at day


        if self.phase in ["day", "night"]:
            if self.phase == "day" or False:  # TODO: add option of special event card for night moving
                if len(self.map.get_locations_walk(current_location,1)) != 0:
                    actions[str(i)] = "move_by_road"
                    i += 1
                if (len(player["dynamic"]["tickets"].content) != 0 and
                        len(self.map.get_locations_railway(current_location, 1, 1)) != 0):
                    actions[str(i)] = "move_by_railway"
                    i += 1
                if len(self.map.get_locations_sea(current_location,1)):
                    actions[str(i)] = "move_by_sea"
                    i += 1
            if self.map.find_by_id(current_location)["type"] != "sea":
                actions[str(i)] = "heal"
                i += 1

            if self.trail.check_if_city_in_trail(current_location) and self.trail.check_if_trail_city_has_combat_card(current_location):
                actions[str(i)] = "search"
                i += 1

            # if current location in cities_in_trail and confronts_card not empty -> search action available

            # TODO: add actions: special, shopping, buy tickets, use card, trade with other hunter

        return actions

    def prepare_game(self):
        self.show.phrase("prepare_game")
        hunters_spawn_available = [location for location in self.map.locations if location["type"] == "city"]

        hunters_indexes = [i for i in range(len(self.players)) if self.players[i]["class"] != "dracula"]
        dracula_index = [index for index in range(len(self.players)) if index not in hunters_indexes][0]

        confirms = [False]

        self.show.current_hunters_position(self.players, hunters_indexes)

        dracula_available_spawn_locations = None

        while not any(confirms):
            self.show.available_start_locations(hunters_spawn_available)

            dracula_available_spawn_locations = [location["id"] for location in hunters_spawn_available]
            for index in hunters_indexes:
                location = None
                while location not in [str(location["id"]) for location in self.map.locations]:
                    self.show.ask_player_to_choose_start_location(self.players[index])
                    location = input()
                if int(location) in dracula_available_spawn_locations:
                    dracula_available_spawn_locations.remove(int(location))
                self.players[index]["dynamic"]["location"] = location

            self.show.current_hunters_position(self.players, hunters_indexes)

            confirms = []
            for index in hunters_indexes:
                self.show.ask_hunter_to_confirm_readiness(self.players[index])
                response = input()
                if response.upper() == "Y":
                    confirms.append(True)
                else:
                    confirms.append(False)
                    break

        self.show.current_hunters_position(self.players, hunters_indexes, final=True)

        self.players[dracula_index]["dynamic"]["combat_cards"].add([self.confronts_deck.take_first() for _ in range(5)])

        location = None

        while (self.players[dracula_index]["dynamic"]["location"]) not in dracula_available_spawn_locations:
            self.show.ask_player_to_choose_start_location(self.players[dracula_index])
            location = input()
            if location.isdigit():
                self.players[dracula_index]["dynamic"]["location"] = int(location)

        self.trail.add_new_trail_item(location, self.get_hunters_locations())
        self.phase = "day"

    def save_state(self, file_path):
        file_path = file_path + ".pkl"
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)
        self.show.loadsave_report(file_path)

    def load_state(self, file_path, display):
        file_path = file_path + ".pkl"
        with open(file_path, 'rb') as file:
            engine = pickle.load(file)
            engine.show = display
        self.show.loadsave_report(file_path, load = True)
        return engine

    def play_day(self):
        self.show.phrase("play_day")  #TODO: add day, week info
        self.show.phrase("wanna_save")
        answer = input()
        if answer != "":
            self.save_state(answer)

        self.hunters_act() #TODO: add condition of dracula event card with no hunter actions next day

        self.phase = "sunset"
        return

    def play_sunset(self):
        self.show.phrase("play_sunset")
        self.phase = "night"
        return

    def play_night(self):
        self.show.phrase("play_night")

        self.show.phrase("wanna_save")
        answer = input()
        if answer != "":
            self.save_state(answer)

        self.hunters_act()
        self.dracula_act() # TODO: add active effect for playing Dracula phase once again because of event card

        self.phase = "sunrise"
        return

    def play_sunrise(self):
        self.show.phrase("play_sunrise")
        self.phase = "end"
        return

    def move_by_road(self, player, distance=1):
        current_location = player["dynamic"]["location"]
        locations_available = self.map.get_locations_walk(current_location, distance)
        locations_full_info = list(map(self.map.find_by_id, locations_available))
        new_location = None

        while not new_location:
            self.show.available_move_locations(locations_full_info)
            new_location = input()
            if new_location == "CANCEL":
                return False
            if new_location.isdigit() and int(new_location) in locations_available:
                player["dynamic"]["location"] = new_location
                # TODO: add trail check and the place for dracula reaction with event cards
                self.show.player_moved(player, self.map.find_by_id(current_location),
                                       self.map.find_by_id(new_location), "road")
                if self.trail.check_if_city_in_trail(new_location):
                    self.trail.disclose_city_in_trail(new_location)
                    print("City", new_location, "open in trail!") # TODO: at the position?
                    # TODO: if there are confront card at the city in trail, ask if it will be an ambush?
                # TODO: add trail update after each move of the hunter
                return True

    def move_by_railway(self, player):
        print("move_railway WIP")
        pass

    def move_by_sea(self, player, distance=1):
        current_location = player["dynamic"]["location"]
        locations_available = self.map.get_locations_sea(current_location, distance)
        locations_full_info = list(map(self.map.find_by_id, locations_available))
        new_location = None

        while not new_location:
            self.show.available_move_locations(locations_full_info)
            new_location = input()
            if new_location == "CANCEL":
                return False
            if new_location.isdigit() and int(new_location) in locations_available:
                player["dynamic"]["location"] = new_location
                # TODO: add trail check and the place for dracula reaction with event cards
                self.show.player_moved(player, self.map.find_by_id(current_location),
                                       self.map.find_by_id(new_location), "sea")
                # TODO: add trail update after each move of the hunter
                return True

    @staticmethod
    def heal(player):
        #TODO: add request if wounds == 0, as player gonna skip the turn

        if player["class"] == "doc":
            player["dynamic"]["wounds"] -=2
        else:
            player["dynamic"]["wounds"] -= 1

        if player["dynamic"]["wounds"] < 0:
            player["dynamic"]["wounds"] = 0
        print("heal") # TODO: add proper notification of heal applied
        return True

    def search(self, player):
        # TODO: add usage of items
        current_location = player["dynamic"]["location"]
        card_disclosed, combat_card = self.trail.disclose_combat_card(current_location)
        if card_disclosed:
            print("Card disclosed:", combat_card)
        result = self.try_to_clean_city(player, combat_card)

        if result:
            print("Card", combat_card, "cleaned successfully")
        else:
            print("Failure")
        return True

    def try_to_clean_city(self, player, card):
        print("City_clean_WIP")
        current_location = player["dynamic"]["location"]
        print("Will this hunter succeed at location cleaning?")
        result = None

        while result not in ["Y", "N"]:
            result = input('Enter "Y" if yes, and "N" if no \n').upper()

        if result == "Y":
            self.trail.clean_combat_card(current_location)
            return True
        else:
            return False

    def shop(self, player):
        print("shop WIP")
        pass

    def buy_tickets(self, player):
        print("buy_tickets WIP")
        pass

    def use_card(self, player):
        print("use_card WIP")
        pass

    def trade(self, player):
        print("trade WIP")
        pass

    def special(self, player):
        print("special WIP")
        pass

    def hunters_act(self):

        actions = {
            "move_by_road": lambda: self.move_by_road(current_player),
            "move_by_railway": lambda: self.move_by_railway(current_player),
            "move_by_sea": lambda: self.move_by_sea(current_player),
            "search": lambda: self.search(current_player),
            "heal": lambda: self.heal(current_player),
            "shop": lambda: self.shop(current_player),
            "buy_tickets": lambda: self.buy_tickets(current_player),
            "use_card": lambda: self.use_card(current_player),
            "trade": lambda: self.trade(current_player),
            "special": lambda: self.special(current_player),
        }

        hunters_indexes = [i for i in range(len(self.players)) if self.players[i]["class"] != "dracula"]  # TODO: review after adding multiple hunter actions for day card

        if "custom_order" in self.active_effects:
            pass  # TODO: add after adding custom order active effect and event card
        else:
            for i in hunters_indexes:
                current_player = self.players[i]
                self.show.current_player(current_player)
                actions_available = self.check_actions_available(current_player)
                if actions_available.get("0") == "dead":
                    print(
                        "No action because the player is dead")  # TODO: add notification that player is dead and will be transported to the closest hospital
                    continue
                elif actions_available.get("1") == "rise_up":
                    current_player["dynamic"]["knock_down"] = 0  # TODO: change to player class method
                    print("The only available action for this player is to rise up")  # TODO: add notification of player rising up as an action
                    continue  # May be different if we have more than one action for hunters at day
                # TODO: add check active effects (bats) applied to the player (and actions following)
                # TODO: add turn skip if player located at the sea at night
                elif len(actions_available) == 0:
                    print("Turn skipped (no actions available, dunno why ¯\\_(ツ)_/¯)")
                    continue
                    # TODO: add public and private info output
                else:
                    result = None

                    while not result:
                        self.show.public_info(self)
                        self.show.private_info(current_player)
                        self.show.actions_available(actions_available)
                        action_chosen = input()
                        result = actions.get(actions_available.get(action_chosen), lambda: None)()

#  TODO: implement class for characters
