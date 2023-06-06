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

@bot.message_handler(commands=['addplayer'])
def add_player_command(message):
    try:
        player_name = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "Error: No player name provided. Use /addplayer <name>.")
        return
    if player_name in players:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
    else:
        players[player_name] = 0
        bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        print(f"Player '{player_name}' added.")

@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    try:
        player_name = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "Error: No player name provided. Use /removeplayer <name>.")
        return
    if player_name in players:
        del players[player_name]
        bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
        print(f"Player '{player_name}' removed.")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

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
    try:
        player_name = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "Error: No player name provided. Use /addpoint <name>.")
        return
    if player_name in players:
        players[player_name] += 1
        bot.send_message(message.chat.id, f"Point added to player '{player_name}'.")
        print(f"Point added to player '{player_name}'.")
        if players[player_name] == 3:
            bot.send_message(message.chat.id, f"Player '{player_name}' has won the game with 3 points!")
            # Sort players by points
            sorted_players = sorted(players.items(), key=lambda item: item[1], reverse=True)
            # Generate ranking message
            ranking_message = "Here are the final rankings:\n"
            for i, (name, points) in enumerate(sorted_players, start=1):
                ranking_message += f"{i}. {name} - {points} points\n"
            bot.send_message(message.chat.id, ranking_message)
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

# Remove Point Command
@bot.message_handler(commands=['removepoint'])
def remove_point_command(message):
    try:
        player_name = message.text.split(' ', 1)[1]
    except IndexError:
        bot.send_message(message.chat.id, "Error: No player name provided. Use /removepoint <name>.")
        return
    if player_name in players:
        if players[player_name] > 0:
            players[player_name] -= 1
            bot.send_message(message.chat.id, f"Point removed from player '{player_name}'.")
            print(f"Point removed from player '{player_name}'.")
        else:
            bot.send_message(message.chat.id, f"Error: Player '{player_name}' has no points.")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

# Clear Points Command
@bot.message_handler(commands=['clearpoints'])
def clear_points_command(message):
    for player in players:
        players[player] = 0
    bot.send_message(message.chat.id, "All points cleared.")
    print("All points cleared.")

# New Game Start
@bot.message_handler(commands=['newgame'])
def new_game_command(message):
    players.clear()
    bot.send_message(message.chat.id, "All points and players cleared. Starting a new game.")
    print("All points and players cleared. Starting a new game.")

# Help shows all available commands
@bot.message_handler(commands=['help'])
def help_command(message):
    # Generate Command Buttons
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    markup.add(button_generate)
    markup.add(button_list)

    help_text = """
Here are the commands you can use:

/start: Start the game and display the rules.
/commands: Show the available command buttons.
/addplayer <name>: Add a player to the game.
/removeplayer <name>: Remove a player from the game.
/listplayers: List all the players currently in the game, along with their scores.
/addpoint <name>: Assign a point to a player.
/removepoint <name>: Remove a point from a player.
/clearpoints: Clear all the points and start a new game.
/rules: Display the rules of the game.
/help: Display this help message.

You can also use the buttons below to generate a search term and list the players.
"""
    bot.send_message(message.chat.id, help_text, reply_markup=markup)

# Runs on /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Generate Search Term Button
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    markup.add(button_generate)
    markup.add(button_list)

    welcome_text = f"""
Hey *{message.chat.first_name}*, Welcome To YouTube Roulette!

Here's a quick explanation of the rules:
1. Each player's turn, they will randomly generate a 4-character search term.
2. They will have to choose one of the first three videos on YouTube using this search term. Channels must be skipped and playlists and songs without a timestamp are considered wildcards and don't count as one of the three choices, though they may be chosen. If a playlist is chosen, you must play the FIRST video. 
3. The group must watch at least one full minute of the video (unless it is under one minute, in which case they must watch the whole video). After that time, players may begin "thumbs downing" a video by holding up their hand, and once a majority of players have thumbs downed, the game leader will exit the video.
4. The person with the most votes gets a point.
5. The first player to get 3 points wins the game.

Special Rules:
Each player has three "Superpowers" they can use ONCE PER GAME:
1. Reroll a single character.
2. Replace a character with a character of their choosing.
3. Swap two characters in the search term.

You can use the buttons below to generate a search term and list the players.
"""
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)
    print(f"Welcome Message Sent To {message.chat.first_name}\n")

# Show the Buttons
@bot.message_handler(commands=['commands'])
def show_buttons(message):
    # Generate Search Term Button
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    markup.add(button_generate)
    markup.add(button_list)

    bot.send_message(message.chat.id, "Here are the available command buttons:", reply_markup=markup)

@bot.message_handler(commands=['rules'])
def rules_command(message):
    rules_text = """
Here's a quick explanation of the rules:
1. Each player's turn, they will randomly generate a 4-character search term.
2. They will have to choose one of the first three videos on YouTube using this search term. Channels must be skipped and playlists and songs without a timestamp are considered wildcards and don't count as one of the three choices, though they may be chosen. If a playlist is chosen, you must play the FIRST video. 
3. The group must watch at least one full minute of the video (unless it is under one minute, in which case they must watch the whole video). After that time, players may begin "thumbs downing" a video by holding up their hand, and once a majority of players have thumbs downed, the game leader will exit the video.
4. The person with the most votes gets a point.
5. The first player to get 3 points wins the game.

Special Rules:
Each player has three "Superpowers" they can use ONCE PER GAME:
1. Reroll a single character.
2. Replace a character with a character of their choosing.
3. Swap two characters in the search term.
"""
    bot.send_message(message.chat.id, rules_text)


# Handle button callback
@bot.callback_query_handler(func=lambda call: call.data == 'generate_search')
def generate_search_callback(call):
    # Handler for the "Generate Search Term" button callback
    search_term = generate_search_term()
    bot.send_message(call.message.chat.id, f"Generated Search Term: {search_term}")
    print(f"Generated Search Term: {search_term}")

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
