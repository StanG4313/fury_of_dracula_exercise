import datetime
import json
import sys

default_config = "default_config.json"
default_preset = "default_preset.json"


def validate_preset(config, preset):
    if not preset["weeks_passed"] in range(config["weeks_may_pass"][0], config["weeks_may_pass"][1] + 1):
        print("Weeks_passed value from preset don't pass config requirements.")
        sys.exit(0)

    if not preset["day"] in range(config["days_in_week"][0], config["days_in_week"][1] + 1):
        print("weeks_passed value from preset don't pass config requirements.")
        sys.exit(0)

    if not preset["starting_phase"] in config["phases_available"]:
        print("Game phase from preset is not in available phases in config.")
        sys.exit(0)

    if not preset["situation"] in config["situations_available"]:
        print("Game situation from preset is not in available situations in config.")
        sys.exit(0)

    if not preset["current_influence"] in range(config["influence_range"][0], config["influence_range"][1] + 1):
        print("current_influence value from preset don't pass config requirements.")
        sys.exit(0)

    if not preset["map"] in config["maps"]:
        print("Map from preset is not in available phases in config.")
        sys.exit(0)

    for effect in preset["active_effects"]:
        if effect not in config["available_effects"]:
            print(effect, "from preset active effects is not in available effects in config.")
            sys.exit(0)

    if not preset["players"] in config["player_collections"]:
        print("Game characters from preset is not in available collections in config.")
        sys.exit(0)


class GameEngine:

    def __init__(self, config_file_path, game_preset_file_path):

        start_time = datetime.datetime.now()
        print("Game engine started at", start_time)
        self.weeks_passed = "undefined"
        self.day = "undefined"
        self.phase = "undefined"
        self.situation = "undefined"
        self.current_influence = "undefined"
        self.map = "undefined"
        self.active_effects = "undefined"
        self.players = "undefined"

        GameEngine.use_config_and_preset(self, config_file_path, game_preset_file_path)

        print("Game engine ready at", start_time)

    def play(self):
        result = ""
        while self.phase != "end":
            result = self.check_game_result()

            if self.phase == "game_preparation":
                self.prepare_game()
            elif self.phase == "day":
                self.play_day()
            elif self.phase == "night":
                self.play_night()

        print(result)
        print("Game ended")

    def check_game_result(self):
        result = "No result"
        if self.current_influence >= 13:
            result = "Dracula wins!"
            self.phase = "end"

        for player in self.players:
            if player["class"] == "dracula":
                if player["dynamic"]["wounds"] >= player["max_wounds"]:
                    result = "Hunters win!"
                    self.phase = "end"
        return result

    def prepare_game(self):
        print("Game preparation in progress")
        hunters_spawn_available = [location for location in self.map if location["type"] == "city"]

        hunters_indexes = [i for i in range(len(self.players)) if self.players[i]["class"] != "dracula"]
        dracula_index = [index for index in range(len(self.players)) if index not in hunters_indexes][0]

        confirms = [False] * len(hunters_indexes)

        print()
        print("Current hunters position:")
        for index in hunters_indexes:
            print(self.players[index]["name_ru"], ": ", self.players[index]["dynamic"]["location"], sep="")

        while not any(confirms):
            print()
            print("Available start locations:")
            for city in hunters_spawn_available:
                if city["big"]:
                    size = "big"
                else:
                    size = "small"

                print(city["title_ru"], ", size: ", size, sep="")
            print()

            dracula_available_spawn_locations = [location["id"] for location in hunters_spawn_available]
            for index in hunters_indexes:
                location = "undefined"
                while location not in [str(location["id"]) for location in self.map]:
                    print(self.players[index]["name_ru"], ", please, specify spawn location NUMBER from available:",
                          sep="")
                    location = input()
                if int(location) in dracula_available_spawn_locations:
                    dracula_available_spawn_locations.remove(int(location))
                self.players[index]["dynamic"]["location"] = location

            print("Current hunters position:")
            for index in hunters_indexes:
                print(self.players[index]["name_ru"], ": ", self.players[index]["dynamic"]["location"], sep="",
                      end=", ")

            confirms = []
            for index in hunters_indexes:
                print(self.players[index]["name_ru"], "please, confirm readiness by typing Y below:")
                response = input()
                if response.upper() == "Y":
                    confirms.append(True)
                else:
                    confirms.append(False)
                    break

        print()
        print("Final hunters position:")
        for index in hunters_indexes:
            print(self.players[index]["name_ru"], ": ", self.players[index]["dynamic"]["location"], sep="",
                  )

        while (self.players[dracula_index]["dynamic"]["location"]) not in dracula_available_spawn_locations:
            print("Dracula, please, specify NUMBER of your starting position:")
            location = input()
            if location.isdigit():
                self.players[dracula_index]["dynamic"]["location"] = int(location)

        self.phase = "day"

    def play_day(self):
        print("Play day")
        self.phase = "night"
        return

    def play_night(self):
        print("Play night")
        self.phase = "end"
        return

    def use_config_and_preset(self, config_file_path, game_preset_file_path):

        if not config_file_path:
            print("Engine uses default config")
            config = default_config
        else:
            config = config_file_path

        if not game_preset_file_path:
            print("Engine uses default preset")
            preset = default_preset
        else:
            preset = game_preset_file_path

        with open(config) as config:
            game_config = json.load(config)
        with open(preset) as preset:
            game_preset = json.load(preset)

        validate_preset(game_config, game_preset)

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

#  TODO: implement classes for: map, character, trail, deck
