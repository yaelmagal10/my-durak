from abstract_bot import AbstractBot

class BeginnerBot(AbstractBot):
    """A beginner bot that plays a simple strategy."""
    
    def game_init(self, num_of_players: int, my_index: int, hand: list, kozar_card: tuple, table_cards: list):
        print("BeginnerBot: game_init called")
        ordered_suits = [0, 1, 2, 3]
        ordered_suits[self.get_kozar_suit()] = 3
        ordered_suits[3] = self.get_kozar_suit()
        self.card_order = [(i, suit) for i in range(13) for suit in ordered_suits]

    def remove_Nones(self, lst):
        """Remove None values from a list."""
        return [item for item in lst if item is not None]

    def optional_attack(self):
        table_cards = self.get_attacking_table_cards() + self.get_defending_table_cards()
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
        lowest_card_index = len(self.get_hand())
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
        return attacking_cards

    def defend(self):
        if len(self.remove_Nones(self.get_defending_table_cards())) == 0:
            defending_cards = []
            for card in self.get_hand():
                if card[0] == self.get_attacking_table_cards()[0][0]:
                    defending_cards.append(card)
            if len(defending_cards) != 0:
                return defending_cards, []
        numbers_by_suit = [sorted([card[0] for card in self.get_hand() if card[1] == suit]) for suit in range(4)]
        defending_cards = []
        indexes = []
        for i, card in sorted(enumerate(self.get_attacking_table_cards()),
                               key=lambda x: self.card_order.index(x[1]) if x[1] is not None else 53):
            if card is None:
                continue
            succeess = False
            for number in numbers_by_suit[card[1]]:
                if number > card[0]:
                    defending_cards.append((number, card[1]))
                    indexes.append(i)
                    succeess = True
                    numbers_by_suit[card[1]].remove(number)
                    break
            if not succeess:
                if len(numbers_by_suit[self.get_kozar_suit()]) > 0:
                    defending_cards.append((numbers_by_suit[self.get_kozar_suit()][0], self.get_kozar_suit()))
                    indexes.append(i)
                    numbers_by_suit[self.get_kozar_suit()].pop(0)
                    succeess = True
            if not succeess:
                return [], []
        return defending_cards, indexes

bot: BeginnerBot = BeginnerBot()