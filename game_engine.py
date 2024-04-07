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

        GameEngine.use_config_and_preset(self, config_file_path, game_preset_file_path)

        print("Game engine ready at", start_time)

    def play(self):
        command = ""
        while command.upper() != "EXIT":
            print('Type some command! (to stop playing type "exit")')
            command = input()
            print(command)

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
        with open(game_preset["map"]) as map:
            self.map = json.load(map)

# Изменение значений в конфигурационном файле
config_data['key_name'] = 'new_value'

# Сохранение изменений в конфигурационном файле
with open('config.json', 'w') as config_file:
    json.dump(config_data, config_file)