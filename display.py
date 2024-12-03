class Display:
    def __init__(self, lang):
        self.language = lang

    def phrase(self, phrase):
        phrases = {
            "welcome": {
                "EN": "Welcome to Fury of Dracula game!",
                "RU": "Добро пожаловать в игру Ярость Дракулы!"
            },
            "prepare_game": {
                "EN": "Game preparation in progress",
                "RU": "Запущена фаза подготовки к игре"
            },
            "no_result": {
                "EN": "No result",
                "RU": "Нет результатов игры"
            },
            "dracula_win": {
                "EN": "Dracula wins!",
                "RU": "Победа Дракулы!"
            },
            "hunters_win": {
                "EN": "Hunters win!",
                "RU": "Победа охотников!"
            },
            "the_end": {
                "EN": "Game ended",
                "RU": "Игра окончена"
            },
            "default_config": {
                "EN": "Engine uses default config (default_config.json)",
                "RU": "Движок использует стандартную конфигурацию (default_config.json)"
            },
            "default_preset": {
                "EN": "Engine uses default preset (default_preset.json)",
                "RU": "Движок использует стандартный пресет (default_preset.json)"
            },
            "weeks_value_error": {
                "EN": "weeks_passed value from preset don't pass config requirements.",
                "RU": "Значение поля weeks_passed не соответствует требованиям конфигурационного файла"
            },
            "day_value_error": {
                "EN": "day value from preset don't pass config requirements.",
                "RU": "Значение поля day не соответствует требованиям конфигурационного файла"
            },
            "phase_error": {
                "EN": "Game phase from preset is not in available phases in config.",
                "RU": "Значение поля phase не соответствует требованиям конфигурационного файла"
            },
            "situation_error": {
                "EN": "Game situation from preset is not in available situations in config.",
                "RU": "Значение поля situation не соответствует требованиям конфигурационного файла"
            },
            "influence_error": {
                "EN": "current_influence value from preset don't pass config requirements.",
                "RU": "Значение поля influence не соответствует требованиям конфигурационного файла"
            },
            "map_error": {
                "EN": "Map from preset is not in available maps in config.",
                "RU": "Карта, указанная в пресете, не является доступной согласно конфигурационному файлу"
            },
            "character_error": {
                "EN": "Game character(s) from preset is not in available collections in config.",
                "RU": "Хотя бы 1 персонаж, указанный в пресете, не является доступным согласно конфигурационному файлу"
            },
            "play_day": {
                "EN": "Current phase: Day",
                "RU": "Наступает день"
            },
            "play_sunset": {
                "EN": "Current phase: Sunset",
                "RU": "Наступает закат"
            },
            "play_night": {
                "EN": "Current phase: Night",
                "RU": "Наступает ночь"
            },
            "play_sunrise": {
                "EN": "Current phase: Sunrise",
                "RU": "Наступает рассвет"
            },
            "wanna_load": {
                "EN": 'Type the name of your save file to load or press "ENTER" to proceed',
                "RU": 'Введите имя файла чтобы загрузить сохранение, или нажмите "ENTER" чтобы продолжить'
            },
            "wanna_save": {
                "EN": 'Type the name of your save file to save or press "ENTER" to proceed',
                "RU": 'Введите имя файла чтобы сохранить состояние игры, или нажмите "ENTER" чтобы продолжить'
            }
        }
        print(phrases[phrase][self.language])

    def engine_startup_with_timestamp(self, phrase, timestamp):
        phrases = {
            "start": {
                "EN": "Game engine started at",
                "RU": "Движок игры запущен в"
            },
            "end": {
                "EN": "Game engine ready at",
                "RU": "Движок игры готов в"
            },
        }

        print(phrases[phrase][self.language], timestamp)

    def effect_error(self, effect):
        phrase = {
            "EN": "Effect " + effect + " from preset active_effects field is not in available effects in config.",
            "RU": "Эффект " + effect +
                  " из поля active_effects в пресете недоступен согласно конфигурационному файлу."
        }

        print(phrase[self.language])

    def current_hunters_position(self, players, hunters_indexes, final=False):
        print()
        first_word = {"EN": "Current", "RU": "Текущие"}

        if final:
            first_word = {"EN": "Final", "RU": "Итоговые"}

        phrase_ending = {"EN": "hunters position:", "RU": "позиции охотников:"}

        name = {"EN": "name_en", "RU": "name_ru"}

        print(first_word[self.language], phrase_ending[self.language])

        for index in hunters_indexes:
            if self.language == "RU" and players[index]["dynamic"]["location"] == "undefined":
                players[index]["dynamic"]["location"] = "не указано"
            print(players[index][name[self.language]], ": ", players[index]["dynamic"]["location"], sep="")
        print()

    def describe_locations_list(self, locations):
        for location in locations:
            key = {
                "EN": "title_en",
                "RU": "title_ru"
            }
            if location["type"] == "city":
                if self.language == "EN":
                    small = "small"
                    big = "big"
                    filler = ", size: "

                elif self.language == "RU":
                    small = "малый"
                    big = "большой"
                    filler = ", размер: "

                else:  # in case of adding any other language
                    small = "small"
                    big = "big"
                    key = "title_en"
                    filler = ", size: "

                if location["big"]:
                    size = big
                else:
                    size = small

                print(location["id"], ") ", location[key.get(self.language, "EN")], filler, size, sep="")

            elif location["type"] == "hospital":
                continue

            else:  # Seas and Dracula castle
                print(location["id"], ") ", location[key.get(self.language, "EN")], sep="")

    def available_move_locations(self, locations_available):
        print()
        phrase = {
            "RU": ["Доступные локации:", 'Укажите новую локацию, или введите "CANCEL" чтобы вернуться в предыдущее меню'],
            "EN": ["Available locations:", 'Specify a new location, or enter "CANCEL" to return to the previous menu']
        }
        print(phrase[self.language][0])
        self.describe_locations_list(locations_available)
        print()
        print(phrase[self.language][1])

    def available_start_locations(self, hunters_spawn_available):
        print()
        phrase = {
            "RU": "Доступные для старта локации:",
            "EN": "Available start locations:"
        }
        print(phrase[self.language])
        self.describe_locations_list(hunters_spawn_available)
        print()

    def ask_player_to_choose_start_location(self, hunter):
        name = {"EN": "name_en", "RU": "name_ru"}
        phrase = {"EN": ", please, specify spawn location NUMBER from available:",
                  "RU": ", пожалуйста, укажите НОМЕР стартовой локации из числа доступных:"}
        print(hunter[name[self.language]], phrase[self.language], sep="")

    def ask_hunter_to_confirm_readiness(self, hunter):
        name = {"EN": "name_en", "RU": "name_ru"}
        phrase = {"EN": "please, confirm readiness by typing Y below:",
                  "RU": "пожалуйста, подтвердите готовность вводом символа Y ниже"}
        print(hunter[name[self.language]], phrase[self.language])

    def loadsave_report(self, file, load=False):
        process = {"EN": "loaded from file", "RU": "загружено из файла"} if load else {"EN": "saved to file",
                                                                                       "RU": "сохранено в файл"}
        phrase = {"EN": "Game state", "RU": "Состояние игры"}
        print(phrase[self.language], process[self.language], file)

    def current_player(self, player):
        name = {"EN": "name_en", "RU": "name_ru"}
        phrase = {"EN": "Current player:",
                  "RU": "Текущий игрок:"}
        print()
        print(phrase[self.language], player[name[self.language]], )

    def actions_available(self, actions_dict):

        phrase = {
            "EN": "Choose your action:",
            "RU": "Выберите действие"
        }
        action_names = {
            "move_by_road": {"EN": "Move using roads", "RU": "Передвинуться по дороге"},
            "move_by_railway": {"EN": "Move using railroads", "RU": "Передвинуться по железной дороге"},
            "move_by_sea": {"EN": "Move across the sea", "RU": "Передвинутсья по морю"},
            "heal": {"EN": "Rest & heal", "RU": "Отдых и исцеление"}
        }

        print()
        print(phrase[self.language])
        for key in actions_dict.keys():
            print(key, ": ", action_names[actions_dict[key]][self.language], sep="")

    def player_moved(self, player, move_from, move_to, way_of_transportation):
        how = {
            "RU": {
                "road" : "по дороге"
            },
            "EN": {
                "road": "using roads"
            }
        }

        if self.language == "RU":
            print("Игрок", player["name_ru"], "перемещён из", move_from.get("title_ru", "госпиталя"), "в",
                  move_to["title_ru"], how["RU"][way_of_transportation], "успешно")
        else:
            print("Player", player["name_en"], "moved from", move_from.get("title_en", "hospital"), "to",
                  move_to["title_en"], how["EN"][way_of_transportation], "successfully")