from enum import Enum


class Input_actions(Enum):
    FIRST_ATTACK = 0  # attack with a card list, you may pass.
    OPTIONAL_ATTACK = 1  # attack with a card list, you must attack.
    DEFENCE = 2  # defend with cards

    TO_HAND = 7  # info about the cards you took from deck to hand. Format: (Input_actions.TO_HAND, card_list)
    BURN = 8  # the attack was burned. Format: (Input_actions.BURN, card_list)
    GAME_INIT = 9  # info about game initialization. Format: (Input_actions.GAME_INIT, num_of_players, player_index, hand,  kozar_card)
    OPTIONAL_ATTACK_PASSIVE = 10  # info about an optional attack. Format: (OPTIONAL_ATTACK_PASSIVE, attacker_index, card_list)
    FIRST_ATTACK_PASSIVE = 11  # info about a beginning of a new attack. Format: (FIRST_ATTACK_PASSIVE, attacker_index, card_list)
    DEFENCE_PASSIVE = 12  # info about a defence. Format: (DEFENCE_PASSIVE, defender_index, defending_cards, indexes)
    TAKE_PASSIVE = 13  # the defender took the attack cards to his hands. Format: (TAKE_PASSIVE, defender_index, card_list)
    FORWARD_PASSIVE = 14  # the defender forwarded the attack. Format: (FORWARD_PASSIVE, forwarder_index, card_list)
    PASS_PASSIVE = 15  # A player passed (as an optional attacker he chose not to attack). Format: (PASS_PASSIVE, passer_index)
    WINNER_PASSIVE = 16  # info about a player who won the game. Format: (WINNER_PASSIVE, winner_index)


class Output_actions(Enum):
    ATTACK = 20  # player attacks with a card list
    DEFEND = 21  # player defends with a card list and an index list
    TAKE = 22  # player takes the cards from the attack (as an unsuccessful defender)
    PASS = 23  # player does nothing (as an attacker in an existing attack)
    FORWARD = 24  # player forwards an attack (as a current defender)
