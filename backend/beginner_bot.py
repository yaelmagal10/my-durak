from abstract_bot import AbstractBot


class BeginnerBot(AbstractBot):
    """A beginner bot that plays a simple strategy."""

    def game_init(
        self,
        num_of_players: int,
        my_index: int,
        hand: list,
        kozar_card: tuple,
        first_player: int,
        lowest_kozar: int,
    ):
        self.log("BeginnerBot: game_init called")
        ordered_suits = [0, 1, 2, 3]
        ordered_suits[self.get_kozar_suit()] = 3
        ordered_suits[3] = self.get_kozar_suit()
        self.card_order = [(i, suit) for i in range(13) for suit in ordered_suits]
        self.log(f"BeginnerBot: card_order initialized: {self.card_order}")

    def remove_Nones(self, lst):
        """Remove None values from a list."""
        return [item for item in lst if item is not None]

    def optional_attack(self):
        table_cards = self.get_table_attack() + self.get_table_defence()
        table_cards = self.remove_Nones(table_cards)
        table_numbers = [card[0] for card in table_cards]
        attacking_cards = []
        for card in self.get_hand():
            if card[1] == self.get_kozar_suit():
                pass
            elif card[0] in table_numbers:
                attacking_cards.append(card)
        return attacking_cards

    def first_attack(self):
        """returns the lowest card in hand by the card order."""
        lowest_card = None
        lowest_card_index = len(self.card_order)
        for card in self.get_hand():
            card_index = self.card_order.index(card)
            if card_index < lowest_card_index:
                lowest_card = card
                lowest_card_index = card_index
        attacking_cards = [lowest_card]
        for card in self.get_hand():
            if card[1] == self.get_kozar_suit() or card == lowest_card:
                continue
            if card[0] == lowest_card[0]:
                attacking_cards.append(card)
        self.log(
            f"BeginnerBot: first_attack called, attacking_cards: {attacking_cards}"
        )
        return attacking_cards

    def defence(self):
        if len(self.remove_Nones(self.get_table_defence())) == 0:
            defending_cards = []
            for card in self.get_hand():
                if card[0] == self.get_table_attack()[0][0]:
                    defending_cards.append(card)
            if len(defending_cards) != 0:
                return defending_cards, []
        numbers_by_suit = [
            sorted([card[0] for card in self.get_hand() if card[1] == suit])
            for suit in range(4)
        ]
        defending_cards = []
        indexes = []
        table_defence = self.get_table_defence()
        self.log(f"numbers_by_suit: {numbers_by_suit}")
        self.log(f"hand: {self.get_hand()}")
        for i, card in sorted(
            enumerate(self.get_table_attack()),
            key=lambda x: self.card_order.index(x[1]) if x[1] is not None else 53,
        ):
            if card is None or table_defence[i] is not None:
                continue
            success = False
            for number in numbers_by_suit[card[1]]:
                if number > card[0]:
                    defending_cards.append((number, card[1]))
                    indexes.append(i)
                    success = True
                    numbers_by_suit[card[1]].remove(number)
                    break
            if not success:
                if len(numbers_by_suit[self.get_kozar_suit()]) > 0 and card[1] != self.get_kozar_suit():
                    defending_cards.append(
                        (
                            numbers_by_suit[self.get_kozar_suit()][0],
                            self.get_kozar_suit(),
                        )
                    )
                    indexes.append(i)
                    numbers_by_suit[self.get_kozar_suit()].pop(0)
                    success = True
            if not success:
                return [], []
        return defending_cards, indexes
    
    def notify_burn(self, card_list):
        self.log(f"burn: {card_list}")

    def notify_cards_drawn_to_hand(self, card_list):
        self.log(f"cards drawn to hand: {card_list}")
        for card in card_list:
            if card not in self.get_hand():
                self.log(f"Card {card} not in hand, something is wrong!")
    
    def notify_winner(self, winner_index):
        self.log(f"Winner: {winner_index}")
        if winner_index == self.get_my_index():
            self.log("BeginnerBot: I won!")
    
    def notify_pass(self, player_index):
        self.log(f"Player {player_index} passed")
    
    def notify_optional_attack(self, player_index, cards):
        self.log(f"Player {player_index} optional attack with cards: {cards}")
        for card in cards:
            if card not in self.get_table_attack():
                self.log(f"Card {card} not in table attack, something is wrong!")
    
    def notify_first_attack(self, player_index, cards):
        self.log(f"Player {player_index} first attack with cards: {cards}")
        for card in cards:
            if card not in self.get_table_attack():
                self.log(f"Card {card} not in table attack, something is wrong!")
    
    def notify_defence(self, player_index, defending_cards, indexes):
        self.log(f"Player {player_index} defended with cards: {defending_cards} at indexes: {indexes}")
        for card in defending_cards:
            if card not in self.get_table_defence():
                self.log(f"Card {card} not in table defence, something is wrong!")
    
    def notify_forward(self, forwarder_index, card_list):
        try:
            self.log(f"Player {forwarder_index} forwarded with cards: {card_list}")
            for card in card_list:
                if card not in self.get_table_attack():
                    self.log(f"Card {card} not in table attack, something is wrong!")
            if not all(card[0] == card_list[0][0] for card in self.get_table_attack() if card is not None):
                self.log("Not all forwarded cards have the same number, something is wrong!")
            if not all(card is None for card in self.get_table_defence()):
                self.log("There are cards in table defence, something is wrong!")
        except Exception as e:
            self.log(f"Error in notify_forward: {e}")
    
    def notify_take(self, defender_index, card_list):
        self.log(f"Player {defender_index} took cards: {card_list}")
    
    



bot: BeginnerBot = BeginnerBot()
