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
        self.card_order = [(i, suit) for suit in ordered_suits for i in range(13)]

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


bot: BeginnerBot = BeginnerBot()
