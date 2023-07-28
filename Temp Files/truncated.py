import os
import telebot
from telebot import types
import random
from googleapiclient.discovery import build
import time
import re
from game import Game
from bot import Bot

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Create an instance of the Bot class
bot_instance = Bot(BOT_TOKEN)

########################################################
#GAME CLASS BELOW THIS LINE

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

# ... more code

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

# ... more code

    def reroll_superpower(self, index):
        # Check if the superpower has been used
        if self.superpowers_used[player_name]["reroll"]:
            return "You have already used the reroll superpower in this game."
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

    

# GAME CLASS ABOVE THIS LINE
########################################################
# BOT CLASS BELOW THIS LINE

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

# ... more code

    def add_player_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        msg = self.bot.send_message(call.message.chat.id, "Please enter the player's name.")
        self.bot.register_next_step_handler(msg, lambda message: game_session.add_player(message, self))

# ... more code

    def cancel_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.reset_game(self)
        self.bot.send_message(call.message.chat.id, "The game has been cancelled. You can start a new game whenever you're ready.")
        print("Game cancelled.")
        self.send_main_menu(call.message)
    

# ... more code

    def start_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.start_game(call.message, self)

    def start_turn(self, message):
        game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
        current_player, current_score = game_session.get_current_player_and_score()
        markup = types.InlineKeyboardMarkup()
        button_generate_term = types.InlineKeyboardButton("Generate Search Term", callback_data='generate')
        button_roll_character = types.InlineKeyboardButton("Roll Single Character", callback_data='roll')
        button_next_turn = types.InlineKeyboardButton("Skip to Next Turn", callback_data='next_turn')
        markup.row(button_generate_term, button_roll_character)
        markup.row(button_next_turn)
        self.bot.send_message(message.chat.id, f"It's {current_player}'s turn! Current score: {current_score}\n\nGenerate Term: Create a 4-character search term for YouTube.\nRoll Character: Randomly select a character for the search term.\nNext Turn: Pass your turn to the next player.", reply_markup=markup)

