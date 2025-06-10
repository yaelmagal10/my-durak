from abstract_bot import AbstractBot
from typing import List, Tuple
import random


class BasicBot(AbstractBot):
    def game_init(
        self,
        num_of_players: int,
        my_index: int,
        hand: List[Tuple[int, int]],
        kozar_card: Tuple[int, int],
    ):
        # Store initial hand and trump card
        self.hand = hand
        self.kozar_card = kozar_card
        self.my_index = my_index
        self.num_of_players = num_of_players

    def first_attack(self) -> List[Tuple[int, int]]:
        # Attack with the lowest card
        if not self.hand:
            return []
        return [min(self.hand)]

    def optional_attack(self) -> List[Tuple[int, int]]:
        # Optionally attack with the next lowest card if possible
        if not self.hand:
            return []
        return [min(self.hand)] if random.random() < 0.5 else []

    def defend(self) -> Tuple[List[Tuple[int, int]], List[int]]:
        # Try to defend with the lowest card that can beat the attack
        attack_cards = self.get_attacking_table_cards()
        defence = []
        indexes = []
        for i, attack_card in enumerate(attack_cards):
            for card in self.hand:
                # Simple rule: defend if same suit and higher, or trump
                if (card[1] == attack_card[1] and card[0] > attack_card[0]) or (
                    card[1] == self.get_kozar_suit()
                    and attack_card[1] != self.get_kozar_suit()
                ):
                    defence.append(card)
                    indexes.append(i)
                    break
        if defence:
            return defence, indexes
        return [], []  # Take if can't defend
