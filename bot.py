import os
import telebot
from telebot import types
import random

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary of Players and their Points
players = {}

# Add Player Command
@bot.message_handler(commands=['addplayer'])
def add_player_command(message):
    player_name = message.text.split(' ', 1)[1]
    players[player_name] = 0
    bot.send_message(message.chat.id, f"Player '{player_name}' added.")

# Remove Player Command
@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    player_name = message.text.split(' ', 1)[1]
    if player_name in players:
        players.pop(player_name)
        bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
    else:
        bot.send_message(message.chat.id, f"Player '{player_name}' not found.")

# List Players Command
@bot.message_handler(commands=['listplayers'])
def list_players_command(message):
    if len(players) > 0:
        player_list = "\n".join([f"{name} - Points: {points}" for name, points in players.items()])
        bot.send_message(message.chat.id, f"List of Players:\n{player_list}")
    else:
        bot.send_message(message.chat.id, "No players found.")

# Assign Point Command
@bot.message_handler(commands=['addpoint'])
def assign_point_command(message):
    player_name = message.text.split(' ', 1)[1]
    if player_name in players:
        players[player_name] += 1
        bot.send_message(message.chat.id, f"Point added to player '{player_name}'.")
    else:
        bot.send_message(message.chat.id, f"Player '{player_name}' not found.")

# Remove Point Command
@bot.message_handler(commands=['removepoint'])
def remove_point_command(message):
    player_name = message.text.split(' ', 1)[1]
    if player_name in players:
        if players[player_name] > 0:
            players[player_name] -= 1
            bot.send_message(message.chat.id, f"Point removed from player '{player_name}'.")
        else:
            bot.send_message(message.chat.id, f"Player '{player_name}' has no points.")
    else:
        bot.send_message(message.chat.id, f"Player '{player_name}' not found.")

# Clear Points Command
@bot.message_handler(commands=['clearpoints'])
def clear_points_command(message):
    players.clear()
    bot.send_message(message.chat.id, "All points cleared. Starting a new game.")

# Whenever Starting Bot
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    # Generate Search Term Button
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    markup.add(button_generate)
    markup.add(button_list)

    markdown = f"""Hey *{message.chat.first_name}*, Welcome To *KR's Python Telegram Bot Template*.\n\nYou can use this template by visiting our template page from the buttons below."""
    
    bot.send_message(message.chat.id, markdown, parse_mode="Markdown", reply_markup=markup)
    print(f"Welcome Message Sent To {message.chat.first_name}\n")

# Handle button callback
@bot.callback_query_handler(func=lambda call: call.data == 'generate_search')
def generate_search_callback(call):
    # Handler for the "Generate Search Term" button callback
    search_term = generate_search_term()
    bot.send_message(call.message.chat.id, f"Generated Search Term: {search_term}")

# Handle button callback
@bot.callback_query_handler(func=lambda call: call.data == 'list_players')
def list_players_callback(call):
    # Handler for the "List Players" button callback
    if len(players) > 0:
        player_list = "\n".join([f"{name} - Points: {points}" for name, points in players.items()])
        bot.send_message(call.message.chat.id, f"List of Players:\n{player_list}")
    else:
        bot.send_message(call.message.chat.id, "No players found.")

print("Bot Started And Waiting For New Messages\n")

# Generate Search Term
def generate_search_term():
    search_term = ""
    wildcard_choices = ['wildcard', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
    other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']

    # Generate first character
    first_char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
    first_char = random.choice(first_char_options)
    if first_char == ' ':
        first_char = 'wildcard'
    search_term += first_char

    # Generate middle characters
    for _ in range(2):
        char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', 'other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

    # Generate last character
    last_char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
    last_char = random.choice(last_char_options)
    if last_char == ' ':
        last_char = 'wildcard'
    search_term += last_char

    if 'wildcard' in search_term:
        search_term += ' (Wildcard)'

    return search_term

print("Bot Started And Waiting For New Messages\n")

# Waiting For New Messages
bot.infinity_polling()
