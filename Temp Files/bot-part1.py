from game import Game
import os
import telebot
from telebot import types
import random
from googleapiclient.discovery import build
import time
import re

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)

class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.game_session = {}  # Store a Game instance for each user
        self.player_keyboard = types.ReplyKeyboardRemove()
        self.user_data = {}

    def get_game_session(self, user_id):
        # Get the Game instance for the given user ID, creating a new one if necessary
        if user_id not in self.game_session:
            self.game_session[user_id] = Game()
            print("New game session created")
        return self.game_session[user_id]
      
    def start_command(self, message):
        game_session = self.get_game_session(message.chat.id)
        game_session.start_bot()
        print(f'Start command received in chat {message.chat.id}')
        self.send_main_menu(message)

    def send_main_menu(self, message):
        game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons.
        button_rules = types.InlineKeyboardButton("Detailed Rules", callback_data='show_rules')

        if game_session.game_phase == "No Game in Progress" or game_session.game_phase == "Game End":
            button_new_game = types.InlineKeyboardButton("Start New Game", callback_data='new_game')

            # Add buttons to the markup
            markup.row(button_new_game)
            markup.row(button_rules)

            # Explanation of the game and the buttons
            explanation_text = """
Welcome to YouTube Roulette! 🎉

Compete with your friends to find the most entertaining YouTube video based on a randomly generated search term. The player whose video gets the most votes wins a point. First to 3 points wins the game! 🏆

Use your three "Superpowers" wisely: reroll a character, replace a character, or swap two characters in the search term.
"""
            start_text = """
Ready to start? Click 'Start New Game' below! For a detailed explanation of the rules, click 'Detailed Rules'.
"""

            # Send the message with the markup
            self.bot.send_message(message.chat.id, explanation_text, reply_markup=self.player_keyboard)
            self.bot.send_message(message.chat.id, start_text, reply_markup=markup)

        # Explanation of the game setup phase
        elif game_session.game_phase == "Game Setup":
            button_add_player = types.InlineKeyboardButton("Add Player", callback_data='add_player')
            button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
            button_start_game = types.InlineKeyboardButton("Start Game", callback_data='start_game')
            button_cancel_game = types.InlineKeyboardButton("Cancel Game", callback_data='cancel_game')
            button_rules = types.InlineKeyboardButton("Show Rules", callback_data='show_rules')
        
            markup.row(button_add_player, button_remove_player)
            markup.row(button_start_game, button_cancel_game, button_rules)
        
            # Explanation of the buttons
            setup_text = """
Game Setup 🎮

Add players using the 'Add Player' button. You need at least two players to start the game. 

Once all players are added, click 'Start Game' to begin the YouTube Roulette! 

Need to remove a player? Use the 'Remove Player' button. 

For a detailed explanation of the rules, click 'Detailed Rules'.
"""

            self.bot.send_message(message.chat.id, setup_text, reply_markup=markup)

        # Explanation of the game in progress phase
        elif game_session.game_phase == "Game In Progress":
            button_generate_term = types.InlineKeyboardButton("Generate Term", callback_data='generate')
            button_roll_character = types.InlineKeyboardButton("Roll Character", callback_data='roll')
            button_assign_point = types.InlineKeyboardButton("Assign Point", callback_data='assign_point')
            button_remove_point = types.InlineKeyboardButton("Remove Point", callback_data='remove_point')
            button_end_game = types.InlineKeyboardButton("End Game", callback_data='end_game')
            button_show_rules = types.InlineKeyboardButton("Show Rules", callback_data='show_rules')
            button_show_leaderboard = types.InlineKeyboardButton("Show Leaderboard", callback_data='show_leaderboard')
        
            markup.row(button_assign_point, button_remove_point)
            markup.row(button_generate_term, button_roll_character)
            markup.row(button_end_game, button_show_rules, button_show_leaderboard)
        
            # Explanation of the buttons
            explanation_text = """
    Game In Progress! Let's roll:
    - "Assign Point": Give a point to a player. You'll need to enter the player's name.
    - "Remove Point": Take a point from a player. Again, you'll need to enter the player's name.
    - "Generate Term": Generate a random 4-character search term for the current player's turn.
    - "Roll Character": Generate a random character. This can be used for the superpowers.
    - "End Game": Stop the game and display the final scores. Use this when you're ready to wrap up.
    - "Show Rules": Need a refresher on the rules? Click here!
    - "Show Leaderboard": Check out the current standings in the game.
    """

            self.bot.send_message(message.chat.id, explanation_text, reply_markup=markup)
        
    def start_polling(self):
        self.bot.infinity_polling()

    @bot.callback_query_handler(func=lambda call: call.data == 'new_game')
    def new_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.start_new_game()
        self.send_main_menu(call.message)

    def rules(self, call):
        self.bot.send_message(call.message.chat.id, """
        Welcome to YouTube Roulette! Here's a detailed explanation of the rules:

        1️⃣ Each player's turn, they will randomly generate a 4-character search term using the 'Generate Term' button.
        2️⃣ The player will then search YouTube using this term and choose one of the first three videos that appear. Note that channels, playlists, and songs without a timestamp are considered wildcards and don't count as one of the three choices, though they may be chosen. If a playlist is chosen, you must play the FIRST video.
        3️⃣ The group must watch at least one full minute of the video (unless it is under one minute, in which case they must watch the whole video). After that time, players may begin "thumbs downing" a video by holding up their hand, and once a majority of players have thumbs downed, the game leader will exit the video.
        4️⃣ After everyone has taken a turn and chosen a video, the group will vote on which person's video they thought was the best. The person whose video gets the most votes gets a point.
        5️⃣ The first player to get 3 points wins the game. 🏆

        Special Rules:
        Each player also has three "Superpowers" they can use once per game:
        - Reroll a single character: If you don't like one of the characters in your search term, you can reroll it to get a new random character.
        - Replace a character with a character of their choosing: If you have a specific character you want in your search term, you can replace one of the existing characters with it.
        - Swap two characters in the search term: If you think your search term would be better with two characters swapped, you can do that too!

        Use your superpowers wisely and have fun!
        """)

    def show_rules_callback(self, call):
        self.rules(call)

    def add_player_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        msg = self.bot.send_message(call.message.chat.id, "Please enter the player's name.")
        self.bot.register_next_step_handler(msg, lambda message: game_session.add_player(message, self))

    def remove_player_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        msg = self.bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
        self.bot.register_next_step_handler(msg, lambda message: game_session.remove_player(message, self))
