import datetime
import json
import sys

default_config = "default_config.json"
default_preset = ""
default_preset = "default_preset.json"




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

# Чтение конфигурационного файла
with open('config.json') as config_file:
    config_data = json.load(config_file)

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