import os
import telebot
from telebot import types
import random

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)

class Game:
    def __init__(self):
        self.players = {}
        self.game_phase = "No Game in Progress"

    def start_bot(self):
        self.players.clear()
        self.game_phase = "No Game in Progress"

    def start_new_game(self):
        self.players.clear()
        self.game_phase = "Game Setup"
        print("Starting game setup.")

class Bot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.game = Game()
        self.player_keyboard = types.ReplyKeyboardRemove()

    def start_command(self, message):
        self.game.start_bot()
        self.send_main_menu(message)

    def send_main_menu(self, message):
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons.
        button_rules = types.InlineKeyboardButton("Detailed Rules", callback_data='show_rules')

        if self.game.game_phase == "No Game in Progress" or self.game.game_phase == "Game End":
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
        elif self.game.game_phase == "Game Setup":
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
        elif self.game.game_phase == "Game In Progress":
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
        self.game.start_new_game()
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

# Create an instance of the Bot class
bot_instance = Bot(BOT_TOKEN)


# Set up your command handlers here...
@bot_instance.bot.message_handler(commands=['start'])
def start_command(message):
    bot_instance.start_command(message)


# Set up your callback handlers here...
bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'new_game')(bot_instance.new_game_callback)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def show_rules_callback(call):
    bot_instance.show_rules_callback(call)


# Start polling for new messages
bot_instance.start_polling()
