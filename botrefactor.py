import os
import telebot
from telebot import types
import random


class Game:
    def __init__(self):
        # Dictionary to store players and their scores
        self.players = {}

        # List to store the order of players' turns
        self.turn_order = []

        # Index to keep track of the current player
        self.current_player_index = 0

        # Variable to keep track of the number of turns taken in the current round
        self.turns_taken = 0

        # Variable to store the current game phase
        self.phase = "No Game in Progress"

    def start_game(self):
        # Clear the players dictionary and turn order list
        self.players.clear()
        self.turn_order.clear()

        # Reset the current player index and turns taken
        self.current_player_index = 0
        self.turns_taken = 0

        # Set the game phase to "Game Setup"
        self.phase = "Game Setup"

    def add_player(self, player_name):
        # Add a player to the game if they are not already in it
        if player_name not in self.players:
            self.players[player_name] = 0
            return True
        else:
            return False

    def remove_player(self, player_name):
        # Remove a player from the game if they are in it
        if player_name in self.players:
            del self.players[player_name]
            return True
        else:
            return False

    def start_round(self):
        # Create the turn order for the round and shuffle it
        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)

        # Reset the current player index and turns taken
        self.current_player_index = 0
        self.turns_taken = 0

        # Set the game phase to "Game In Progress"
        self.phase = "Game In Progress"

    def next_turn(self):
        # Move to the next player's turn
        self.current_player_index += 1

        # If all players have had a turn, reset the current player index and set the game phase to "End of Round"
        if self.current_player_index >= len(self.turn_order):
            self.current_player_index = 0
            self.phase = "End of Round"

    def assign_point(self, player_name):
        # Assign a point to a player if they are in the game
        if player_name in self.players:
            self.players[player_name] += 1
            return True
        else:
            return False

    def remove_point(self, player_name):
        # Remove a point from a player if they are in the game and have at least one point
        if player_name in self.players and self.players[player_name] > 0:
            self.players[player_name] -= 1
            return True
        else:
            return False

    def end_game(self):
        # Set the game phase to "Game End"
        self.phase = "Game End"

class Bot:
    def __init__(self, token, game):
        self.bot = telebot.TeleBot(token)
        self.game = game
        self.commands = {
            'start': self.handle_start_game,
            'addplayer': self.handle_add_player,
            'removeplayer': self.handle_remove_player,
            # Add more commands here as needed
        }

    def start_bot(self):
        for command, handler in self.commands.items():
            self.bot.message_handler(commands=[command])(handler)
        self.bot.polling()

    # The rest of the methods go here

    def handle_start_game(self, message):
        """
        This method handles the /start command. It resets the game and sends the main menu.
        """
        self.game.reset()
        self.send_main_menu(message)

    def handle_add_player(self, message):
        """
        This method handles the /addplayer command. It adds a player to the game.
        """
        player_name = message.text
        if self.game.add_player(player_name):
            self.bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        else:
            self.bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")

    def handle_remove_player(self, message):
        """
        This method handles the /removeplayer command. It removes a player from the game.
        """
        player_name = message.text
        if self.game.remove_player(player_name):
            self.bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
        else:
            self.bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

    def handle_start_round(self, message):
        """
        This method handles the /startround command. It starts a new round of the game.
        """
        if len(self.game.players) == 0:
            self.bot.send_message(message.chat.id, "Error: No players in the game.")
        else:
            self.game.start_round()
            self.bot.send_message(message.chat.id, f"Round started. Turn order: {', '.join(self.game.turn_order)}")

    def handle_next_turn(self, message):
        """
        This method handles the /nextturn command. It advances the game to the next turn.
        """
        if self.game.phase != "Game In Progress":
            self.bot.send_message(message.chat.id, "Error: No round in progress.")
        else:
            self.game.next_turn()
            current_player = self.game.turn_order[self.game.current_player_index]
            self.bot.send_message(message.chat.id, f"It's {current_player}'s turn.")

    def handle_assign_point(self, message):
        """
        This method handles the /assignpoint command. It assigns a point to a player.
        """
        player_name = message.text
        if self.game.assign_point(player_name):
            self.bot.send_message(message.chat.id, f"Point assigned to '{player_name}'.")
        else:
            self.bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

    def handle_remove_point(self, message):
        """
        This method handles the /removepoint command. It removes a point from a player.
        """
        player_name = message.text
        if self.game.remove_point(player_name):
            self.bot.send_message(message.chat.id, f"Point removed from '{player_name}'.")
        else:
            self.bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found or has no points.")

    def handle_end_game(self, message):
        """
        This method handles the /endgame command. It ends the current game.
        """
        self.game.end_game()
        self.bot.send_message(message.chat.id, "The game has ended.")

    def handle_help(self, message):
        """
        This method handles the /help command. It sends the rules of the game.
        """
        rules = """
        1. Use /addplayer to add a player to the game.
        2. Use /removeplayer to remove a player from the game.
        3. Use /startround to start a new round. The turn order will be randomly determined.
        4. Use /nextturn to advance to the next turn.
        5. Use /assignpoint to assign a point to a player.
        6. Use /removepoint to remove a point from a player.
        7. Use /endgame to end the game.
        """
        self.bot.send_message(message.chat.id, rules)

    def handle_unknown(self, message):
        """
        This method handles any unknown commands. It sends an error message.
        """
        self.bot.send_message(message.chat.id, "Error: Unknown command.")

class SearchTermGenerator:
    def __init__(self):
        self.wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
        self.other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']

    def generate_search_term(self):
        search_term = ""

        # Generate first character
        char_options = self.wildcard_choices + ['other item']
        char = random.choice(char_options)
        if char == ' ':
            char = '<wildcard>'
        elif char == 'other item':
            char = random.choice(self.other_list_choices)
        search_term += char

        # Generate middle characters
        for _ in range(2):
            char_options = self.wildcard_choices + ['other item']
            char = random.choice(char_options)
            if char == 'other item':
                char = random.choice(self.other_list_choices)
            search_term += char

        # Generate last character
        char_options = self.wildcard_choices + ['other item']
        char = random.choice(char_options)
        if char == ' ':
            char = '<wildcard>'
        elif char == 'other item':
            char = random.choice(self.other_list_choices)
        search_term += char

        return search_term

    def roll_single_character(self):
        char_options = self.wildcard_choices + ['other item']
        char = random.choice(char_options)
        if char == ' ':
            char = '<wildcard>'
        elif char == 'other item':
            char = random.choice(self.other_list_choices)
        return char
