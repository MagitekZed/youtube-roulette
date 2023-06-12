import os
import telebot
from telebot import types
import random


# Global Variables

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)
# List of players and their scores
players = {}
# List of players in turn order
turn_order = []
# Index of the current player
current_player_index = 0
# Global variable to store the number of turns taken in the current round
turns_taken = 0
# Global variable to store the current game phase
game_phase = "No Game in Progress"


#STARTING THE GAME AND MAIN MENU

# Function definition for the /start command
@bot.message_handler(commands=['start'])
def start_command(message):

    # Reset the game phase
    global game_phase
    game_phase = "No Game in Progress"

    # Reset the players dictionary
    global players
    players = {}

    # Display the main menu
    send_main_menu(message)

# Main Menu 
@bot.message_handler(commands=['menu'])
def send_main_menu(message):
    # Create an instance of InlineKeyboardMarkup
    markup = types.InlineKeyboardMarkup()

    # Define the inline keyboard buttons.
    button_rules = types.InlineKeyboardButton("Detailed Rules", callback_data='show_rules')

    if game_phase == "No Game in Progress" or game_phase == "Game End":
        button_new_game = types.InlineKeyboardButton("Start New Game", callback_data='new_game')
        # Clear the custom keyboard
        global player_keyboard
        player_keyboard = types.ReplyKeyboardRemove()

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
        bot.send_message(message.chat.id, explanation_text, reply_markup=player_keyboard)
        bot.send_message(message.chat.id, start_text, reply_markup=markup)

    # Explanation of the game setup phase
    elif game_phase == "Game Setup":
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
    
        bot.send_message(message.chat.id, setup_text, reply_markup=markup)

    #Explanation of the game setup phase
    elif game_phase == "Game In Progress":
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
    
        bot.send_message(message.chat.id, explanation_text, reply_markup=markup)
    

#ENTERING THE GAME SETUP PHASE

# Function to start a new game
def start_new_game(message):
    players.clear()
    print("Starting game setup.")

# Register this function as a message handler for the /newgame command
@bot.message_handler(commands=['newgame'])
def new_game_command(message):
    start_new_game(message)
    # Transition to the "Game Setup" phase
    global game_phase
    game_phase = "Game Setup"
    bot.send_message(message.chat.id, "The game setup phase has started! Use the menu to add players.")
    send_main_menu(message)

# Callback for the "Start New Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'new_game')
def new_game_callback(call):
    # Call the function that handles the /newgame command
    start_new_game(call.message)
    # Transition to the "Game Setup" phase
    global game_phase
    game_phase = "Game Setup"
    send_main_menu(call.message)


