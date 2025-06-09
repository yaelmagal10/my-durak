from enum import Enum


class Input_actions(Enum):
    OPTIONAL_ATTACK = 0  # attack with a card list
    FIRST_ATTACK = 1
    DEFENCE = 2  # defend with a card

    TO_HAND = 7  # info about the cards you took from deck to hand
    BURN = 8  # the attack was burned
    GAME_INIT = 9  # info about game initialization
    OPTIONAL_ATTACK_PASSIVE = 10  # info about an optional attack
    FIRST_ATTACK_PASSIVE = 11  # info about a beginning of a new attack
    DEFENCE_PASSIVE = 12  # info about a defence
    TAKE_PASSIVE = 13  # the defender took the attack cards to his hands
    FORWARD_PASSIVE = 14  # the defender forwarded the attack
    PASS_PASSIVE = 15  # do nothing (as an attacker in an existing attack)


class Output_actions(Enum):
    ATTACK = 20  # attack with a card list
    DEFEND = 21  # defend with a card
    TAKE = 22  # take the cards from the attack (as an unsuccessful defender)
    PASS = 23  # do nothing (as an attacker in an existing attack)
    FORWARD = 24  # forward an attack (as a current defender)
