from game import Game
import os
import telebot
from telebot import types
import random
from googleapiclient.discovery import build
import time
import re
import requests
import json
import time

# Getting Bot Token From Secrets
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Creating Telebot Object
bot = telebot.TeleBot(BOT_TOKEN)
# Watch2Gether API token
WATCH_TOKEN = os.environ.get('WATCH_TOKEN')

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
        2️⃣ The player will then search YouTube using this term and choose one of the first three videos that appear. Note that are considered wildcards and don't count as one of the three choices, though they may be chosen. If a playlist is chosen, you must play the FIRST video.
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

    def cancel_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.reset_game(self)
        self.bot.send_message(call.message.chat.id, "The game has been cancelled. You can start a new game whenever you're ready.")
        print("Game cancelled.")
        self.send_main_menu(call.message)
    

    def send_player_submenu(self, message):
        game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
        markup = types.InlineKeyboardMarkup()
        button_add_another = types.InlineKeyboardButton("Add Another Player", callback_data='add_player')
        button_remove_player = types.InlineKeyboardButton("Remove Player", callback_data='remove_player')
        button_start_game = types.InlineKeyboardButton("Start Game", callback_data='start_game')
        button_cancel_game = types.InlineKeyboardButton('Cancel Game', callback_data='cancel_game')
        markup.row(button_add_another, button_remove_player)
        markup.row(button_start_game,button_cancel_game)

        # Generate a string with the list of current players
        player_list = "\n".join(game_session.players.keys())
        if player_list:
            player_list = f"Current players:\n{player_list}"
        else:
            player_list = "No players added yet."

        self.bot.send_message(message.chat.id, f"{player_list}\n\nWould you like to add/remove another player or start the game?", reply_markup=markup)

    def start_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user

        # Create a new room
        create_room_url = 'https://api.w2g.tv/rooms/create.json'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        body = {
            'w2g_api_key': WATCH_TOKEN,
            'share': 'https://youtu.be/pdsJ8GpPXbc',  # Preload "Let's get started!" video
            'bg_color': '#A6C3D5',  # Change this to your preferred color
            'bg_opacity': '50'
        }
        response = requests.post(create_room_url, headers=headers, data=json.dumps(body))
        data = response.json()

        # Get the streamkey
        streamkey = data['streamkey']

        # Store the room link in the game session
        game_session.room_link = f'https://w2g.tv/rooms/{streamkey}'
        print('Here\'s your stream link: ')
        print(game_session.room_link)
      
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

    def next_turn_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.next_turn(call.message, self)

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
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.next_round(call.message, self)

    def assign_point_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        msg = self.bot.send_message(call.message.chat.id, "Please enter the name of the player to assign a point to.")
        self.bot.register_next_step_handler(msg, lambda message: game_session.assign_point_name(message, self))

    def remove_point_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        msg = self.bot.send_message(call.message.chat.id, "Please enter the name of the player to remove a point from.")
        self.bot.register_next_step_handler(msg, lambda message: game_session.remove_point_name(message, self))

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
        game_session = self.get_game_session(message.chat.id)  # Get the game instance for this user
        # Get the leaderboard
        leaderboard = game_session.get_leaderboard()
        # Send the leaderboard
        self.bot.send_message(message.chat.id, f"Leaderboard:\n{leaderboard}")
        # Check if the game has ended
        if game_session.game_phase == "Game End":
            # Send the main menu for the "Game End" phase
            self.send_main_menu(message)

    def show_leaderboard_callback(self, call):
        self.show_leaderboard(call.message)

    def end_game_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        game_session.end_game(call.message, self)

    def generate_term_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Generate the term
        game_session.generate_search_term()
        # Send a message with the generated term
        self.bot.send_message(call.message.chat.id, f"Search term generated: {game_session.search_term}")
        # Send the superpower menu
        self.send_superpower_menu(call.message)

    def roll_character_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        char = game_session.generate_single_character()
        self.bot.send_message(call.message.chat.id, f"Rolled Character: {char}")
        print(f"Rolled Character: {char}")

    def search_youtube(self, message, search_term):
      youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_API_KEY'), cache_discovery=False, discoveryServiceUrl='https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest')
  
      search_request = youtube.search().list(
          part="snippet",
          maxResults=20,
          q=search_term,
          type="video,playlist"
      )
  
      search_response = search_request.execute()
  
      video_count = 0
      for item in search_response['items']:
          if video_count == 3:
              break
  
          item_id = item['id']
          item_type = item_id['kind'].split('#')[-1]
          item_title = item['snippet']['title']
          item_id = item_id['videoId'] if item_type == 'video' else item_id['playlistId']
  
          # Make an additional API call to get the video details
          video_request = youtube.videos().list(
              part="statistics,contentDetails",
              id=item_id
          ) if item_type == 'video' else None
  
          video_response = video_request.execute() if video_request else None
          video_item = video_response['items'][0] if video_response else None
  
          # Get the number of views and the length of the video
          if video_item and 'statistics' in video_item:
              video_views = video_item['statistics']['viewCount']
          else:
              video_views = 'N/A'
  
          video_length = video_item['contentDetails']['duration'] if video_item else 'N/A'  # This is in the format PT#M#S
  
          if video_length != 'N/A':
              video_duration = re.search('PT(\d+M)?(\d+S)?', video_length)
              video_minutes = video_duration.group(1)[:-1] if video_duration.group(1) else '0'
              video_seconds = video_duration.group(2)[:-1] if video_duration.group(2) else '0'
              video_length = f"{video_minutes} minutes {video_seconds} seconds"
  
          item_url = f"https://www.youtube.com/watch?v={item_id}" if item_type == 'video' else f"https://www.youtube.com/playlist?list={item_id}"
  
          # Send a message with the item details
          if item_type == 'playlist':
              # Make an API call to retrieve the first video in the playlist
              playlist_items_request = youtube.playlistItems().list(
                  part="snippet",
                  maxResults=1,
                  playlistId=item_id
              )
              
              playlist_items_response = playlist_items_request.execute()
              playlist_items = playlist_items_response.get('items', [])
              
              if playlist_items:
                  first_video_item = playlist_items[0]
                  first_video_id = first_video_item['snippet']['resourceId']['videoId']
                  item_url = f"https://www.youtube.com/playlist?list={item_id}"
              
                  # Retrieve the thumbnail for the first video with high resolution
                  video_request = youtube.videos().list(
                      part="snippet",
                      id=first_video_id,
                      fields="items(snippet(thumbnails(high(url))))"
                  )
              
                  video_response = video_request.execute()
                  video_items = video_response.get('items', [])
              
                  if video_items:
                      video_item = video_items[0]
                      thumbnail = video_item['snippet']['thumbnails']['high']
                      thumbnail_url = thumbnail['url']
                      # Include the playlist URL and thumbnail URL in the message
                      item_message = f"<b>PLAYLIST</b>\n\nTitle: {item_title}\nViews: N/A\nLength: N/A\nThumbnail: {thumbnail_url}\nURL: {item_url}"
                  else:
                      item_message = f"<b>PLAYLIST</b>\n\nTitle: {item_title}\nViews: N/A\nLength: N/A\nURL: {item_url}"
              else:
                  item_message = f"<b>PLAYLIST</b>\n\nTitle: {item_title}\nViews: N/A\nLength: N/A\nURL: {item_url}"
          else:
              item_message = f"Title: {item_title}\nViews: {video_views}\nLength: {video_length}\nURL: {item_url}"
  
          # Send a message with the item details
          self.bot.send_message(message.chat.id, item_message, parse_mode='HTML')
          log_message = item_message
          print(log_message)
          time.sleep(2)  # Add a 2-second delay
  
          if item_type == 'video':
              video_count += 1

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

    def get_player_name(self, user_id):
        # Retrieve the game session for the user
        game_session = self.get_game_session(user_id)
        
        # Retrieve the current player's name from the game session
        current_player_index = game_session.current_player_index
        current_player = game_session.turn_order[current_player_index]
    
        return current_player

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
        - Reroll: Reroll a character in the search term.
        - Replace: Replace a character in the search term.
        - Swap: Swap two characters in the search term.
        """

        # Send the message with the markup
        self.bot.send_message(message.chat.id, superpowers_explanation + "Choose a superpower or continue without using one:", reply_markup=markup)

    def use_superpower_callback(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user        
        self.send_superpower_choice_menu(call.message)
        
    def reroll_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user

        # Retrieve the current player's name
        current_player = self.get_player_name(call.message.chat.id)
        print(f"reroll player name: {current_player}")

        # Check if the reroll superpower has already been used by the player
        if game_session.superpowers_used[current_player]["reroll"]:
            self.bot.send_message(call.message.chat.id, f"The 'reroll' superpower has already been used by {current_player}.")
            # Go back to the superpower menu
            self.send_superpower_choice_menu(call.message)
        else:
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

        # Retrieve the current player's name
        player_name = self.get_player_name(call.message.chat.id)
        
        # Get the index of the character to replace
        index = int(call.data.split('_')[1])
    
        # Replace the character
        game_session.reroll_superpower(player_name, index)
        
        self.bot.send_message(call.message.chat.id, f"Superpower 'reroll' used successfully. New term: {game_session.search_term}")
                
        # Go to the next turn
        self.continue_callback(call)

    def replace_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user

        # Retrieve the current player's name
        current_player = self.get_player_name(call.message.chat.id)
        print(f"Replace player name: {current_player}")

        # Check if the replace superpower has already been used by the player
        if game_session.superpowers_used[current_player]["replace"]:
            self.bot.send_message(call.message.chat.id, f"The 'replace' superpower has already been used by {current_player}.")
            # Go back to the superpower menu
            self.send_superpower_choice_menu(call.message)
        else:
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
        # Retrieve the current player's name
        player_name = self.get_player_name(message.chat.id)

        index = self.user_data[message.chat.id]

        # Replace the character with the user's input
        game_session.handle_character_input(index, message.text, player_name)

        # Remove the index from the user data
        del self.user_data[message.chat.id]

        # Go to the next turn
        self.continue_callback(message)

    def swap_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
        # Retrieve the current player's name
        current_player = self.get_player_name(call.message.chat.id)
        print(f"Swap player name: {current_player}")

        # Check if the swap superpower has already been used by the player
        if game_session.superpowers_used[current_player]["swap"]:
            self.bot.send_message(call.message.chat.id, f"The 'swap' superpower has already been used by {current_player}.")
            # Go back to the superpower menu
            self.send_superpower_choice_menu(call.message)
        else:
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
        # Retrieve the current player's name
        player_name = self.get_player_name(call.message.chat.id)

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
            game_session.swap_characters(index1, index2, player_name)

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