# The rules function is called when the user clicks the "Show Rules" button.
# It sends a new message with the rules of the game.
@bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def rules(call):
    bot.send_message(call.message.chat.id, """
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

# Register this function as a message handler for the /rules command
@bot.message_handler(commands=['rules'])
def rules_command(message):
    show_rules(message)

# Call this function from the callback function for the "Show Rules" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_rules')
def show_rules_callback(call):
    show_rules(call.message)

# Callback for the "Cancel Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'cancel_game')
def cancel_game_callback(call):
    # Reset the game
    reset_game()
    # Send a message to the user
    bot.send_message(call.message.chat.id, "The game has been cancelled. You can start a new game whenever you're ready.")
    send_main_menu(call.message)



#ADD AND REMOVE PLAYERS

# Function to add a player
def add_player(message):
    player_name = message.text
    if player_name in players:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
        send_player_submenu(message)  # Send the new submenu after attempting to add a player      
    else:
        players[player_name] = 0
        bot.send_message(message.chat.id, f"Player '{player_name}' added.")
        send_player_submenu(message)  # Send the new submenu after adding a player

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
        send_player_submenu(message)  # Send the new submenu after removing a player
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' not found.")
        send_player_submenu(message)  # Send the new submenu after removing a player        

# Call this function from the callback function for the "Remove Player" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_player')
def remove_player_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
    bot.register_next_step_handler(msg, remove_player)


# Send the add/remove player submenu during game setup
def send_player_submenu(message):
    markup = types.InlineKeyboardMarkup()
    button_add_another = types.InlineKeyboardButton("Add Another Player", callback_data='add_player')
    button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
    button_start_game = types.InlineKeyboardButton("Start Game", callback_data='start_game')
    button_cancel_game = types.InlineKeyboardButton('Cancel Game', callback_data='cancel_game')
    markup.row(button_add_another, button_remove_player)
    markup.row(button_start_game,button_cancel_game)

    # Generate a string with the list of current players
    player_list = "\n".join(players.keys())
    if player_list:
        player_list = f"Current players:\n{player_list}"
    else:
        player_list = "No players added yet."

    bot.send_message(message.chat.id, f"{player_list}\n\nWould you like to add/remove another player or start the game?", reply_markup=markup)



#TRANSITION TO GAME IN PROGRESS

# Callback for the "Start Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def start_game_callback(call):
    # Check if there are enough players to start the game
    if len(players) < 2:
        bot.send_message(call.message.chat.id, "Error: At least 2 players are required to start the game.")
    else:
        # Initialize turn order
        global turn_order
        turn_order = list(players.keys())
        random.shuffle(turn_order)

        # Initialize current player index
        global current_player_index
        current_player_index = 0

        # Create a new ReplyKeyboardMarkup object. This will be the custom keyboard.
        global player_keyboard
        player_keyboard = types.ReplyKeyboardMarkup(row_width=2)

        # Create a list of KeyboardButton objects, one for each player in the game.
        player_buttons = [types.KeyboardButton(player) for player in players]

        # Add all of the player buttons to the markup using the add method.
        player_keyboard.add(*player_buttons)

        # Transition to the "Game In Progress" phase
        global game_phase
        game_phase = "Game In Progress"
        bot.send_message(call.message.chat.id, "The game has started!", reply_markup=player_keyboard)

        # Announce the first player's turn and send the turn menu
        start_turn(call.message)


#TURN MANAGEMENT

# Function to start the turn
def start_turn(message):
    current_player = turn_order[current_player_index]
    current_score = players[current_player]
    markup = types.InlineKeyboardMarkup()
    button_generate_term = types.InlineKeyboardButton("Generate Term", callback_data='generate')
    button_roll_character = types.InlineKeyboardButton("Roll Character", callback_data='roll')
    button_next_turn = types.InlineKeyboardButton("Next Turn", callback_data='next_turn')
    markup.row(button_generate_term, button_roll_character)
    markup.row(button_next_turn)
    bot.send_message(message.chat.id, f"It's {current_player}'s turn. Your current score is {current_score}.\n\nGenerate Term: Create a 4-character search term for YouTube.\nRoll Character: Randomly select a character for the search term.\nNext Turn: Pass your turn to the next player.", reply_markup=markup)

# Callback for the "Next Turn" button
@bot.callback_query_handler(func=lambda call: call.data == 'next_turn')
def next_turn_callback(call):
    global current_player_index
    current_player_index += 1
    if current_player_index >= len(turn_order):
        # Reset the current player index
        current_player_index = 0
        # Send the end of round menu
        send_end_of_round_menu(call.message)
    else:
        # If not everyone has had a turn, start the next turn
        start_turn(call.message)
      
# Callback for the "Next Turn" button
@bot.callback_query_handler(func=lambda call: call.data == 'next_turn')
def next_turn_callback(call):
    global current_player_index
    global turns_taken
    # Increment the index of the current player (wrapping around to the start of the list if necessary)
    current_player_index = (current_player_index + 1) % len(turn_order)
    # Increment the number of turns taken
    turns_taken += 1
    # Check if the round is over
    if turns_taken == len(turn_order):
        # Reset the number of turns taken
        turns_taken = 0
        # Send the end of round menu
        send_end_of_round_menu(call.message)
    else:
        # Start the next turn
        start_turn(call.message)

# Function to send the end of round menu
def send_end_of_round_menu(message):
    markup = types.InlineKeyboardMarkup()
    button_assign_point = types.InlineKeyboardButton("Assign Point", callback_data='assign_point')
    button_remove_point = types.InlineKeyboardButton("Remove Point", callback_data='remove_point')
    button_show_rules = types.InlineKeyboardButton("Show Rules", callback_data='show_rules')
    button_end_game = types.InlineKeyboardButton("End Game", callback_data='end_game')
    button_next_round = types.InlineKeyboardButton("Next Round", callback_data='next_round')
    markup.row(button_assign_point, button_remove_point)
    markup.row(button_show_rules, button_end_game)
    markup.row(button_next_round)
    bot.send_message(message.chat.id, "Round over! Time to vote for the winner!", reply_markup=markup)

# Callback for the "Next Round" button
@bot.callback_query_handler(func=lambda call: call.data == 'next_round')
def next_round_callback(call):
    # Reset the current player index
    global current_player_index
    current_player_index = 0
    # Show the leaderboard
    show_leaderboard(call.message)
    # Start the next round
    start_turn(call.message)

# Callback for the "Assign Point" button
@bot.callback_query_handler(func=lambda call: call.data == 'assign_point')
def assign_point_callback(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to assign a point to.")
    bot.register_next_step_handler(msg, assign_point_name)

# Function definition for assigning points
@bot.message_handler(func=lambda message: True, content_types=['text'])
def assign_point_name(message):
    if message.text in players:
        players[message.text] += 1
        bot.send_message(message.chat.id, f"Point assigned to player: {message.text}")
        if players[message.text] == 3:
            # Transition to the "Game End" phase
            global game_phase
            game_phase = "Game End"
            bot.send_message(message.chat.id, f"Player '{message.text}' has won the game with 3 points!")
            # Display the final leaderboard
            show_leaderboard(message)
        else:
            # Send the submenu for assigning or removing points or going to the next round
            send_point_submenu(message)
    else:
        bot.send_message(message.chat.id, f"Error: Player '{message.text}' does not exist.")

# point submenu after assigning a point
def send_point_submenu(message):
    markup = types.InlineKeyboardMarkup()
    button_assign_point = types.InlineKeyboardButton("Assign Another Point", callback_data='assign_point')
    button_remove_point = types.InlineKeyboardButton("Remove Point", callback_data='remove_point')
    button_next_round = types.InlineKeyboardButton("Next Round", callback_data='next_round')
    button_end_game = types.InlineKeyboardButton("End Game", callback_data='end_game')
    markup.row(button_assign_point, button_remove_point)
    markup.row(button_next_round, button_end_game)
    bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=markup)

# function to show the leaderboard
def show_leaderboard(message):
    # Determine the chat ID
    chat_id = message.chat.id
    # Sort the players by points in descending order
    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
    # Format the leaderboard as a string
    leaderboard = "\n".join(f"{name}: {points}" for name, points in sorted_players)
    # Send the leaderboard
    bot.send_message(chat_id, f"Leaderboard:\n{leaderboard}")
    # Check if the game has ended
    if game_phase == "Game End":
        # Send the main menu for the "Game End" phase
        send_main_menu(message)

# Callback for the "Show Leaderboard" button
@bot.callback_query_handler(func=lambda call: call.data == 'show_leaderboard')
def show_leaderboard_callback(call):
    show_leaderboard(call.message)

# Callback for the "Remove Point" button
@bot.callback_query_handler(func=lambda call: call.data == 'remove_point')
def remove_point_callback(call):
    # Send a message asking for the player's name
    msg = bot.send_message(call.message.chat.id, "Please enter the name of the player to remove a point from.")
    # Register a listener for the next message from this user
    bot.register_next_step_handler(msg, remove_point_name)

# function to remove a point
def remove_point_name(message):
    player_name = message.text
    if player_name in players and players[player_name] > 0:
        players[player_name] -= 1
        bot.send_message(message.chat.id, f"Point removed from player: {player_name}")
    else:
        bot.send_message(message.chat.id, f"Error: Player '{player_name}' either does not exist or has no points to remove.")

# Function to end the game
def end_game(message):
    # Find the player(s) with the highest score
    max_score = max(players.values())
    winners = [player for player, score in players.items() if score == max_score]

    # Prepare the end game message
    if len(winners) == 1:
        winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 *{winners[0]}* is the *WINNER* of the game with *{max_score}* points! 🏆\n\nThanks for playing! Ready for another round?"
    else:
        winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 We have a tie! *{' and '.join(winners)}* are the *WINNERS* of the game with *{max_score}* points each! 🏆\n\nThanks for playing! Ready for another round?"

    # Send the end game message
    bot.send_message(message.chat.id, winner_message, parse_mode='Markdown')

    # Reset the game
    reset_game()
    send_main_menu(message)

# Callback for the "End Game" button
@bot.callback_query_handler(func=lambda call: call.data == 'end_game')
def end_game_callback(call):
    end_game(call.message)

# Function to reset the game
def reset_game():
    global players, game_phase
    players = {}
    game_phase = "No Game in Progress"

# Function to generate a search term
def generate_search_term():
    search_term = ""
    wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'']
    other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']

    # Generate first character
    char_options = wildcard_choices + ['other item']
    char = random.choice(char_options)
    if char == ' ':
        char = '<wildcard>'
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

# Callback for the "Generate Term" button
@bot.callback_query_handler(func=lambda call: call.data == 'generate')
def generate_term_callback(call):
    search_term = generate_search_term()
    bot.send_message(call.message.chat.id, f"Generated Search Term: {search_term}")

# Callback for the "Roll Character" button
@bot.callback_query_handler(func=lambda call: call.data == 'roll')
def roll_character_callback(call):
    char = generate_single_character()
    bot.send_message(call.message.chat.id, f"Rolled Character: {char}")

# Waiting For New Messages
bot.infinity_polling()
