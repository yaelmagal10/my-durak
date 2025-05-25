# To import durak_actions, use:
# from durak_actions import Output_actions, Input_actions

from durak_actions import Output_actions, Input_actions

RANKS = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def rank_value(card):
    return card[0]


def __call__(message, hand, table_or_attack_card, trump_suit, bot_state=None):
    # message: tuple(Input_actions)
    # hand: list of (rank_index, suit_index)
    # table_or_attack_card: list of cards (for attack) or a single card (for defend)
    # trump_suit: int
    # bot_state: dict (optional)
    if message[0] in (Input_actions.FIRST_ATTACK, Input_actions.OPTIONAL_ATTACK):
        # Attack step: play the lowest non-trump, else lowest trump
        if not hand:
            return []
        non_trumps = [c for c in hand if c[1] != trump_suit]
        if non_trumps:
            card = min(non_trumps, key=rank_value)
        else:
            card = min(hand, key=rank_value)
        return [card]
    elif message[0] == Input_actions.DEFENCE:
        attack_card = table_or_attack_card
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
        return []


# For compatibility with loader
attack = lambda hand, table, trump_suit, bot_state=None: __call__(
    (Input_actions.FIRST_ATTACK,), hand, table, trump_suit, bot_state
)
defend = lambda hand, attack_card, trump_suit, bot_state=None: __call__(
    (Input_actions.DEFENCE,), hand, attack_card, trump_suit, bot_state
)
