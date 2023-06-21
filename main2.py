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



# GAME CLASS ABOVE THIS LINE
########################################################
# BOT CLASS BELOW THIS LINE


  
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

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def show_rules_callback(call):
    bot_instance.show_rules_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'cancel_game')
def cancel_game_callback(call):
    bot_instance.cancel_game_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'add_player')
def add_player_callback(call):
    bot_instance.add_player_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    bot_instance.remove_player_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def start_game_callback(call):
    bot_instance.start_game_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'next_turn')
def next_turn_callback(call):
    bot_instance.next_turn_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'next_round')
def next_round_callback(call):
    bot_instance.next_round_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'assign_point')
def assign_point_callback(call):
    bot_instance.assign_point_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'remove_point')
def remove_point_callback(call):
    bot_instance.remove_point_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'show_leaderboard')
def show_leaderboard_callback(call):
    bot_instance.show_leaderboard_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'end_game')
def end_game_callback(call):
    bot_instance.end_game_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'generate')
def generate_term_callback(call):
    bot_instance.generate_term_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'roll')
def roll_character_callback(call):
    bot_instance.roll_character_callback(call)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'continue')
def continue_callback(call):
    bot_instance.continue_callback(call)

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
