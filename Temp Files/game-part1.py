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
        self.superpowers = {}

    def start_bot(self):
        self.players.clear()
        self.game_phase = "No Game in Progress"

    def start_new_game(self):
        self.players.clear()
        self.game_phase = "Game Setup"
        print("Starting game setup.")
        self.search_term = ""
        self.superpowers = {}

    def reset_game(self, bot_instance):
        self.players.clear()
        self.game_phase = "No Game in Progress"
        self.search_term = ""
        self.superpowers = {}

    def add_player(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
            bot_instance.send_player_submenu(message)  # Send the new submenu after attempting to add a player      
        else:
            self.players[player_name] = 0
            bot_instance.bot.send_message(message.chat.id, f"Player '{player_name}' added.")
            self.superpowers[player_name] = {"reroll": False, "replace": False, "swap": False}
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
