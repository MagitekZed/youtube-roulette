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

# Global variable to store the current game phase
game_phase = "No Game in Progress"

# Main Menu 
@bot.message_handler(commands=['menu'])
def send_main_menu(message):
    markup = types.InlineKeyboardMarkup()

    if game_phase == "No Game in Progress":
        button_new_game = types.InlineKeyboardButton("Start New Game", callback_data='new_game')
        button_help = types.InlineKeyboardButton("Help", callback_data='help')

        markup.row(button_new_game)
        markup.row(button_help)

        # Explanation of the game and the buttons
        explanation_text = """
        Welcome to YouTube Roulette! In this game, players take turns generating random search terms and choosing a video to watch based on these terms. The player whose video gets the most votes wins a point. The first player to get 3 points wins the game!
    
        Here's what the buttons do:
        - "Start New Game": Clears all points and players and starts a new game.
        - "Help": Shows all available commands.
        """
    
        bot.send_message(message.chat.id, explanation_text, reply_markup=markup)

    # Explanation of the game setup phase
    elif game_phase == "Game Setup":
        button_add_player = types.InlineKeyboardButton("Add Player", callback_data='add_player')
        button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
        button_start_game = types.InlineKeyboardButton("Start Game", callback_data='start_game')
        button_cancel_game = types.InlineKeyboardButton("Cancel Game", callback_data='cancel_game')

        markup.row(button_add_player, button_remove_player)
        markup.row(button_start_game, button_cancel_game)

        # Explanation of the buttons
        explanation_text = """
        Game Setup Phase:
        - "Add Player": Adds a new player to the game. You will be prompted to enter the player's name.
        - "Remove Player": Removes a player from the game. You will be prompted to enter the player's name.
        - "Start Game": Starts the game with the current players.
        - "Cancel Game": Cancels the game setup and returns to the initial state.
        """

        bot.send_message(message.chat.id, explanation_text, reply_markup=markup)

# Function to start a new game
def start_new_game(message):
    players.clear()
    bot.send_message(message.chat.id, "All points and players cleared. You can now add players.")
    print("All points and players cleared. Starting game setup.")

# Register this function as a message handler for the /newgame command
@bot.message_handler(commands=['newgame'])
def new_game_command(message):
    start_new_game(message)

# Callback for the "Start New Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'new_game')
def new_game_callback(call):
    # Call the function that handles the /newgame command
    start_new_game(call.message)
    # Transition to the "Game Setup" phase
    global game_phase
    game_phase = "Game Setup"
    bot.send_message(call.message.chat.id, "The game setup phase has started! Use the menu to add players.")

# Function to show the rules
def show_rules(message):
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

# Register this function as a message handler for the /rules command
@bot.message_handler(commands=['rules'])
def rules_command(message):
    show_rules(message)

# Call this function from the callback function for the "Show Rules" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def show_rules_callback(call):
    show_rules(call.message)

# Callback for the "Start Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def start_game_callback(call):
    # Check if there are enough players to start the game
    if len(players) < 2:
        bot.send_message(call.message.chat.id, "Error: At least 2 players are required to start the game.")
    else:
        # Transition to the "Game In Progress" phase
        global game_phase
        game_phase = "Game In Progress"
        bot.send_message(call.message.chat.id, "The game has started!")

# Callback for the "Cancel Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_game')
def cancel_game_callback(call):
    # Clear the list of players
    players.clear()
    # Transition back to the "No Game in Progress" phase
    global game_phase
    game_phase = "No Game in Progress"
    bot.send_message(call.message.chat.id, "The game setup has been canceled.")

# Function to add a player
def add_player(message):
    player_name = message.text
    if player_name in players:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
    else:
        players[player_name] = 0
        bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        print(f"Player '{player_name}' added.")

# Register this function as a message handler for the /addplayer command
@bot.message_handler(commands=['addplayer'])
def add_player_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_player)

# Call this function from the callback function for the "Add Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'add_player')
def add_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_player)

# Function to remove a player
def remove_player(message):
    player_name = message.text
    if player_name in players:
        del players[player_name]
        bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
        print(f"Player '{player_name}' removed.")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

# Register this function as a message handler for the /removeplayer command
@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Call this function from the callback function for the "Remove Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Function to add a player
def add_player(message):
    player_name = message.text
    if player_name in players:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
    else:
        players[player_name] = 0
        bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        print(f"Player '{player_name}' added.")

# Register this function as a message handler for the /addplayer command
@bot.message_handler(commands=['addplayer'])
def add_player_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_player)

# Call this function from the callback function for the "Add Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'add_player')
def add_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_player)

# Function to remove a player
def remove_player(message):
    player_name = message.text
    if player_name in players:
        del players[player_name]
        bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
        print(f"Player '{player_name}' removed.")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

# Register this function as a message handler for the /removeplayer command
@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Call this function from the callback function for the "Remove Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Function to generate a search term
def generate_search_term():
    search_term = ""
    wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
    other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']

    # Generate first character
    char_options = wildcard_choices + ['other item']
    char = random.choice(char_options)
    if char == ' ':
        char = '<wildcar>'
    elif char == 'other item':
        char = random.choice(other_list_choices)
    search_term += char

    # Generate middle characters
    for _ in range(2):
        char_options = wildcard_choices + ['other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

    # Generate last character
    char_options = wildcard_choices + ['other item']
    char = random.choice(char_options)
    if char == ' ':
        char = '<wildcard'
    elif char == 'other item':
        char = random.choice(other_list_choices)
    search_term += char

    return search_term

# Register this function as a message handler for the /generate command
@bot.message_handler(commands=['generate'])
def generate_term_command(message):
    search_term = generate_search_term()
    bot.send_message(message.chat.id, f"Generated Search Term: {search_term}")
    print(f"Generated Search Term: {search_term}")

# Function to generate a single character
def generate_single_character():
    other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
    char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
    char = random.choice(char_options)
    if char == 'other item':
        char = random.choice(other_list_choices)
    return char

# Register this function as a message handler for the /roll command
@bot.message_handler(commands=['roll'])
def roll_command(message):
    char = generate_single_character()
    bot.send_message(message.chat.id, f"Rolled Character: {char}")
    print(f"Rolled Character: {char}")

# Call this function from the callback function for the "Roll" button
@bot.callback_query_handler(func=lambda call: call.data == 'roll')
def roll_callback(call):
    char = generate_single_character()
    bot.send_message(call.message.chat.id, f"Rolled Character: {char}")
    print(f"Rolled Character: {char}")

# Function to add a point to a player
def add_point(message):
    player_name = message.text
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

# Register this function as a message handler for the /addpoint command
@bot.message_handler(commands=['addpoint'])
def add_point_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_point)

# Call this function from the callback function for the "Add Point" button
@bot.callback_query_handler(func=lambda call: call.data == 'add_point')
def add_point_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the player's name.")
    bot.register_next_step_handler(msg, add_point)

# Function to remove a player
def remove_player(message):
    player_name = message.text
    if player_name in players:
        del players[player_name]
        bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
        print(f"Player '{player_name}' removed.")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")

# Register this function as a message handler for the /removeplayer command
@bot.message_handler(commands=['removeplayer'])
def remove_player_command(message):
    msg = bot.send_message(message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Call this function from the callback function for the "Remove Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)

# Waiting For New Messages
bot.infinity_polling()
