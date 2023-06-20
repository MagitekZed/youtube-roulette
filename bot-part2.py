
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
 
