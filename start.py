import sys

from game_engine import GameEngine


def run_main_game_process(config_file_path=None, game_preset_path=None):

    print("Welcome to Fury of Dracula game!")
    engine = GameEngine(config_file_path, game_preset_path)
    engine.play()


if __name__ == "__main__":
    config_file = ""
    game_preset_file = ""
    run_main_game_process(config_file, game_preset_file)
    sys.exit(0)