# ... more code

    def send_superpower_menu(self, message):
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons.
        button_use_superpower = types.InlineKeyboardButton("Use Superpower", callback_data='use_superpower')
        button_continue = types.InlineKeyboardButton("Continue", callback_data='continue')

        # Add buttons to the markup
        markup.row(button_use_superpower, button_continue)

        # Send the message with the markup
        self.bot.send_message(message.chat.id, "Would you like to use a superpower or continue?", reply_markup=markup)

    def continue_callback(self, call_or_message):
        # Check if the argument is a CallbackQuery or a Message
        if isinstance(call_or_message, types.CallbackQuery):
            call = call_or_message
            message = call.message
            game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        else:
            message = call_or_message
            game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
    
        # Send a message with the new search term
        self.bot.send_message(message.chat.id, f"New search term: {game_session.search_term}")
      
        # Execute the search_youtube function with the search term
        self.search_youtube(message, game_session.search_term)
    
        # Proceed to the next turn
        game_session.next_turn(message, self)

    def send_superpower_choice_menu(self, message):
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons.
        button_reroll = types.InlineKeyboardButton("Reroll", callback_data='reroll')
        button_replace = types.InlineKeyboardButton("Replace", callback_data='replace')
        button_swap = types.InlineKeyboardButton("Swap", callback_data='swap')
        button_continue = types.InlineKeyboardButton("Continue without Superpower", callback_data='continue')

        # Add buttons to the markup
        markup.row(button_reroll, button_replace, button_swap)
        markup.row(button_continue)

        # Define the superpowers explanation
        superpowers_explanation = """
        Superpowers:
        - Reroll: Generate a new search term.
        - Replace: Replace a character in the search term.
        - Swap: Swap two characters in the search term.
        """

        # Send the message with the markup
        self.bot.send_message(message.chat.id, superpowers_explanation + "Choose a superpower or continue without using one:", reply_markup=markup)

    def use_superpower_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        if game_session.check_superpower(call.from_user.id):
            self.send_superpowers_choice_menu(call.message)
        else:
            self.bot.send_message(call.message.chat.id, "You have already used all your superpowers.")

    def reroll_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons with the characters of the search term
        buttons = [types.InlineKeyboardButton(char, callback_data=f'reroll_{i}') for i, char in enumerate(game_session.search_term)]

        # Add buttons to the markup
        markup.row(*buttons)

        # Ask the user which character they want to replace
        self.bot.send_message(call.message.chat.id, "Which character do you want to replace?", reply_markup=markup)

    def replace_character(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Get the index of the character to replace
        index = int(call.data.split('_')[1])

        # Replace the character
        game_session.reroll_superpower(index)

        # Go to the next turn
        self.continue_callback(call)

    def replace_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons with the characters of the search term
        buttons = [types.InlineKeyboardButton(char, callback_data=f'replace_char_{i}') for i, char in enumerate(game_session.search_term)]

        # Add buttons to the markup
        markup.row(*buttons)

        # Ask the user which character they want to replace
        self.bot.send_message(call.message.chat.id, "Which character do you want to replace?", reply_markup=markup)

    def replace_character_with_input(self, call):
        # Get the index of the character to replace
        index = int(call.data.split('_')[2])

        # Store the index in the user data
        self.user_data[call.message.chat.id] = index

        # Ask the user to input a new character
        msg = self.bot.send_message(call.message.chat.id, "Please input a new character.")

        # Register the handle_character_input method as the next step handler
        self.bot.register_next_step_handler(msg, self.handle_character_input)

    def handle_character_input(self, message):
        game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
        # Get the index of the character to replace
        index = self.user_data[message.chat.id]

        # Replace the character with the user's input
        game_session.handle_character_input(index, message.text)

        # Remove the index from the user data
        del self.user_data[message.chat.id]

        # Go to the next turn
        self.continue_callback(message)

    def swap_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Create an instance of InlineKeyboardMarkup
        markup = types.InlineKeyboardMarkup()

        # Define the inline keyboard buttons with the characters of the search term
        buttons = [types.InlineKeyboardButton(char, callback_data=f'swap_{i}') for i, char in enumerate(game_session.search_term)]

        # Add buttons to the markup
        markup.row(*buttons)

        # Ask the user which character they want to swap
        self.bot.send_message(call.message.chat.id, "Select the first character to swap.", reply_markup=markup)

    def swap_character(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Get the index of the character to swap
        index = int(call.data.split('_')[1])

        # Check if this chat ID exists in the user data
        if call.message.chat.id not in self.user_data:
            self.user_data[call.message.chat.id] = {}

        # Check if this is the first or second character to swap
        if 'swap_index' in self.user_data[call.message.chat.id]:
            # This is the second character to swap
            index1 = self.user_data[call.message.chat.id]['swap_index']
            index2 = index

            # Swap the characters
            game_session.swap_characters(index1, index2)

            # Remove the swap index from the user data
            del self.user_data[call.message.chat.id]['swap_index']

            # If there are no more user data for this chat, remove the chat from the user data
            if not self.user_data[call.message.chat.id]:
                del self.user_data[call.message.chat.id]

            # Go to the next turn
            self.continue_callback(call)
        else:
            # This is the first character to swap
            # Store the index in the user data
            self.user_data[call.message.chat.id]['swap_index'] = index

            # Ask the user to select the second character to swap
            self.bot.send_message(call.message.chat.id, "Select the second character to swap.")
  
# BOT CLASS ABOVE THIS LINE
########################################################

########################################################

# Set up your command handlers here...
@bot_instance.bot.message_handler(commands=['start'])
def start_command(message):
    bot_instance.start_command(message)

########################################################

# Set up your callback handlers here...
bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'new_game')(bot_instance.new_game_callback)

# ... more code

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'add_player')
def add_player_callback(call):
    bot_instance.add_player_callback(call)

# ... mode code

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def start_game_callback(call):
    bot_instance.start_game_callback(call)

# ... more code

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'use_superpower')
def use_superpower_callback(call):
    bot_instance.use_superpower_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'reroll')
def reroll_superpower_callback(call):
    bot_instance.reroll_superpower(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data.startswith('reroll_'))
def replace_character_callback(call):
    bot_instance.replace_character(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'replace')
def replace_superpower_callback(call):
    bot_instance.replace_superpower(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data.startswith('replace_char_'))
def replace_character_with_input_callback(call):
    bot_instance.replace_character_with_input(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'swap')
def swap_superpower_callback(call):
    bot_instance.swap_superpower(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data.startswith('swap_'))
def swap_character_callback(call):
    bot_instance.swap_character(call)

########################################################

# Start polling for new messages
bot_instance.start_polling()
