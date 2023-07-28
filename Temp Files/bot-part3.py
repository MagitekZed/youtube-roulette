
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
        # Send the superpower choice menu
        self.send_superpower_choice_menu(call.message)

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
