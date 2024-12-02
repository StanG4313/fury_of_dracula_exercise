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
                location = "undefined"
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

        location = None

        while (self.players[dracula_index]["dynamic"]["location"]) not in dracula_available_spawn_locations:
            self.show.ask_player_to_choose_start_location(self.players[dracula_index])
            location = input()
            if location.isdigit():
                self.players[dracula_index]["dynamic"]["location"] = int(location)

        self.trail.add_new_trail_item(location)
        self.phase = "day"

    def save_state(self, file_path):
        file_path = file_path + ".pkl"
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)
        self.show.loadsave_report(file_path)

    def load_state(self, file_path):
        file_path = file_path + ".pkl"
        with open(file_path, 'rb') as file:
            engine = pickle.load(file)
        self.show.loadsave_report(file_path, load = True)
        return engine

    def play_day(self):
        self.show.phrase("play_day")
        self.show.phrase("wanna_save")
        answer = input()
        if answer != "":
            self.save_state(answer)
        self.phase = "sunset"
        return

    def play_sunset(self):
        self.show.phrase("play_sunset")
        self.phase = "night"
        return

    def play_night(self):
        self.show.phrase("play_night")
        self.phase = "sunrise"
        return

    def play_sunrise(self):
        self.show.phrase("play_sunrise")
        self.phase = "end"
        return

    def move_by_road(self, player):
        pass

    def move_by_railway(self, player):
        pass

    def move_by_sea(self, player):
        pass

    @staticmethod
    def heal(player):
        #TODO: add request if wounds == 0 if gonna skip the turn

        if player["class"] == "doc":
            player["dynamic"]["wounds"] -=2
        else:
            player["dynamic"]["wounds"] -= 1

        if player["dynamic"]["wounds"] < 0:
            player["dynamic"]["wounds"] = 0

        return True

#  TODO: implement classes for: map, character
