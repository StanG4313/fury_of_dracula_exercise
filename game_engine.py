import datetime
import json
import pickle
import sys

from display import Display
from decks import Deck, EventsDeck, Discard
from trail import Trail
from players import Hunter, Dracula
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

        self.confronts_discard = game_preset.get("confronts_discard", Discard(default_preset["confronts_discard"]))
        self.confronts_deck = game_preset.get("confronts_deck", Deck(related_discard=self.confronts_discard, file_path=default_preset["confronts_deck"]))
        self.fight_deck = game_preset.get("fight_deck", Deck(default_preset["fight_deck"]))
        self.events_discard = game_preset.get("events_discard", Discard(default_preset["events_discard"]))
        self.events_deck = game_preset.get("events_deck", EventsDeck(related_discard=self.events_discard, file_path=default_preset["events_deck"]))
        self.items_discard = game_preset.get("items_discard", Discard(default_preset["items_discard"]))
        self.items_deck = game_preset.get("items_deck", Deck(related_discard= self.items_discard, file_path=default_preset["items_deck"]))
        self.tickets_discard = game_preset.get("tickets_discard", Discard(default_preset["tickets_discard"]))
        self.tickets_deck = game_preset.get("tickets_deck", Deck(related_discard= self.tickets_discard, file_path=default_preset["tickets_deck"]))

        self.trail = game_preset.get("Trail", Trail())
        self.map = GameMap(game_preset.get("map", default_preset["map"]))

        self.show.engine_startup_with_timestamp("start", start_time)



        with open(game_preset.get("players", default_preset["players"])) as players:
            players = json.load(players)
            self.hunters = list()
            for player in players:
                if player["class"] == "dracula":
                    self.dracula = Dracula(player)
                else:
                    self.hunters.append(Hunter(player))

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

        if self.dracula.wounds >= self.dracula.max_wounds:
            result = "hunters_win"
            self.phase = "end"
        return result

    def check_actions_available(self, player):
        actions = dict()
        i = 1
        current_location = player.location

        if player.dead:
            actions["0"] = "dead"
            return actions
        if player.knock_down:
            actions["1"] = "rise_up"
            return actions  # TODO: check it with active effect of more then one action at day
        if self.map.find_by_id(current_location)["type"] == "sea":
            actions["0"] = "sea"
            return actions


        if self.phase in ["day", "night"]:
            if self.phase == "day" or False:  # TODO: add option of special event card for night moving
                if len(self.map.get_locations_walk(current_location,1)) != 0:
                    actions[str(i)] = "move_by_road"
                    i += 1
                if (len(player.tickets.content) != 0 and
                        len(self.map.get_locations_railway(int(current_location), 1, 1)) != 0):
                    actions[str(i)] = "move_by_railway"
                    i += 1
                if len(self.map.get_locations_sea(current_location,1)):
                    actions[str(i)] = "move_by_sea"
                    i += 1
            if self.map.find_by_id(current_location)["type"] != "sea":
                actions[str(i)] = "heal"
                i += 1

            if (self.trail.check_if_city_in_trail(current_location) and
                    self.trail.check_if_trail_city_has_combat_card(current_location)):
                actions[str(i)] = "search"
                i += 1

            if self.map.find_by_id(current_location)["type"] in ["city", "hospital"]:
                actions[str(i)] = "shop"
                i += 1

                if self.map.find_by_id(current_location)["type"] != "hospital":
                    actions[str(i)] = "buy_tickets"
                    i += 1
        # TODO: add actions: special, use card, trade with other hunter
        return actions

    def prepare_game(self):
        self.show.phrase("prepare_game")
        hunters_spawn_available = [location for location in self.map.locations if location["type"] == "city"]

        confirms = [False]

        dracula_available_spawn_locations = None

        while not any(confirms):
            self.show.available_start_locations(hunters_spawn_available)

            dracula_available_spawn_locations = [location["id"] for location in hunters_spawn_available]
            for hunter in self.hunters:
                location = None
                while location not in [str(location["id"]) for location in self.map.locations]:
                    self.show.ask_player_to_choose_start_location(hunter)
                    location = input()
                if int(location) in dracula_available_spawn_locations:
                    dracula_available_spawn_locations.remove(int(location))
                hunter.location = location

            self.show.current_hunters_position(self.hunters)

            confirms = []
            for hunter in self.hunters:
                self.show.ask_hunter_to_confirm_readiness(hunter)
                response = input()
                if response.upper() == "Y":
                    confirms.append(True)
                else:
                    confirms.append(False)
                    break

        self.show.current_hunters_position(self.hunters, final=True)

        self.dracula.combat_cards.add([self.confronts_deck.take_first() for _ in range(5)])

        #Show dracula his cards in hand
        for card in  self.dracula.combat_cards.content:
            print(card)

        location = None

        while self.dracula.location not in dracula_available_spawn_locations:
            self.show.ask_player_to_choose_start_location(self.dracula)
            location = input()
            if location.isdigit():
                self.dracula.location = int(location)

        self.trail.add_new_trail_item(location, self.get_hunters_locations())
        self.phase = "day"

    def save_state(self, file_path):
        file_path = "saves/" + file_path + ".pkl"
        with open(file_path, 'wb') as file:
            pickle.dump(self, file)
        self.show.loadsave_report(file_path)

    def load_state(self, file_path, display):
        file_path = "saves/" + file_path + ".pkl"
        try:
            with open(file_path, 'rb') as file:
                engine = pickle.load(file)
                engine.show = display
            self.show.loadsave_report(file_path, load=True)
            return engine
        except FileNotFoundError:
            print("File doesn't exist!")
            return None

    def play_day(self):
        self.show.phrase("play_day")  #TODO: add day, week info
        self.show.phrase("wanna_save")
        answer = input()
        if answer != "":
            self.save_state(answer)

        self.hunters_act() #TODO: add condition of dracula event card with no hunter actions next day

        self.phase = "sunset"
        return

    def play_sunset(self):
        self.show.phrase("play_sunset")
        self.show.public_info(self)

        self.hunters_cards()
        self.fight_with_dracula_check()

        self.phase = "night"
        return

    def play_night(self):
        self.show.phrase("play_night")

        self.show.phrase("wanna_save")
        answer = input()
        if answer != "":
            self.save_state(answer)

        self.hunters_act()
        self.dracula_act() # TODO: add active effect for playing Dracula phase once again because of event card

        self.phase = "sunrise"
        return

    def play_sunrise(self):
        self.show.phrase("play_sunrise")
        self.show.public_info(self)

        self.hunters_cards()
        self.fight_with_dracula_check()

        print('Type "EXIT" to stop the game')
        if input() == "EXIT":
            self.phase = "end"
        else:
            self.phase = "day"
        return

    def move_by_road(self, player, distance=1):
        locations_available = self.map.get_locations_walk(player.location, distance)
        locations_full_info = list(map(self.map.find_by_id, locations_available))
        new_location = None

        while not new_location:
            self.show.available_move_locations(locations_full_info)
            new_location = input()
            if new_location == "CANCEL":
                return False
            if new_location.isdigit() and int(new_location) in locations_available:
                player.location = new_location
                # TODO: add trail check and the place for dracula reaction with event cards
                self.show.player_moved(player, self.map.find_by_id(player.location),
                                       self.map.find_by_id(new_location), "road")
                if self.trail.check_if_city_in_trail(new_location):
                    self.trail.disclose_city_in_trail(new_location)
                    print("City", new_location, "open in trail!") # TODO: at the position?
                    # TODO: if there are confront card at the city in trail, ask if it will be an ambush?
                # TODO: add trail update after each move of the hunter
                return True

    def move_by_railway(self, player):
        print("move_railway WIP")
        pass

    def move_by_sea(self, player, distance=1):
        locations_available = self.map.get_locations_sea(player.location, distance)
        locations_full_info = list(map(self.map.find_by_id, locations_available))
        new_location = None

        while not new_location:
            self.show.available_move_locations(locations_full_info)
            new_location = input()
            if new_location == "CANCEL":
                return False
            if new_location.isdigit() and int(new_location) in locations_available:
                player.location = new_location
                # TODO: add trail check and the place for dracula reaction with event cards
                self.show.player_moved(player, self.map.find_by_id(player.location),
                                       self.map.find_by_id(new_location), "sea")
                # TODO: add trail update after each move of the hunter
                return True

    @staticmethod
    def heal(hunter):
        #TODO: add request if wounds == 0, as player gonna skip the turn

        amount = 2 if hunter.player_class == "doc" else 1

        hunter.heal(amount)

        print("heal") # TODO: add proper notification of heal applied
        return True

    def search(self, player):
        # TODO: add usage of items
        card_disclosed, combat_card = self.trail.disclose_combat_card(player.location) # TODO: search disclose ALL confront cards at the city
        if card_disclosed:
            print("Card disclosed:", combat_card)
        result = self.try_to_clean_city(player, combat_card)

        if result:
            print("Card", combat_card, "cleaned successfully")
        else:
            print("Failure")
        return True

    def try_to_clean_city(self, player, card):
        print("City_clean_WIP")
        print("Will this hunter succeed at location cleaning?")
        result = None

        while result not in ["Y", "N"]:
            result = input('Enter "Y" if yes, and "N" if no \n').upper()

        if result == "Y":
            self.trail.clean_combat_card(player.location)
            return True
        else:
            return False

    def shop(self, player):
        night = self.phase == "night"
        extra_events = list()
        extra_items = list()

        if night:
            print("At night you will take the event card from below of the deck, and Dracula card will go to it's hand. Are you sure?")
            if input('Enter "Y" to confirm/n').upper() != "Y":
                return False

            card_taken = self.events_deck.take_last()

            if card_taken["for_dracula"]:
                extra_events.extend(self.dracula.get_event_card(card_taken))
                print("Dracula got an event card")

            else:
                extra_events.extend(player.get_event_card(card_taken))

        else:
            card_taken = self.events_deck.take_first()

            if card_taken["for_dracula"]:
                extra_events.append(card_taken)
                print("Dracula card goes to discard")

            else:
                extra_events.extend(player.get_event_card(card_taken))
                print("Event card added to player's inventory")

        items_amount = 2 if player.player_class == "lord" else 1

        if self.map.find_by_id(player.location)["big"]:

            extra_items.append(player.get_item_card(self.items_deck.take_first, items_amount))  # TODO: check how it works if lord takes two cards, but there is only one left
            print(items_amount, "item(s) added to player's inventory")

        self.events_discard.add(extra_events)
        self.items_discard.add(extra_items)

        return True

    def buy_tickets(self, player):
        stop = False
        second = False

        while not stop:
            if player.tickets.get_items_amount() >= 2: #TODO: change to "while", just in case
                for ticket in player.tickets.content:
                    print(ticket)

                print("choose which one to discard (specify it's ID):")
                ticket_id = input()
                self.tickets_discard.add([player.tickets.take_by_id(ticket_id)])
                print("Ticket with ID", ticket_id, "discarded")

            player.tickets.add([self.tickets_deck.take_first()])
            print("Ticket added to player's inventory")
            stop = True

            if player.player_class == "lord":
                if not second:
                    print('Would you like to buy another ticket? Enter "Y" if yes')

                    if input().upper() == "Y":
                        stop = False
                        second = True

        return True

    def use_card(self, player):
        print("use_card WIP")
        pass

    def trade(self, player):
        print("trade WIP")
        pass

    def special(self, player):
        print("special WIP")
        pass

    def hunters_cards(self):
        print("Moment for hunters to activate their event cards (sunrise/sunset) WIP") # TODO: add after adding event cards with corresponding use time
        pass

    def fight_with_dracula_check(self):
        if self.dracula.location in self.get_hunters_locations():
            print("Dracula gonna fight with some hunter(s)")


    def hunters_act(self):

        actions = {
            "move_by_road": lambda: self.move_by_road(hunter),
            "move_by_railway": lambda: self.move_by_railway(hunter),
            "move_by_sea": lambda: self.move_by_sea(hunter),
            "search": lambda: self.search(hunter),
            "heal": lambda: self.heal(hunter),
            "shop": lambda: self.shop(hunter),
            "buy_tickets": lambda: self.buy_tickets(hunter),
            "use_card": lambda: self.use_card(hunter),
            "trade": lambda: self.trade(hunter),
            "special": lambda: self.special(hunter),
        }

        # TODO: review after adding multiple hunter actions for day card

        if "custom_order" in self.active_effects:
            pass  # TODO: add after adding custom order active effect and event card
        else:
            for hunter in self.hunters:
                self.show.current_player(hunter)
                actions_available = self.check_actions_available(hunter)
                if actions_available.get("0") == "dead":
                    print(
                        "No action because the player is dead")  # TODO: add notification that player is dead and will be transported to the closest hospital
                    continue
                elif actions_available.get("0") == "sea":
                    print(
                        "No action because the player is located at sea at night")
                    continue
                elif actions_available.get("1") == "rise_up":
                    if hunter.knock_down:
                        print("The only available action for this player is to rise up")
                        hunter.hunter_rise_up()
                    continue  # May be different if we have more than one action for hunters at day
                # TODO: add check active effects (bats) applied to the player (and actions following)
                elif len(actions_available) == 0:
                    print("Turn skipped (no actions available, dunno why ¯\\_(ツ)_/¯)")
                    continue
                    # TODO: add public and private info output
                else:
                    result = None

                    while not result:
                        self.show.public_info(self)
                        self.show.private_info(hunter)
                        self.show.actions_available(actions_available)
                        action_chosen = input()
                        result = actions.get(actions_available.get(action_chosen), lambda: None)()

    def dracula_act(self):
        print("Dracula phase")
        print(self.show.public_info)
        for cell in self.trail.trail:
            print(cell, self.trail.trail[cell])

        self.show.current_hunters_position(self.hunters)
        for card in self.dracula.combat_cards.content:
            print(card)

        self.move_by_road(self.dracula) # TODO: add inability for Dracula to go to the city from trail again

        if self.dracula.location in self.get_hunters_locations():
            activation_card = self.trail.add_new_trail_item(self.dracula.location, self.get_hunters_locations())

        else:
            id_chosen = input("Specify ID of the card you want to place to your new location: \n")
            card_chosen = self.dracula.combat_cards.take_by_id(id_chosen)
            activation_card = self.trail.add_new_trail_item(self.dracula.location, self.get_hunters_locations(), card_chosen)

            if len(self.dracula.combat_cards.content) < 5:
                self.dracula.combat_cards.add([self.confronts_deck.take_first()])
                print("Dracula took card")

        if activation_card:
            self.card_apply_effect(activation_card)

        return

    def get_hunters_locations(self):
        return [hunter.location for hunter in self.hunters]

    def card_apply_effect(self, card):
        print("Card activation effect applied WIP")
        return
#  TODO: implement class for characters
#  TODO: unify confront/combat cards, check if fight/battle cards unified