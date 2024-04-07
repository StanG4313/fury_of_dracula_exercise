import datetime

default_config = "default_config.json"
default_preset = ""


class GameEngine:
    def __init__(self, config_file_path, game_preset_file_path):

        start_time = datetime.datetime.now()
        print("Game engine started at", start_time)

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




import json

# Чтение конфигурационного файла
with open('config.json') as config_file:
    config_data = json.load(config_file)

# Получение значений из конфигурационного файла
value = config_data['key_name']

# Изменение значений в конфигурационном файле
config_data['key_name'] = 'new_value'

# Сохранение изменений в конфигурационном файле
with open('config.json', 'w') as config_file:
    json.dump(config_data, config_file)