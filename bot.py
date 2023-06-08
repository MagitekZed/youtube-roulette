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

# Main Menu 
@bot.message_handler(commands=['menu'])
def send_main_menu(message):
    markup = types.InlineKeyboardMarkup()

    button_new_game = types.InlineKeyboardButton("Start New Game", callback_data='new_game')
    button_show_rules = types.InlineKeyboardButton("Show Rules", callback_data='show_rules')
    button_add_player = types.InlineKeyboardButton("Add Player", callback_data='add_player')
    button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
    button_help = types.InlineKeyboardButton("Help", callback_data='help')

    markup.row(button_new_game, button_show_rules)
    markup.row(button_add_player, button_remove_player)
    markup.row(button_help)

    bot.send_message(message.chat.id, "Main Menu:", reply_markup=markup)

# Callback for the "Start New Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'new_game')
def new_game_callback(call):
    # Call the function that handles the /newgame command
    new_game_command(call.message)

# Callback for the "Show Rules" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def show_rules_callback(call):
    # Call the function that handles the /rules command
    rules_command(call.message)

# Callback for the "Add Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'add_player')
def add_player_callback(call):
    # Call the function that handles the /addplayer command
    add_player_command(call.message)

# Callback for the "Remove Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    # Call the function that handles the /removeplayer command
    remove_player_command(call.message)

# Callback for the "Help" button
@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    # Call the function that handles the /help command
    help_command(call.message)

# Command to add a player to the game
@bot.message_handler(commands=['addplayer'])
def add_player_command(message):
    # Send a message asking for the player's name
    msg = bot.send_message(message.chat.id, "Please enter the player's name.")
    # Register a listener for the next message from this user
    bot.register_next_step_handler(msg, add_player_name)

def add_player_name(message):
    player_name = message.text
    if player_name in players:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
    else:
        players[player_name] = 0
        bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        print(f"Player '{player_name}' added.")

# Command to remove a player from the game
@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    # Send a message asking for the player's name
    msg = bot.send_message(message.chat.id, "Please enter the name of the player to remove.")
    # Register a listener for the next message from this user
    bot.register_next_step_handler(msg, remove_player_name)

def remove_player_name(message):
    player_name = message.text
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
    button_reroll = types.InlineKeyboardButton("Reroll Character", callback_data='reroll')
    markup.add(button_generate)
    markup.add(button_list)
    markup.add(button_reroll)

    help_text = """
Here are the commands you can use:

/start: Start the game and display the rules.
/commands: Show the available command buttons.
/addplayer <name>: Add a player to the game.
/removeplayer <name>: Remove a player from the game.
/listplayers: List all the players currently in the game, along with their scores.
/addpoint <name>: Assign a point to a player.
/removepoint <name>: Remove a point from a player.
/clearpoints: Clear all the points.
/newgame: Clear all the points and players, starting a new game.
/generate: Generate a new random character string.
/reroll: Generate a single character for the "reroll" superpower. 
/rules: Display the rules of the game.
/help: Display this help message.

You can also use the buttons below to generate a search term and list the players.
"""
    bot.send_message(message.chat.id, help_text, reply_markup=markup)

# Runs on /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Generate Command Buttons
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    button_reroll = types.InlineKeyboardButton("Reroll Character", callback_data='reroll')
    markup.add(button_generate)
    markup.add(button_list)
    markup.add(button_reroll)

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
    print(f"Welcome Message Sent To {message.chat.first_name}")

# Show the Buttons
@bot.message_handler(commands=['commands'])
def show_buttons(message):
    # Generate Command Buttons
    markup = types.InlineKeyboardMarkup()
    button_generate = types.InlineKeyboardButton("Generate Search Term", callback_data='generate_search')
    button_list = types.InlineKeyboardButton("List Players", callback_data='list_players')
    button_reroll = types.InlineKeyboardButton("Reroll Character", callback_data='reroll')
    markup.add(button_generate)
    markup.add(button_list)
    markup.add(button_reroll)

    bot.send_message(message.chat.id, "Here are the available command buttons:", reply_markup=markup)

# display the rules
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
    first_char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
    first_char = random.choice(first_char_options)
    if first_char == ' ':
        first_char = 'wildcard'
    elif first_char == 'other item':
        first_char = random.choice(other_list_choices)
    search_term += first_char

    # Generate middle characters
    for _ in range(2):
        char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

    # Generate last character
    last_char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
    last_char = random.choice(last_char_options)
    if last_char == ' ':
        last_char = 'wildcard'
    elif last_char == 'other item':
        last_char = random.choice(other_list_choices)
    search_term += last_char
    
    return search_term

# Generate Single Character
def generate_single_character():
    other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
    char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', 'other item']
    char = random.choice(char_options)
    if char == 'other item':
        char = random.choice(other_list_choices)
    return char

# Handle button callback
@bot.callback_query_handler(func=lambda call: call.data == 'reroll')
def reroll_callback(call):
    # Handler for the "Reroll Character" button callback
    char = generate_single_character()
    bot.send_message(call.message.chat.id, f"Rerolled Character: {char}")
    print(f"Rerolled Character: {char}")

# Command to generate a new single character
@bot.message_handler(commands=['reroll'])
def reroll_command(message):
    char = generate_single_character()
    bot.send_message(message.chat.id, f"Rerolled Character: {char}")
    print(f"Rerolled Character: {char}")

# Handle button callback
@bot.callback_query_handler(func=lambda call: call.data == 'generate_search')
def generate_search_callback(call):
    # Handler for the "Generate Search Term" button callback
    search_term = generate_search_term()
    bot.send_message(call.message.chat.id, f"Generated Search Term: {search_term}")
    print(f"Generated Search Term: {search_term}")

# Command to generate a new search term
@bot.message_handler(commands=['generate'])
def generate_term_command(message):
    search_term = generate_search_term()
    bot.send_message(message.chat.id, f"Generated Search Term: {search_term}")
    print(f"Generated Search Term: {search_term}")

# Waiting For New Messages
bot.infinity_polling()
