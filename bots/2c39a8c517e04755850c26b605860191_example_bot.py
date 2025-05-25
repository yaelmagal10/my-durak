# To import durak_actions, use:
# from durak_actions import Output_actions, Input_actions

from durak_actions import Output_actions, Input_actions

RANKS = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def rank_value(card):
    return card[0]


class ExampleBot:
    name = "ExampleBot"

    def __call__(self, message, state=None):
        # message: tuple(Input_actions)
        # state: optional dict
        # For attack: message[0] in (Input_actions.FIRST_ATTACK, Input_actions.OPTIONAL_ATTACK)
        # For defend: message[0] == Input_actions.DEFENCE
        # The state is not used in this simple bot
        if state is None:
            state = {}
        # For attack, expect: (Input_actions.FIRST_ATTACK,) or (Input_actions.OPTIONAL_ATTACK,)
        # For defend, expect: (Input_actions.DEFENCE,)
        if message[0] in (Input_actions.FIRST_ATTACK, Input_actions.OPTIONAL_ATTACK):
            # state should contain 'hand', 'table', 'trump_suit'
            hand = state.get("hand", [])
            table = state.get("table", [])
            trump_suit = state.get("trump_suit", 0)
            if not hand:
                return [Output_actions.PASS]
            non_trumps = [c for c in hand if c[1] != trump_suit]
            if non_trumps:
                card = min(non_trumps, key=rank_value)
            else:
                card = min(hand, key=rank_value)
            return [Output_actions.ATTACK, [card]]
        elif message[0] == Input_actions.DEFENCE:
            hand = state.get("hand", [])
            attack_card = state.get("attack_card", None)
            trump_suit = state.get("trump_suit", 0)
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


# Export the bot instance
bot = ExampleBot()
