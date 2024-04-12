import datetime
import json
import sys

from display import Display

default_config = "default_config.json"
default_preset = "default_preset.json"


class GameEngine:

    def __init__(self, config_file_path, game_preset_file_path, lang):

        self.show = Display(lang)
        self.show.phrase("welcome")

        start_time = datetime.datetime.now()
        self.show.engine_startup_with_timestamp("start", start_time)
        self.weeks_passed = "undefined"
        self.day = "undefined"
        self.phase = "undefined"
        self.situation = "undefined"
        self.current_influence = "undefined"
        self.map = "undefined"
        self.active_effects = "undefined"
        self.players = "undefined"

        GameEngine.use_config_and_preset(self, config_file_path, game_preset_file_path)

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
        if self.current_influence >= 13:
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
        hunters_spawn_available = [location for location in self.map if location["type"] == "city"]

        hunters_indexes = [i for i in range(len(self.players)) if self.players[i]["class"] != "dracula"]
        dracula_index = [index for index in range(len(self.players)) if index not in hunters_indexes][0]

        confirms = [False]

        self.show.current_hunters_position(self.players, hunters_indexes)

        while not any(confirms):
            self.show.available_start_locations(hunters_spawn_available)

            dracula_available_spawn_locations = [location["id"] for location in hunters_spawn_available]
            for index in hunters_indexes:
                location = "undefined"
                while location not in [str(location["id"]) for location in self.map]:
                    self.show.ask_player_to_choose_start_location(self.players[index])
                    location = input()
                if int(location) in dracula_available_spawn_locations:
                    dracula_available_spawn_locations.remove(int(location))
                self.players[index]["dynamic"]["location"] = location

            self.show.current_hunters_position(self.players, hunters_indexes)

            confirms = []
            for index in hunters_indexes:
                self.show.ask_hunter_to_confirm_readiness(self.players[index])
                # print(self.players[index]["name_ru"], "please, confirm readiness by typing Y below:")
                response = input()
                if response.upper() == "Y":
                    confirms.append(True)
                else:
                    confirms.append(False)
                    break

        self.show.current_hunters_position(self.players, hunters_indexes, final=True)

        while (self.players[dracula_index]["dynamic"]["location"]) not in dracula_available_spawn_locations:
            self.show.ask_player_to_choose_start_location(self.players[dracula_index])
            location = input()
            if location.isdigit():
                self.players[dracula_index]["dynamic"]["location"] = int(location)

        self.phase = "day"

    def play_day(self):
        self.show.phrase("play_day")
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

    def use_config_and_preset(self, config_file_path, game_preset_file_path):

        if not config_file_path:
            self.show.phrase("default_config")
            config = default_config
        else:
            config = config_file_path

        if not game_preset_file_path:
            self.show.phrase("default_preset")
            preset = default_preset
        else:
            preset = game_preset_file_path

        with open(config) as config:
            game_config = json.load(config)
        with open(preset) as preset:
            game_preset = json.load(preset)

        self.validate_preset(game_config, game_preset)

        self.weeks_passed = game_preset["weeks_passed"]
        self.day = game_preset["day"]
        self.phase = game_preset["starting_phase"]
        self.situation = game_preset["situation"]
        self.current_influence = game_preset["current_influence"]
        self.active_effects = game_preset["active_effects"]
        with open(game_preset["map"]) as map_file:
            self.map = json.load(map_file)
        with open(game_preset["players"]) as players:
            self.players = json.load(players)

    def validate_preset(self, config, preset):
        if not preset["weeks_passed"] in range(config["weeks_may_pass"][0], config["weeks_may_pass"][1] + 1):
            self.show.phrase("weeks_value_error")
            sys.exit(0)

        if not preset["day"] in range(config["days_in_week"][0], config["days_in_week"][1] + 1):
            self.show.phrase("day_value_error")
            sys.exit(0)

        if not preset["starting_phase"] in config["phases_available"]:
            self.show.phrase("phase_error")
            sys.exit(0)

        if not preset["situation"] in config["situations_available"]:
            self.show.phrase("situation_error")
            sys.exit(0)

        if not preset["current_influence"] in range(config["influence_range"][0], config["influence_range"][1] + 1):
            self.show.phrase("influence_error")
            sys.exit(0)

        if not preset["map"] in config["maps"]:
            self.show.phrase("map_error")
            sys.exit(0)

        for effect in preset["active_effects"]:
            if effect not in config["available_effects"]:
                self.show.effect_error(effect)
                sys.exit(0)

        if not preset["players"] in config["player_collections"]:
            self.show.phrase("character_error")
            sys.exit(0)

#  TODO: implement classes for: map, character
