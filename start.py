import sys

from display import Display
from game_engine import GameEngine


def run_main_game_process(config_file_path=None, game_preset_path=None, lang="EN"):
    display = Display(lang)
    engine = GameEngine(config_file_path, game_preset_path, display)
    display.phrase("wanna_load")
    answer = input()
    if answer != "":
        engine = engine.load_state(answer, display)
    engine.play()


if __name__ == "__main__":
    config_file = ""
    game_preset_file = ""
    language = "EN"
    run_main_game_process(config_file, game_preset_file, language)
    sys.exit(0)
