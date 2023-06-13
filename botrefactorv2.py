import os
import telebot
from telebot import types
import random
from googleapiclient.discovery import build
import time

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)

########################################################
#GAME CLASS BELOW THIS LINE

class Game:
    def __init__(self):
        self.players = {}
        self.turn_order = []
        self.current_player_index = 0
        self.game_phase = "No Game in Progress"
        self.turns_taken = 0

    def start_bot(self):
        self.players.clear()
        self.game_phase = "No Game in Progress"

    def start_new_game(self):
        self.players.clear()
        self.game_phase = "Game Setup"
        print("Starting game setup.")

    def reset_game(self, bot_instance):
        self.players.clear()
        self.game_phase = "No Game in Progress"

    def cancel_game_callback(self, call, bot_instance):
        self.reset_game()
        bot_instance.bot.send_message(call.message.chat.id, "The game has been cancelled. You can start a new game whenever you're ready.")
        bot_instance.send_main_menu(call.message)

    def add_player(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' already exists.")
            bot_instance.send_player_submenu(message)  # Send the new submenu after attempting to add a player      
        else:
            self.players[player_name] = 0
            bot_instance.bot.send_message(message.chat.id, f"Player '{player_name}' added.")
            bot_instance.send_player_submenu(message)  # Send the new submenu after adding a player

    def remove_player(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players:
            del self.players[player_name]
            bot_instance.bot.send_message(message.chat.id, f"Player '{player_name}' removed.")
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
        bot_instance.bot.send_message(message.chat.id, "The game has started!", reply_markup=player_keyboard)
    
        # Announce the first player's turn and send the turn menu
        bot_instance.start_turn(message)


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

    def assign_point_callback(self, call, bot_instance):
        msg = bot_instance.bot.send_message(call.message.chat.id, "Please enter the name of the player to assign a point to.")
        bot_instance.bot.register_next_step_handler(msg, lambda message: self.assign_point_name(message, bot_instance))

    def assign_point_name(self, message, bot_instance):
        if message.text in self.players:
            self.players[message.text] += 1
            bot_instance.bot.send_message(message.chat.id, f"Point assigned to player: {message.text}")
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

    def remove_point_callback(self, call, bot_instance):
        # Send a message asking for the player's name
        msg = bot_instance.bot.send_message(call.message.chat.id, "Please enter the name of the player to remove a point from.")
        # Register a listener for the next message from this user
        bot_instance.bot.register_next_step_handler(msg, lambda message: self.remove_point_name(message, bot_instance))

    def remove_point_name(self, message, bot_instance):
        player_name = message.text
        if player_name in self.players and self.players[player_name] > 0:
            self.players[player_name] -= 1
            bot_instance.bot.send_message(message.chat.id, f"Point removed from player: {player_name}")
            # Send the submenu for assigning or removing points or going to the next round
            bot_instance.send_point_submenu(message)
        else:
            bot_instance.bot.send_message(message.chat.id, f"Error: Player '{player_name}' either does not exist or has no points to remove.")
            # Send the submenu for assigning or removing points or going to the next round
            bot_instance.send_point_submenu(message)

    def get_leaderboard(self):
        # Sort the players by points in descending order
        sorted_players = sorted(self.players.items(), key=lambda x: x[1], reverse=True)
        # Format the leaderboard as a string
        leaderboard = "\n".join(f"{name}: {points}" for name, points in sorted_players)
        return leaderboard

    def end_game(self, message, bot_instance):
        # Find the player(s) with the highest score
        max_score = max(self.players.values())
        winners = [player for player, score in self.players.items() if score == max_score]

        # Prepare the end game message
        if len(winners) == 1:
            winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 *{winners[0]}* is the *WINNER* of the game with *{max_score}* points! 🏆\n\nThanks for playing! Ready for another round?"
        else:
            winner_message = f"🎉🎉🎉 *CONGRATULATIONS!* 🎉🎉🎉\n\n🏆 We have a tie! *{' and '.join(winners)}* are the *WINNERS* of the game with *{max_score}* points each! 🏆\n\nThanks for playing! Ready for another round?"

        # Send the end game message
        bot_instance.bot.send_message(message.chat.id, winner_message, parse_mode='Markdown')

        # Reset the game
        self.reset_game(bot_instance)
        bot_instance.send_main_menu(message)

    def generate_search_term(self):
        search_term = ""
        wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', 'other item']
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']

        # Generate first character
        char = random.choice(wildcard_choices)
        if char == ' ':
            char = '<wildcard>'
        elif char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

        # Generate middle characters
        for _ in range(2):
            char = random.choice(wildcard_choices)
            if char == 'other item':
                char = random.choice(other_list_choices)
            search_term += char

        # Generate last character
        char = random.choice(wildcard_choices)
        if char == ' ':
            char = '<wildcard'
        elif char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char
        print(f"Search term generated: {search_term}")
      
        return search_term

    def generate_single_character(self):
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
        char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        return char


# GAME CLASS ABOVE THIS LINE
########################################################
# BOT CLASS BELOW THIS LINE

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

    def add_player_callback(self, call):
        msg = self.bot.send_message(call.message.chat.id, "Please enter the player's name.")
        self.bot.register_next_step_handler(msg, lambda message: self.game.add_player(message, self))

    def remove_player_callback(self, call):
        msg = self.bot.send_message(call.message.chat.id, "Please enter the name of the player to remove.")
        self.bot.register_next_step_handler(msg, lambda message: self.game.remove_player(message, self))

    def send_player_submenu(self, message):
        markup = types.InlineKeyboardMarkup()
        button_add_another = types.InlineKeyboardButton("Add Another Player", callback_data='add_player')
        button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
        button_start_game = types.InlineKeyboardButton("Start Game", callback_data='start_game')
        button_cancel_game = types.InlineKeyboardButton('Cancel Game', callback_data='cancel_game')
        markup.row(button_add_another, button_remove_player)
        markup.row(button_start_game,button_cancel_game)

        # Generate a string with the list of current players
        player_list = "\n".join(self.game.players.keys())
        if player_list:
            player_list = f"Current players:\n{player_list}"
        else:
            player_list = "No players added yet."

        self.bot.send_message(message.chat.id, f"{player_list}\n\nWould you like to add/remove another player or start the game?", reply_markup=markup)

    def start_game_callback(self, call):
        self.game.start_game(call.message, self)

    def start_turn(self, message):
        current_player = self.game.turn_order[self.game.current_player_index]
        current_score = self.game.players[current_player]
        markup = types.InlineKeyboardMarkup()
        button_generate_term = types.InlineKeyboardButton("Generate Term", callback_data='generate')
        button_roll_character = types.InlineKeyboardButton("Roll Character", callback_data='roll')
        button_next_turn = types.InlineKeyboardButton("Next Turn", callback_data='next_turn')
        markup.row(button_generate_term, button_roll_character)
        markup.row(button_next_turn)
        self.bot.send_message(message.chat.id, f"It's {current_player}'s turn. Your current score is {current_score}.\n\nGenerate Term: Create a 4-character search term for YouTube.\nRoll Character: Randomly select a character for the search term.\nNext Turn: Pass your turn to the next player.", reply_markup=markup)

    def next_turn_callback(self, call):
        self.game.next_turn(call.message, self)

    def send_end_of_round_menu(self, message):
        markup = types.InlineKeyboardMarkup()
        button_assign_point = types.InlineKeyboardButton("Assign Point", callback_data='assign_point')
        button_remove_point = types.InlineKeyboardButton("Remove Point", callback_data='remove_point')
        button_show_rules = types.InlineKeyboardButton("Show Rules", callback_data='show_rules')
        button_end_game = types.InlineKeyboardButton("End Game", callback_data='end_game')
        button_next_round = types.InlineKeyboardButton("Next Round", callback_data='next_round')
        markup.row(button_assign_point, button_remove_point)
        markup.row(button_show_rules, button_end_game)
        markup.row(button_next_round)
        self.bot.send_message(message.chat.id, "Round over! Time to vote for the winner!", reply_markup=markup)

    def next_round_callback(self, call):
        self.game.next_round(call.message, self)

    def send_point_submenu(self, message):
        markup = types.InlineKeyboardMarkup()
        button_assign_point = types.InlineKeyboardButton("Assign Another Point", callback_data='assign_point')
        button_remove_point = types.InlineKeyboardButton("Remove Point", callback_data='remove_point')
        button_next_round = types.InlineKeyboardButton("Next Round", callback_data='next_round')
        button_end_game = types.InlineKeyboardButton("End Game", callback_data='end_game')
        markup.row(button_assign_point, button_remove_point)
        markup.row(button_next_round, button_end_game)
        self.bot.send_message(message.chat.id, "What would you like to do next?", reply_markup=markup)

    def show_leaderboard(self, message):
        # Get the leaderboard
        leaderboard = self.game.get_leaderboard()
        # Send the leaderboard
        self.bot.send_message(message.chat.id, f"Leaderboard:\n{leaderboard}")
        # Check if the game has ended
        if self.game.game_phase == "Game End":
            # Send the main menu for the "Game End" phase
            self.send_main_menu(message)

    def show_leaderboard_callback(self, call):
        self.show_leaderboard(call.message)

    def end_game_callback(self, call):
        self.game.end_game(call.message, self)

    def generate_term_callback(self, call):
        search_term = self.game.generate_search_term()
        self.bot.send_message(call.message.chat.id, f"Generated search term: {search_term}")
        self.search_youtube(search_term, call.message)

    def roll_character_callback(self, call):
        char = self.game.generate_single_character()
        self.bot.send_message(call.message.chat.id, f"Rolled Character: {char}")
        print(f"Rolled Character: {char}")

    def search_youtube(self, search_term, message):
        youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'), cache_discovery=False, discoveryServiceUrl='https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest')
    
        request = youtube.search().list(
            part="snippet",
            maxResults=3,
            q=search_term,
            type="video"
        )

        response = request.execute()

        for item in response['items']:
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            self.bot.send_message(message.chat.id, video_title)
            self.bot.send_message(message.chat.id, video_url)
            time.sleep(2)  # Add a 1-second delay

# BOT CLASS ABOVE THIS LINE
########################################################

# Create an instance of the Bot class
bot_instance = Bot(BOT_TOKEN)

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
    bot_instance.game.cancel_game_callback(call, bot_instance)

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
    bot_instance.game.assign_point_callback(call, bot_instance)

@bot_instance.bot.callback_query_handler(func=lambda call: call.data == 'remove_point')
def remove_point_callback(call):
    bot_instance.game.remove_point_callback(call, bot_instance)

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


########################################################

# Start polling for new messages
bot_instance.start_polling()
