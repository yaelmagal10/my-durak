# Required interface:
# - attack(hand, table, trump_suit) -> card
# - defend(hand, attack_card, trump_suit) -> card


def rank_value(rank):
    order = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    return order.index(rank)


def attack(hand, table, trump_suit):
    # hand: list of {"rank": str, "suit": str}
    # table: list of cards on table
    # trump_suit: str
    # Play the lowest card
    if not hand:
        return None
    return min(hand, key=lambda c: (c["suit"] == trump_suit, rank_value(c["rank"])))


def defend(hand, attack_card, trump_suit):
    # Try to beat attack_card with same suit and higher rank
    candidates = [
        c
        for c in hand
        if c["suit"] == attack_card["suit"]
        and rank_value(c["rank"]) > rank_value(attack_card["rank"])
    ]
    if candidates:
        return min(candidates, key=lambda c: rank_value(c["rank"]))
    # Otherwise, use lowest trump if attack_card is not trump
    if attack_card["suit"] != trump_suit:
        trumps = [c for c in hand if c["suit"] == trump_suit]
        if trumps:
            return min(trumps, key=lambda c: rank_value(c["rank"]))
    return None
