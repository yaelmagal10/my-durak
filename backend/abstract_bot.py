from durak_actions import Input_actions, Output_actions
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Dict


class AbstractBot(ABC):
    def listen_optional_attack(
        self, attacker_index: int, card_list: List[Tuple[int, int]]
    ):
        """Listen to a non-starting attack from a player."""
        pass

    def listen_first_attack(
        self, attacker_index: int, card_list: List[Tuple[int, int]]
    ):
        """Listen to the starting attack from a player."""
        pass

    def listen_defence(
        self,
        defender_index: int,
        defending_cards: List[Tuple[int, int]],
        indexes: List[int],
    ):
        """Listen to a defence from a player."""
        pass

    def listen_take(self, defender_index: int, card_list: List[Tuple[int, int]]):
        """Listen to a player taking the attack cards to his hand."""
        pass

    def listen_forward(self, forwarder_index: int, card_list: List[Tuple[int, int]]):
        """Listen to a player forwarding the attack."""
        pass

    def listen_pass(self, passer_index: int):
        """Listen to a player passing (as an optional attacker)."""
        pass

    def listen_burn(self, card_list: List[Tuple[int, int]]):
        """Listen to a burn of the attack cards."""
        pass

    def listen_cards_drawn_to_hand(self, card_list: List[Tuple[int, int]]):
        """Listen to drawing cards from the deck to my hand."""
        pass

    def listen_winner(self, winner_index: int):
        """Listen to a player who won the game."""
        pass

    def game_init(
        self,
        num_of_players: int,
        my_index: int,
        hand: List[Tuple[int, int]],
        kozar_card: Tuple[int, int],
        first_player: int,
        lowest_kozar: int
    ):
        """Gets called when the game is initialized."""
        pass

    @abstractmethod
    def first_attack(self) -> List[Tuple[int, int]]:
        """Start an attack with a card list (mandatory)."""
        pass

    @abstractmethod
    def optional_attack(self) -> List[Tuple[int, int]]:
        """Add cards to an existing attack (optional). Return an empty list for pass."""
        pass

    @abstractmethod
    def defend(self) -> Tuple[List[Tuple[int, int]], List[int]]:
        """Defend against an attack. Return a list of cards and list of indexes
        representing which attacking card each card is defending.
        To take, return an empty list of cards and an empty list of indexes.
        To forward, return a list of forwarding cards and an empty list of indexes.
        To defend, return both lists as described above."""
        pass

    def get_original_index(self, current_index: int) -> int:
        """Get the original index of a player based on its current index.
        If something is wrong, return -1."""
        if not self.__active_players:
            return -1
        if current_index < 0 or current_index >= len(self.__active_players):
            return -1
        return self.__active_players[current_index]

    def get_current_index(self, original_index: int) -> int:
        """Get the current index of a player based on its original index.
        If something is wrong, return -1."""
        if not self.__active_players:
            return -1
        if original_index not in self.__active_players:
            return -1
        return self.__active_players.index(original_index)

    def get_hand(self) -> List[Tuple[int, int]]:
        """Get the current hand of the bot."""
        return self.__hand

    def get_kozar_suit(self) -> int:
        """Get the suit of the kozar card."""
        return self.__kozar_card[1] if self.__kozar_card else -1

    def get_kozar_card(self) -> Tuple[int, int]:
        """Get the kozar card."""
        return self.__kozar_card if self.__kozar_card else (-1, -1)

    def get_table_attack(self) -> List[Tuple[int, int]]:
        """Get the current attacking cards on the table."""
        return self.__table_attack

    def get_table_defence(self) -> List[Tuple[int, int]]:
        """Get the current defending cards on the table."""
        return self.__table_defence

    def get_my_index(self) -> int:
        """Get the index of the bot in the game."""
        return self.__my_index if hasattr(self, "__my_index") else -1

    def get_raw_events(self) -> List[Tuple]:
        """Get all the raw events that the bot has received, by order."""
        return self.__events if hasattr(self, "__events") else []

    def call(
        self,
        event: Tuple,
        hand: List,
        table_attack: List,
        table_defence: List,
        state: Dict[str, Any],
    ):
        # print(f"state given is: {state}")
        self.__dict__.update(state if state is not None else {})
        if not hasattr(self, "__events"):
            self.__events = []
        self.__events.append(event)
        action = event[0] if event else None
        self.__hand = hand
        self.__table_attack = table_attack
        self.__table_defence = table_defence
        ret_dict = {}
        match action:
            case Input_actions.OPTIONAL_ATTACK:
                cards = self.optional_attack()
                if isinstance(cards, list) and len(cards) == 0:
                    ret_dict["action"] = [Output_actions.PASS]
                else:
                    ret_dict["action"] = [Output_actions.ATTACK, cards]
            case Input_actions.FIRST_ATTACK:
                cards = self.first_attack()
                ret_dict["action"] = [Output_actions.ATTACK, cards]
            case Input_actions.DEFENCE:
                cards, indexes = self.defend()
                if cards is None or len(cards) == 0:
                    ret_dict["action"] = [Output_actions.TAKE]
                elif indexes is None or len(indexes) == 0:
                    ret_dict["action"] = [Output_actions.FORWARD, cards]
                else:
                    ret_dict["action"] = [Output_actions.DEFEND, cards, indexes]
            case Input_actions.OPTIONAL_ATTACK_PASSIVE:
                self.listen_optional_attack(event[1], event[2])
            case Input_actions.FIRST_ATTACK_PASSIVE:
                self.listen_first_attack(event[1], event[2])
            case Input_actions.DEFENCE_PASSIVE:
                self.listen_defence(event[1], event[2], event[3])
            case Input_actions.TAKE_PASSIVE:
                self.listen_take(event[1], event[2])
            case Input_actions.FORWARD_PASSIVE:
                self.listen_forward(event[1], event[2])
            case Input_actions.PASS_PASSIVE:
                self.listen_pass(event[1])
            case Input_actions.BURN:
                self.listen_burn(event[1])
            case Input_actions.TO_HAND:
                self.listen_cards_drawn_to_hand(event[1])
            case Input_actions.GAME_INIT:
                self.__active_players = [i for i in range(event[1])]
                self.__my_index = event[2]
                self.__hand = event[3]
                self.__kozar_card = event[4]
                self.game_init(event[1], event[2], event[3], event[4], event[5], event[6])
            case Input_actions.WINNER_PASSIVE:
                self.__active_players.pop(event[1])
                self.listen_winner(event[1])
            case _:
                raise ValueError(f"Unknown action: {action}")
        ret_dict["state"] = self.__dict__
        return ret_dict
