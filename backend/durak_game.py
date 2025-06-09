from random import shuffle, choice, randint, choices
from durak_actions import Output_actions, Input_actions
from typing import List, Tuple, Optional, Any, Dict
from inspect import currentframe

get_line = lambda: currentframe().f_lineno
CARDS_PER_HAND: int = 6
STARTING_MAX_ATTACK_SIZE: int = 5
MAX_ATTACK_SIZE_AFTER_BURN: int = 6
RANKS: List[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS: List[str] = ["♣", "♦", "♥", "♠"]


def pretty_print_state(state):
    print("Game State:")
    print(f"Trump Suit: {state['trump_suit']}")
    print(f"Trump Card: {state['trump_card']}")
    print("Hands:")
    for i, hand in enumerate(state["hands"]):
        print(f"  Player {i}: {', '.join(hand)}")
    print(f"Attacker: Player {state['attacker']}")
    print(f"Defender: Player {state['defender']}")
    print(f"Current Player: Player {state.get('curr_player', -1)}")
    print(f"Table Attack: {state['table_attack']}")
    print(f"Table Defence: {state['table_defence']}")
    print(f"Burn: {state['burn']}")
    print(f"Number of Burned Cards: {state['num_of_burned_cards']}")
    print("Deck:")
    for i, card in enumerate(state["deck"]):
        print(f"{card}", end="  " if i % 10 != 9 else "\n")
    print(f"Deck Count: {state['deck_count']}")


def card_str_to_tuple(card_str: Optional[str]) -> Optional[Tuple[int, int]]:
    if not card_str:
        return None
    if len(card_str) == 3:
        rank = "10"
        suit = card_str[2]
    else:
        rank = card_str[0]
        suit = card_str[1]
    return (RANKS.index(rank), SUITS.index(suit))


def inform(player: Any, message: Any, state: Any = None) -> Any:
    # Provide default values for bot call signature
    # message, hand, table_or_attack_card, trump_suit, bot_state=None
    # For inform, only message and state are relevant, so pass None for others
    try:
        return player.__call__(message, None, None, None, state)
    except:
        print(f"Error calling player {player}: {message}")
        return None


def inform_all(
    player_list: List[Any], message: Any, states: Optional[List[Any]] = None
) -> None:
    if states is None:
        for player, state in zip(player_list, states):
            inform(player, message, state)
    else:
        for player in player_list:
            inform(player, message)


def card_tuple_to_str(card_tuple: Optional[Tuple[int, int]]) -> str:
    if card_tuple is None:
        return ""
    return f"{RANKS[card_tuple[0]]}{SUITS[card_tuple[1]]}"


def card_list_strs_to_tuples(hand: List[str]) -> List[Optional[Tuple[int, int]]]:
    return [card_str_to_tuple(c) for c in hand]


def card_list_tuples_to_strs(hand: List[Optional[Tuple[int, int]]]) -> List[str]:
    return [card_tuple_to_str(c) for c in hand]


def valid_card_format(card: Any) -> bool:
    return (
        isinstance(card, tuple)
        and len(card) == 2
        and isinstance(card[0], int)
        and 0 <= card[0] < 13
        and isinstance(card[1], int)
        and 0 <= card[1] < 4
    )


def valid_card_list_format(card_list: Any) -> bool:
    return isinstance(card_list, list) and all(
        valid_card_format(card) for card in card_list
    )


# possible actions: (ATTACK, attacking_card_list) , (DEFEND, defending_card, defending_index) , (TAKE) , (PASS) , (FORWARD, forwarding_card)
def valid_action_format(action: Any) -> bool:
    if not isinstance(action, list) or len(action) not in [1, 2, 3]:
        return False
    action_kind = action[0]
    if action_kind == Output_actions.ATTACK:
        if len(action) != 2:
            return False
        card_list = action[1]
        if not isinstance(card_list, list):
            return False
        return valid_card_list_format(card_list)
    if action_kind == Output_actions.DEFEND:
        if len(action) != 3:
            return False
        card_list = action[1]
        index_list = action[2]
        if len(card_list) != len(index_list):
            return False
        return valid_card_list_format(card_list) and all(
            isinstance(index, int) and index >= 0 for index in index_list
        )
    if action_kind == Output_actions.TAKE:
        return len(action) == 1
    if action_kind == Output_actions.PASS:
        return len(action) == 1
    if action_kind == Output_actions.FORWARD:
        if len(action) != 2:
            return False
        card_list = action[1]
        if not isinstance(card_list, list):
            return False
        return valid_card_list_format(card_list)
    return False


def init_deck() -> List[Tuple[int, int]]:
    deck = list()
    for i in range(13):
        for j in range(4):
            deck.append((i, j))
    shuffle(deck)
    return deck


def real_cards(card_lst: List[Optional[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    return [card for card in card_lst if card is not None]


def attack_vector(
    attack: List[Optional[Tuple[int, int]]], defence: List[Optional[Tuple[int, int]]]
) -> set:
    # print(f"line 125: attack is {attack}, defence is {defence}")
    if attack[0] is None:  # New attack
        # print("New attack, returning full attack vector")
        return set(range(13))
    return set(card[0] for card in attack + defence if card is not None)


def valid_to_attack(
    attacking_card: Tuple[int, int],
    attack: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
) -> bool:
    # if not attacking_card[0] in attack_vector(attack, defence):
    # print(attacking_card)
    # print(f"Invalid attack: {attacking_card[0]} not in attack vector")

    return attacking_card[0] in attack_vector(attack, defence)


def valid_to_defend(
    defending_card: Tuple[int, int], attacking_card: Tuple[int, int], kozar_suit: int
) -> bool:
    if defending_card[1] == attacking_card[1] and defending_card[0] > attacking_card[0]:
        return True
    if defending_card[1] == kozar_suit and attacking_card[1] != kozar_suit:
        return True
    return False


def take(
    player_list: List[Any],
    player_index: int,
    attack: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
    player_hand: List[Tuple[int, int]],
    states: Optional[List[Any]] = None,
) -> None:
    cards_to_hand = real_cards(attack + defence)
    print(f"real cards = {cards_to_hand}")
    # inform(player_list[player_index], (Input_actions.TO_HAND, tuple(cards_to_hand)))
    inform_all(
        player_list,
        (Input_actions.TAKE_PASSIVE, player_index, tuple(cards_to_hand)),
        states,
    )
    for card in cards_to_hand:
        player_hand.append(card)
    print(f"actual hand: {player_hand}")


def defend(
    index: int,
    attack: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
    defending_card: Tuple[int, int],
    defending_hand: List[Tuple[int, int]],
    kozar_suit: int,
) -> int:
    if defending_card not in defending_hand:
        return 0
    if (
        index >= len(defence)
        or index < 0
        or defence[index] != None
        or attack[index] == None
    ):
        return 0
    if not valid_to_defend(defending_card, attack[index], kozar_suit):
        return 0

    defending_hand.remove(defending_card)
    defence[index] = defending_card
    return 1


def attack_action(
    attack_pointer: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
    attacking_card_lst: List[Tuple[int, int]],
    attacking_hand: List[Tuple[int, int]],
) -> int:
    if attack_pointer and all(card is not None for card in attack_pointer):
        return 0
    # attack_vec = attack_vector(attack, defence)
    count_attacks = 0
    for card in attacking_card_lst:
        if card not in attacking_hand:
            print("line 200: attacking card not in hand")
            continue
        if attack_pointer and all(c is not None for c in attack_pointer):
            continue
        if not valid_to_attack(card, attack_pointer, defence):
            print("line 205: invalid attack")
            continue
        attacking_index = attack_pointer.index(
            None
        )  # First index available for attacking
        attacking_hand.remove(card)
        attack_pointer[attacking_index] = card
        count_attacks += 1
    print(f"line {get_line()}: attack success")
    return count_attacks


def make_table_size_of_max_attack_size(
    table_attack: List[Optional[Tuple[int, int]]],
    table_defence: List[Optional[Tuple[int, int]]],
    max_attack_size: int,
) -> Tuple[List[Optional[Tuple[int, int]]], List[Optional[Tuple[int, int]]]]:
    while len(table_attack) > max_attack_size:
        table_attack.pop(None)
    while len(table_defence) > max_attack_size:
        table_defence.pop(None)
    if len(table_attack) < max_attack_size:
        table_attack.extend([None] * (max_attack_size - len(table_attack)))
    if len(table_defence) < max_attack_size:
        table_defence.extend([None] * (max_attack_size - len(table_defence)))
    return table_attack, table_defence


def advance_game_step(
    state: Dict[str, Any], bots: List[Any], bot_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    # pretty_print_state(state)
    if bot_names is None:
        bot_names = [f"Bot {i+1}" for i in range(len(bots))]
    num_of_players = len(bots)
    num_of_burned_cards = state["num_of_burned_cards"]
    attacker = state["attacker"]
    defender = state["defender"]
    hands = [card_list_strs_to_tuples(h) for h in state["hands"]]
    table_attack = [card_str_to_tuple(c) for c in state["table_attack"]]
    table_defence = [card_str_to_tuple(c) for c in state["table_defence"]]
    if not table_attack or all(card is None for card in table_attack):
        max_attack_size = min(
            len(hands[defender]),
            MAX_ATTACK_SIZE_AFTER_BURN if state["burn"] else STARTING_MAX_ATTACK_SIZE,
        )
        table_attack, table_defence = make_table_size_of_max_attack_size(
            table_attack, table_defence, max_attack_size
        )
    end_of_round = False
    # If the attack is successful, the defender will be the next player
    is_defence_succesful = True
    trump_suit = SUITS.index(state["trump_suit"])
    # log is now a list of lists, one per bot
    log = [l[:] for l in state["log"]]
    bot_states = state.get("bot_states", [{} for _ in bots])
    curr_player = state["curr_player"]
    # Add a status list per bot if not present
    status = state.get("status", ["" for _ in bots])

    # --- WINNER DETECTION AND REMOVAL ---
    # Helper to mark winners and remove them from the round
    def update_winners_and_remove():
        nonlocal hands, bots, bot_names, log, status, attacker, defender, curr_player, num_of_players
        # Mark as "WON" if hand is empty and not already marked
        for i, hand in enumerate(hands):
            if len(hand) == 0 and status[i] != "WON":
                status[i] = "WON"
                log[i].append("Player has WON!")
        # Remove all players who have won from the round (but keep them in the state for UI)
        # Only active players participate in the round
        active_indices = [i for i, hand in enumerate(hands) if len(hand) > 0]
        if not active_indices:
            return

        # Update attacker, defender, curr_player to next active if needed
        def next_active(idx):
            for offset in range(1, len(hands) + 1):
                ni = (idx + offset) % len(hands)
                if len(hands[ni]) > 0:
                    return ni
            return idx

        if len(hands[attacker]) == 0:
            attacker = next_active(attacker)
        if len(hands[defender]) == 0 or defender == attacker:
            defender = next_active(attacker)
        if len(hands[curr_player]) == 0:
            curr_player = next_active(curr_player)
        # If only one player left, game is over (handled by frontend/end condition)

    # Helper to add a log entry for a specific bot
    def add_log(bot_idx, entry):
        if 0 <= bot_idx < len(log):
            log[bot_idx].append(entry)

    # Helper to set a status entry for a specific bot
    def set_status(bot_idx, entry):
        if 0 <= bot_idx < len(status):
            status[bot_idx] = entry

    if curr_player == defender:
        if all(
            table_defence[index] != None or table_attack[index] == None
            for index in range(len(table_attack))
        ):
            print(
                f"line {get_line()} (burn): attack is {table_attack}, defence is {table_defence}"
            )
            burned_cards = tuple(real_cards(table_attack + table_defence))
            num_of_burned_cards += len(burned_cards)
            inform_all(bots, (Input_actions.BURN, burned_cards), bot_states)
            state["burn"] = True
            add_log(
                defender,
                f"Player {defender+1} burned cards: {card_list_tuples_to_strs(burned_cards)}",
            )
            end_of_round = True
            is_defence_succesful = True
        else:
            # Prepare arguments for defence
            hand = hands[curr_player]
            # Find the first attack card that is not defended
            attack_card = None
            for i in range(len(table_attack)):
                if table_attack[i] is not None and (table_defence[i] is None):
                    attack_card = table_attack[i]
                    break
            # Call bot with correct signature
            try:
                result = bots[curr_player].__call__(
                    (Input_actions.DEFENCE,),
                    hand,
                    attack_card,
                    trump_suit,
                    bot_states[curr_player],
                )
            except:
                print(
                    f"line {get_line()}: Bot {bot_names[curr_player]} raised an exception during defence"
                )
                result = Output_actions.TAKE
            # If bot returns dict, extract log/status
            if isinstance(result, dict):
                action = result.get("action")
                bot_log = result.get("log")
                bot_status = result.get("status")
                if bot_log:
                    add_log(curr_player, bot_log)
                if bot_status:
                    set_status(curr_player, bot_status)
            else:
                action = result
            if valid_action_format(action):
                print(f"line {get_line()}: Defender action is valid")
                if action[0] == Output_actions.DEFEND:
                    if defend(
                        action[2][0],
                        table_attack,
                        table_defence,
                        action[1][0],
                        hands[curr_player],
                        trump_suit,
                    ):
                        inform_all(
                            bots,
                            (
                                Input_actions.DEFENCE_PASSIVE,
                                curr_player,
                                action[1][0],
                                action[2][0],
                            ),
                            bot_states,
                        )
                        add_log(
                            curr_player,
                            f"Player {curr_player+1} defended with {card_tuple_to_str(action[1][0])}",
                        )
                    else:
                        take(
                            bots,
                            curr_player,
                            table_attack,
                            table_defence,
                            hands[curr_player],
                            bot_states,
                        )
                        end_of_round = True
                        is_defence_succesful = False

                        add_log(curr_player, f"Player {curr_player+1} took cards")
                elif action[0] == Output_actions.FORWARD:
                    num_of_allowed_forwarding_cards = min(
                        max_attack_size,
                        len(hands[(defender + 1) % num_of_players]),  # YOAD
                    ) - len(real_cards(table_attack))
                    if (
                        table_defence[0] != None
                        or num_of_allowed_forwarding_cards <= 0
                        or not valid_action_format(action)
                        or table_defence
                        and any(card is not None for card in table_defence)
                    ):
                        take(
                            bots,
                            defender,
                            table_attack,
                            table_defence,
                            hands[defender],
                            bot_states,
                        )
                        end_of_round = True
                        is_defence_succesful = False
                        add_log(defender, f"Player {defender+1} took cards")
                    else:
                        forwarding_cards = action[1]
                        if len(forwarding_cards) > num_of_allowed_forwarding_cards:
                            take(
                                bots,
                                defender,
                                table_attack,
                                table_defence,
                                hands[defender],
                                bot_states,
                            )
                            end_of_round = True
                            is_defence_succesful = False
                            add_log(defender, f"Player {defender+1} took cards")
                        else:
                            for card in forwarding_cards:
                                if card not in hands[defender] or card[0] not in [
                                    c[0] for c in table_attack if c is not None
                                ]:
                                    take(
                                        bots,
                                        defender,
                                        table_attack,
                                        table_defence,
                                        hands[defender],
                                        bot_states,
                                    )
                                    end_of_round = True
                                    is_defence_succesful = False
                                    add_log(defender, f"Player {defender+1} took cards")
                                    break
                                else:
                                    table_attack.append(forwarding_cards)
                                    hands[defender].remove(forwarding_cards)
                                    inform_all(
                                        bots,
                                        (
                                            Input_actions.FORWARD_PASSIVE,
                                            defender,
                                            forwarding_cards,
                                        ),
                                        bot_states,
                                    )
                                    table_attack.append(forwarding_cards)
                                    defender = (defender + 1) % num_of_players
                                    curr_player = defender
                                    add_log(
                                        defender,
                                        f"Player {defender+1} forwarded cards {card_list_tuples_to_strs(forwarding_cards)}",
                                    )
                else:
                    take(
                        bots,
                        curr_player,
                        table_attack,
                        table_defence,
                        hands[curr_player],
                        bot_states,
                    )
                    end_of_round = True
                    is_defence_succesful = False
                    add_log(curr_player, f"Player {curr_player+1} took cards")

            else:
                print(f"line {get_line()}: invalid defence action")
                take(
                    bots,
                    curr_player,
                    table_attack,
                    table_defence,
                    hands[curr_player],
                    bot_states,
                )
                end_of_round = True
                is_defence_succesful = False
                add_log(curr_player, f"Player {curr_player+1} took cards")
    else:  # If the current player is not the defender, they are attacking
        # Prepare arguments for attack
        hand = hands[curr_player]
        table = [c for c in table_attack if c is not None]
        try:
            result = bots[curr_player].__call__(
                (
                    (
                        Input_actions.FIRST_ATTACK
                        if all(card is None for card in table_attack)
                        else Input_actions.OPTIONAL_ATTACK
                    ),
                ),
                hand,
                table,
                trump_suit,
                bot_states[curr_player],
            )
        except:
            print(
                f"line {get_line()}: Bot {bot_names[curr_player]} raised an exception during attack"
            )
            result = Output_actions.PASS
        if isinstance(result, dict):
            action = result.get("action")
            bot_log = result.get("log")
            bot_status = result.get("status")
            if bot_log:
                add_log(curr_player, bot_log)
            if bot_status:
                set_status(curr_player, bot_status)
        else:
            action = result

        # The first attack case: player has to attack with at least 1 card.
        is_succesful_attack = False
        if all(card is None for card in table_attack):
            if valid_action_format(action) and action[0] == Output_actions.ATTACK:
                is_succesful_attack = attack_action(
                    table_attack, table_defence, action[1], hands[curr_player]
                )
            if is_succesful_attack:
                inform_all(
                    bots,
                    (Input_actions.FIRST_ATTACK_PASSIVE, curr_player, action[1]),
                    bot_states,
                )
                add_log(
                    curr_player,
                    f"Player {curr_player+1} attacked with {card_list_tuples_to_strs(action[1])}",
                )
            if not is_succesful_attack:
                print("line 476: invalid first attack action")
                # If this is the first attack (all table_attack are None), pick a random card from hand and attack with it
                if hands[curr_player]:
                    random_card = choice(
                        [c for c in hands[curr_player] if c is not None]
                    )
                    print(
                        f"line {get_line()}: Forcing attack with random card from hand: {random_card}"
                    )
                    res = attack_action(
                        table_attack, table_defence, [random_card], hands[curr_player]
                    )
                    assert res == 1, "Forced attack should always succeed"
                    inform_all(
                        bots,
                        (
                            Input_actions.FIRST_ATTACK_PASSIVE,
                            curr_player,
                            [random_card],
                        ),
                        bot_states,
                    )
                    add_log(
                        curr_player,
                        f"Player {curr_player+1} attacked with {card_tuple_to_str(random_card)} (forced random)",
                    )
                else:
                    print(f"line {get_line()}: No cards to attack with")
                    print(
                        "THIS SHOULD NOT HAPPEN"
                    )  # YOAD: This is related to the end game  where the player who starts the attack has no cards.

        # The regular attack case: player can attack with 0 or more cards.
        else:
            if valid_action_format(action) and action[0] == Output_actions.ATTACK:
                is_succesful_attack = attack_action(
                    table_attack, table_defence, action[1], hands[curr_player]
                )

            if is_succesful_attack:
                inform_all(
                    bots,
                    (
                        Input_actions.OPTIONAL_ATTACK_PASSIVE,
                        curr_player,
                        action[1],
                    ),
                    bot_states,
                )
                add_log(
                    curr_player,
                    f"Player {curr_player+1} attacked with {card_list_tuples_to_strs(action[1])}",
                )
            else:
                inform_all(
                    bots,
                    (Input_actions.PASS_PASSIVE, curr_player),
                    bot_states,
                )
                add_log(curr_player, f"Player {curr_player+1} passes")
                print(
                    f"line {get_line()}: regular attack for player {curr_player+1} has failed, passing turn"
                )
    # --- Deal cards to players after round ends ---
    if end_of_round:
        # Get deck from state (if present), else empty
        deck = state.get("deck", [])
        # Convert deck from string to tuple if needed
        if deck and isinstance(deck[0], str):
            deck = [card_str_to_tuple(c) for c in deck]
        # The player who started the attack
        curr_attacker = attacker
        curr_defender = defender
        # Deal to attacker first
        count_pops = 0
        for _ in range(min(len(deck), CARDS_PER_HAND - len(hands[curr_attacker]))):
            hands[curr_attacker].append(deck.pop())
            count_pops += 1
        # Deal to all other players in cyclic order, skipping defender
        for i in range(1, num_of_players):
            player_index = (curr_attacker + i) % num_of_players
            if player_index == curr_defender:
                continue
            for _ in range(min(len(deck), CARDS_PER_HAND - len(hands[player_index]))):
                hands[player_index].append(deck.pop())
                count_pops += 1
        # Deal to defender last
        for _ in range(min(len(deck), CARDS_PER_HAND - len(hands[curr_defender]))):
            hands[curr_defender].append(deck.pop())
            count_pops += 1
        # Update deck in state
        print(f"Dealt {count_pops} cards from deck")
        state["deck"] = deck
        state["deck_count"] = len(deck)
        print(f"Remaining deck count: {len(deck)}")
        # Reset table attack and defence
        table_attack = []
        table_defence = []
        attacker = defender if is_defence_succesful else (defender + 1) % num_of_players
        defender = (attacker + 1) % num_of_players  # YOAD
        curr_player = attacker  # Reset current player to the new attacker
        # Update winners and remove them from the round
        update_winners_and_remove()
    else:
        curr_player = (curr_player + 1) % num_of_players
        update_winners_and_remove()

    # Always update deck_count before returning state
    state["deck_count"] = len(state.get("deck", []))

    hands_str = [card_list_tuples_to_strs(h) for h in hands]
    table_attack_str = [card_tuple_to_str(c) for c in table_attack]
    table_defence_str = [card_tuple_to_str(c) for c in table_defence]

    return {
        **state,
        "hands": hands_str,
        "table_attack": table_attack_str if not end_of_round else [],
        "table_defence": table_defence_str if not end_of_round else [],
        "attacker": attacker,
        "defender": defender,
        "log": log,
        "bot_states": bot_states,
        "curr_player": curr_player,
        "status": status,
        "num_of_burned_cards": num_of_burned_cards,
        "deck_count": state["deck_count"],
    }
