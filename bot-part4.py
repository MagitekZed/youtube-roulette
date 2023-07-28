
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
        index = self.user_data[message.chat.id]

        # Replace the character with the user's input
        game_session.handle_character_input(index, message.text)

        # Remove the index from the user data
        del self.user_data[message.chat.id]

        # Go to the next turn
        self.continue_callback(message)

    def swap_superpower(self, call):
        game_session = self.get_game_session(call.message.chat.id)  # Get the game instance for this user
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
            game_session.swap_characters(index1, index2)

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
