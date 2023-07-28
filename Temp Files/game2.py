import os
import telebot
from telebot import types
import random
from googleapiclient.discovery import build
import time
import re

class Game:
    def __init__(self):
        self.players = {}
        self.turn_order = []
        self.current_player_index = 0
        self.game_phase = "No Game in Progress"
        self.turns_taken = 0
        self.search_term = ""
        self.superpowers_used = {}

    def start_bot(self):
        self.players.clear()
        self.game_phase = "No Game in Progress"

    def start_new_game(self):
        self.players.clear()
        self.game_phase = "Game Setup"
        print("Starting game setup.")
        self.search_term = ""
        self.superpowers_used = {}

    def reset_game(self, bot_instance):
        self.players.clear()
        self.game_phase = "No Game in Progress"
        self.search_term = ""
        self.superpowers_used = {}

    def add_player(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
            bot_instance.send_player_submenu(message)  # Send the new submenu after attempting to add a player      
        else:
            self.players[player_name] = 0
            bot_instance.bot.send_message(message.chat.id, f"Player '{player_name}' added.")
            self.superpowers_used[player_name] = {"reroll": False, "replace": False, "swap": False}
            print(f"Player added: {player_name}")
            bot_instance.send_player_submenu(message)  # Send the new submenu after adding a player

    def remove_player(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players:
            del self.players[player_name]
            del self.superpowers[player_name]
            bot_instance.bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
            print(f"Player removed: {player_name}")
            bot_instance.send_player_submenu(message)  # Send the new submenu after removing a player
        else:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")
            bot_instance.send_player_submenu(message)  # Send the new submenu after removing a player

    def start_game(self, message, bot_instance):
        # Check if there are enough players to start the game
        if len(self.players) < 2:
            bot_instance.bot.send_message(message.chat.id, "Error: At least 2 players are required to start the game.")
            return
    
        # Initialize turn order
        self.turn_order = list(self.players.keys())
        random.shuffle(self.turn_order)
    
        # Initialize current player index
        self.current_player_index = 0
    
        # Create a new ReplyKeyboardMarkup object. This will be the custom keyboard.
        player_keyboard = types.ReplyKeyboardMarkup(row_width=2)
    
        # Create a list of KeyboardButton objects, one for each player in the game.
        player_buttons = [types.KeyboardButton(player) for player in self.players]
    
        # Add all of the player buttons to the markup using the add method.
        player_keyboard.add(*player_buttons)
    
        # Transition to the "Game In Progress" phase
        self.game_phase = "Game In Progress"
        print("Game Started")
        bot_instance.bot.send_message(message.chat.id, "The game has started!", reply_markup=player_keyboard)
    
        # Announce the first player's turn and send the turn menu
        bot_instance.start_turn(message)

    def get_current_player_and_score(self):
        current_player = self.turn_order[self.current_player_index]
        current_score = self.players[current_player]
        return current_player, current_score
    
    def next_turn(self, message, bot_instance):
        # Increment the index of the current player (wrapping around to the start of the list if necessary)
        self.current_player_index = (self.current_player_index + 1) % len(self.turn_order)
        # Increment the number of turns taken
        self.turns_taken += 1
        # Check if the round is over
        if self.turns_taken == len(self.turn_order):
            # Reset the number of turns taken
            self.turns_taken = 0
            # Send the end of round menu
            bot_instance.send_end_of_round_menu(message)
        else:
            # Start the next turn
            bot_instance.start_turn(message)

    def next_round(self, message, bot_instance):
        # Reset the current player index
        self.current_player_index = 0
        # Show the leaderboard
        bot_instance.show_leaderboard(message)
        # Start the next round
        bot_instance.start_turn(message)

    def assign_point_name(self, message, bot_instance):
        if message.text in self.players:
            self.players[message.text] += 1
            bot_instance.bot.send_message(message.chat.id, f"Point assigned to player: {message.text}")
            print(f"Point added to: {message.text}")
            if self.players[message.text] == 3:
                # Transition to the "Game End" phase
                self.game_phase = "Game End"
                bot_instance.bot.send_message(message.chat.id, f"Player '{message.text}' has won the game with 3 points!")
                # Display the final leaderboard
                bot_instance.show_leaderboard(message)
            else:
                # Send the submenu for assigning or removing points or going to the next round
                bot_instance.send_point_submenu(message)
        else:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{message.text}' does not exist.")
            # Send the submenu for assigning or removing points or going to the next round
            bot_instance.send_point_submenu(message)

    def remove_point_name(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players and self.players[player_name] > 0:
            self.players[player_name] -= 1
            bot_instance.bot.send_message(message.chat.id, f"Point removed from player: {player_name}")
            print(f"Point removed from: {message.text}")
            # Send the submenu for assigning or removing points or going to the next round
            bot_instance.send_point_submenu(message)
        else:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' either does not exist or has no points to remove.")
            # Send the submenu for assigning or removing points or going to the next round
            bot_instance.send_point_submenu(message)

    def get_leaderboard(self):
        # Sort the players by points in descending order
        sorted_players = sorted(self.players.items(), key=lambda x: x[1], reverse=True)
        # Format the leaderboard as a string
        leaderboard = "\n".join(f"{name}: {points}" for name, points in sorted_players)
        return leaderboard

    def end_game(self, message, bot_instance):
        # Find the player(s) with the highest score
        max_score = max(self.players.values())
        winners = [player for player, score in self.players.items() if score == max_score]

        # Prepare the end game message
        if len(winners) == 1:
            winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 *{winners[0]}* is the *WINNER* of the game with *{max_score}* points! 🏆\n\nThanks for playing! Ready for another round?"
        else:
            winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 We have a tie! *{' and '.join(winners)}* are the *WINNERS* of the game with *{max_score}* points each! 🏆\n\nThanks for playing! Ready for another round?"

        # Send the end game message
        print(f"{winner_message}")
        bot_instance.bot.send_message(message.chat.id, winner_message, parse_mode='Markdown')

        # Reset the game
        self.reset_game(bot_instance)
        bot_instance.send_main_menu(message)

    def generate_search_term(self):
        search_term = ""
        wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', 'other item']
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
        first_last_choice = wildcard_choices
        first_last_choice.remove(' ')
      
        # Generate first character
        char = random.choice(first_last_choice)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

        # Generate middle characters
        for _ in range(2):
            char = random.choice(wildcard_choices)
            if char == 'other item':
                char = random.choice(other_list_choices)
            search_term += char

        # Generate last character
        char = random.choice(first_last_choice)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char
        self.search_term = search_term
        print(f"Search term generated: {search_term}")
      
        return search_term

    def generate_single_character(self):
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
        char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        return char

    def reroll_superpower(self, player_name, index):
        # Mark the superpower as used
        self.superpowers_used[player_name]["reroll"] = True
        # Replace the character
        char = self.generate_single_character()
        self.search_term = self.search_term[:index] + char + self.search_term[index+1:]

    def replace_character(self, old_char, new_char):
        # Replace the old character with the new character in the search term
        self.search_term = self.search_term.replace(old_char, new_char, 1)
        print(f"new search term: {search_term}")

    def replace_character_with_input(self, index, new_char):
        # Replace the character with the user's input
        self.search_term = self.search_term[:index] + new_char + self.search_term[index+1:]

    def handle_character_input(self, index, new_char):
        # Replace the character with the user's input
        self.replace_character_with_input(index, new_char)

    def swap_characters(self, index1, index2):
        # Swap the characters
        chars = list(self.search_term)
        chars[index1], chars[index2] = chars[index2], chars[index1]
        self.search_term = ''.join(chars)

    
