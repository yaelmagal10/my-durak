# To import durak_actions, use:
# from durak_actions import Output_actions, Input_actions

from durak_actions import Output_actions, Input_actions
from typing import List, Tuple, Optional, Any

RANKS: List[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def rank_value(card: Tuple[int, int]) -> int:
    return card[0]


class ExampleBot:
    # name: str = "ExampleBot"
    # If you provide a name field, it will be used in the game UI.
    # Otherwise, the bot's name will be as you chose it in the UI of uploading bots.

    def __call__(
        self,
        message: Tuple[Any, ...],
        hand: Optional[List[Tuple[int, int]]],
        table_or_attack_card: Any,
        trump_suit: Optional[int],
        bot_state: Optional[Any] = None,
    ) -> List[Any]:
        # message: tuple(Input_actions)
        # hand: list of (rank_index, suit_index)
        # table_or_attack_card: list of cards (for attack) or a single card (for defend)
        # trump_suit: int
        # bot_state: dict (optional)
        if message[0] in (Input_actions.FIRST_ATTACK, Input_actions.OPTIONAL_ATTACK):
            if not hand:
                return [Output_actions.PASS]
            non_trumps = [c for c in hand if c[1] != trump_suit]
            if non_trumps:
                card = min(non_trumps, key=rank_value)
            else:
                card = min(hand, key=rank_value)
            return [Output_actions.ATTACK, [card]]
        elif message[0] == Input_actions.DEFENCE:
            attack_card = table_or_attack_card
            # Forwarding logic: if attack table is a list of cards (not a single card)
            # and all cards have the same rank, and player has a card of that rank, forward
            if isinstance(attack_card, list) and len(attack_card) > 0:
                attack_ranks = set(c[0] for c in attack_card)
                if len(attack_ranks) == 1:
                    rank_to_forward = next(iter(attack_ranks))
                    if hand and any(c[0] == rank_to_forward for c in hand):
                        # Forward with the first card of that rank
                        card = next(c for c in hand if c[0] == rank_to_forward)
                        return [Output_actions.FORWARD, [card], [0]]
            if attack_card is None or not hand:
                return [Output_actions.TAKE]
            candidates = [
                c for c in hand if c[1] == attack_card[1] and c[0] > attack_card[0]
            ]
            if candidates:
                card = min(candidates, key=rank_value)
                return [Output_actions.DEFEND, [card], [0]]
            if attack_card[1] != trump_suit:
                trumps = [c for c in hand if c[1] == trump_suit]
                if trumps:
                    card = min(trumps, key=rank_value)
                    return [Output_actions.DEFEND, [card], [0]]
            return [Output_actions.TAKE]
        else:
            return [Output_actions.PASS]


bot: ExampleBot = ExampleBot()
