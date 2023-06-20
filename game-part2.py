
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
        print(f"{winner_message}")
        bot_instance.bot.send_message(message.chat.id, winner_message, parse_mode='Markdown')

        # Reset the game
        self.reset_game(bot_instance)
        bot_instance.send_main_menu(message)

    def generate_search_term(self):
        search_term = ""
        wildcard_choices = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', 'other item']
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
        first_last_choice = wildcard_choices
        first_last_choice.remove(' ')
      
        # Generate first character
        char = random.choice(first_last_choice)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char

        # Generate middle characters
        for _ in range(2):
            char = random.choice(wildcard_choices)
            if char == 'other item':
                char = random.choice(other_list_choices)
            search_term += char

        # Generate last character
        char = random.choice(first_last_choice)
        if char == 'other item':
            char = random.choice(other_list_choices)
        search_term += char
        self.search_term = search_term
        print(f"Search term generated: {search_term}")
      
        return search_term

    def generate_single_character(self):
        other_list_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '/', '$', '%', '+', '[', ']', '\"', '_', '-', '.', ':', '?', '!', '@', '&', '#', '(']
        char_options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '-', '\'', ' ', 'other item']
        char = random.choice(char_options)
        if char == 'other item':
            char = random.choice(other_list_choices)
        return char

    def reroll_superpower(self, index):
        # Replace the character
        char = self.generate_single_character()
        self.search_term = self.search_term[:index] + char + self.search_term[index+1:]

    def replace_character(self, old_char, new_char):
        # Replace the old character with the new character in the search term
        self.search_term = self.search_term.replace(old_char, new_char, 1)
        print(f"new search term: {search_term}")

    def replace_character_with_input(self, index, new_char):
        # Replace the character with the user's input
        self.search_term = self.search_term[:index] + new_char + self.search_term[index+1:]

    def handle_character_input(self, index, new_char):
        # Replace the character with the user's input
        self.replace_character_with_input(index, new_char)

    def swap_characters(self, index1, index2):
        # Swap the characters
        chars = list(self.search_term)
        chars[index1], chars[index2] = chars[index2], chars[index1]
        self.search_term = ''.join(chars)

    
