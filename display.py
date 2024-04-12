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

    def available_start_locations(self, hunters_spawn_available):
        print()

        if self.language == "EN":
            small = "small"
            big = "big"
            key = "title_en"
            filler = ", size: "
            print("Available start locations:")

        elif self.language == "RU":
            small = "малый"
            big = "большой"
            key = "title_ru"
            filler = ", размер: "
            print("Доступные для старта локации:")

        else:  # in case of adding any other language
            small = "small"
            big = "big"
            key = "title_en"
            filler = ", size: "
            print("Available start locations:")

        for city in hunters_spawn_available:
            if city["big"]:
                size = big
            else:
                size = small

            print(city[key], filler, size, sep="")
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