from durak_actions import Output_actions, Input_actions
from configurations import *
from random import shuffle, choice
from typing import List, Tuple, Optional, Any, Dict
from inspect import currentframe
from time import time
import signal


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


def __call_bot_subprocess(q, bot, args, kwargs):
    f = open("file.txt", "w")
    f.write("Subprocess started\n")
    f.close()
    try:
        result = bot.call(*args, **kwargs)
        q.put(("ok", result))
    except Exception as e:
        q.put(("err", e))


def call_bot(bot, *args, timeout: float = MAX_TIME_PER_TURN, **kwargs):
    if not USE_TIMING:
        return bot.call(*args, **kwargs)

    def raise_timeout_error(*args):
        raise TimeoutError

    signal.signal(signal.SIGALRM, raise_timeout_error)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        return bot.call(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def inform(player_bot: Any, message: Any, params: Tuple, state: Any) -> Any:
    # message, parameters, bot_state
    try:
        return call_bot(player_bot, message, *params, state)
    except Exception as e:
        print(f"\nline {currentframe().f_lineno}: Exception in inform calling player {player_bot} with {message}: {e}")
        return None


def inform_all(
    bots: List[Any],
    index_list: List[int],
    message: Any,
    params_list: List[Tuple],
    states: List[Any],
    log: List[List[str]],
) -> None:
    for bot_index, params in zip(index_list, params_list):
        result = inform(bots[bot_index], message, params, states[bot_index])
        if isinstance(result, dict):
            if "state" in result:
                states[bot_index] = result["state"]
            if "log" in result and isinstance(result["log"], list):
                log[bot_index].extend(result["log"])


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
    return (
        isinstance(card_list, list)
        and len(card_list) <= MAX_ATTACK_SIZE_AFTER_BURN
        and all(valid_card_format(card) for card in card_list)
    )


# possible actions: (ATTACK, attacking_card_list) , (DEFEND, defending_card_list, defending_index_list) , (TAKE) , (PASS) , (FORWARD, forwarding_card_list)
def valid_action_format(action: Any) -> bool:
    if not isinstance(action, list) or len(action) not in [1, 2, 3]:
        return False
    action_kind = action[0]
    if action_kind == Output_actions.ATTACK:
        if len(action) != 2:
            return False
        card_list = action[1]
        return valid_card_list_format(card_list)

    if action_kind == Output_actions.DEFEND:
        if len(action) != 3:
            return False
        card_list = action[1]
        index_list = action[2]
        if not valid_card_list_format(card_list) or not isinstance(index_list, list):
            return False
        if len(card_list) != len(index_list):
            return False
        if not all(isinstance(i, int) and 0 <= i for i in index_list):
            return False
        return True

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


def real_cards(card_list: List[Optional[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    return [card for card in card_list if card is not None]


def attack_vector(
    attack: List[Optional[Tuple[int, int]]], defence: List[Optional[Tuple[int, int]]]
) -> set:
    if attack[0] is None:  # New attack
        return set(range(13))
    return set(card[0] for card in attack + defence if card is not None)


def valid_to_attack(
    attacking_card: Tuple[int, int],
    attack: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
) -> bool:
    return attacking_card[0] in attack_vector(attack, defence)


def valid_to_defend(
    defending_card: Tuple[int, int], attacking_card: Tuple[int, int], kozar_suit: int
) -> bool:
    if defending_card[1] == attacking_card[1] and defending_card[0] > attacking_card[0]:
        return True
    if defending_card[1] == kozar_suit and attacking_card[1] != kozar_suit:
        return True
    return False


def defend_with_one_card(
    index: int,  # Index in the defence table
    attack: List[Optional[Tuple[int, int]]],  # Current attack vector
    defence: List[Optional[Tuple[int, int]]],  # Current defence vector
    defending_card: Tuple[int, int],  # Card to defend with
    defending_hand: List[Tuple[int, int]],  # Hand of the defending player
    kozar_suit: int,  # Suit of the kozar card (trump suit)
) -> int:
    if not isinstance(index, int):
        return 0
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


# assuming the parameters passed the valid_action_format check
def defend_with_card_list(
    index_list: List[int],  # Indices in the defence table
    defending_card_list: List[Tuple[int, int]],  # Card list to defend with
    attack: List[Optional[Tuple[int, int]]],  # Current attack vector
    defence: List[Optional[Tuple[int, int]]],  # Current defence vector
    defending_hand: List[Tuple[int, int]],  # Hand of the defending player
    kozar_suit: int,  # Suit of the kozar card (trump suit)
) -> List[Tuple[int, int]]:
    successful_defending_cards = []
    successful_index_list = []
    for index, card in zip(index_list, defending_card_list):
        if defend_with_one_card(
            index, attack, defence, card, defending_hand, kozar_suit
        ):
            successful_defending_cards.append(card)
            successful_index_list.append(index)
    return successful_defending_cards, successful_index_list


def forward_with_card_list(
    forwarding_card_list: List[Tuple[int, int]],
    attack: List[Optional[Tuple[int, int]]],
    forwarding_hand: List[Tuple[int, int]],
    num_of_allowed_forwarding_cards: int,
) -> List[Tuple[int, int]]:
    successful_forwarding_card_list = []
    for card in forwarding_card_list:
        if num_of_allowed_forwarding_cards <= 0:
            break
        if card not in forwarding_hand:
            continue
        if card[0] != attack[0][0]:
            continue
        forwarding_hand.remove(card)
        if None not in attack:
            attack.append(None)
        attack[attack.index(None)] = card  # Place card in the first available slot
        successful_forwarding_card_list.append(card)
        num_of_allowed_forwarding_cards -= 1

    return successful_forwarding_card_list


def attack_with_card_list(
    attack: List[Optional[Tuple[int, int]]],
    defence: List[Optional[Tuple[int, int]]],
    attacking_card_list: List[Tuple[int, int]],
    attacking_hand: List[Tuple[int, int]],
) -> int:
    if attack and all(card is not None for card in attack):
        return []
    successful_attacking_cards = []
    for card in attacking_card_list:
        if card not in attacking_hand:
            continue
        if not valid_to_attack(card, attack, defence):
            continue
        if None not in attack:
            break
        attacking_index = attack.index(None)  # First index available for attacking
        attacking_hand.remove(card)
        attack[attacking_index] = card
        successful_attacking_cards.append(card)
    return successful_attacking_cards


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

    if bot_names is None:
        bot_names = [f"Bot {i}" for i in range(len(bots))]
    num_of_players = len(bots)
    num_of_burned_cards = state["num_of_burned_cards"]
    attacker = state["attacker"]
    defender = state["defender"]
    lowest_trump = state["lowest_trump"]
    hands = [card_list_strs_to_tuples(h) for h in state["hands"]]

    def get_next_player(idx: int) -> int:
        deck = state.get("deck", [])
        if deck:
            return (idx + 1) % len(hands)
        for offset in range(1, len(hands) + 1):
            ni = (idx + offset) % len(hands)
            if len(hands[ni]) > 0:
                return ni
        return idx

    def get_active_players():
        deck = state.get("deck", [])
        return [i for i in range(num_of_players) if deck or len(hands[i]) != 0]

    table_attack = [card_str_to_tuple(c) for c in state["table_attack"]]
    table_defence = [card_str_to_tuple(c) for c in state["table_defence"]]
    max_attack_size = min(
        len(hands[defender]),
        MAX_ATTACK_SIZE_AFTER_BURN if state["burn"] else STARTING_MAX_ATTACK_SIZE,
    )
    if not table_attack or all(card is None for card in table_attack):
        table_attack, table_defence = make_table_size_of_max_attack_size(
            table_attack, table_defence, max_attack_size
        )
    if len(table_defence) < max_attack_size:
        table_defence.extend([None] * (max_attack_size - len(table_defence)))
    if len(table_attack) < max_attack_size:
        table_attack.extend([None] * (max_attack_size - len(table_attack)))
    end_of_round = False
    is_defence_successful = (
        True  # If the attack is successful, the defender will be the next player
    )
    trump_suit = SUITS.index(state["trump_suit"])
    # log is now a list of lists, one per bot
    log = [l[:] for l in state["log"]]
    bot_states = state.get("bot_states", [{} for _ in bots])
    curr_player = state["curr_player"]
    # Add a status list per bot if not present
    status = state.get("status", ["" for _ in bots])
    did_game_init_occur: bool = state.get("did_game_init_occur", False)

    def get_params_list():
        return [
            (
                hands[player_index].copy(),
                table_attack.copy(),
                table_defence.copy(),
                [len(hand) for hand in hands],
                defender,
                state["deck_count"],
            )
            for player_index in get_active_players()
        ]

    if not did_game_init_occur:

        params_list = get_params_list()
        for player_index, bot in enumerate(bots):
            result = inform(
                bot,
                (
                    Input_actions.GAME_INIT,
                    num_of_players,
                    player_index,
                    hands[player_index],
                    card_str_to_tuple(state["trump_card"]),
                    attacker,
                    lowest_trump,
                ),
                params_list[player_index],
                bot_states[player_index],
            )
            if isinstance(result, dict):
                if "state" in result:
                    bot_states[player_index] = result["state"]
                if "log" in result:
                    log[player_index].extend(result["log"])
                if "status" in result:
                    set_status(player_index, result["status"])
        did_game_init_occur = True

    def take() -> None:
        cards_to_hand = real_cards(table_attack + table_defence)
        inform_all(
            bots,
            get_active_players(),
            (Input_actions.TAKE_PASSIVE, defender, tuple(cards_to_hand)),
            get_params_list(),
            bot_states,
            log,
        )
        add_log(
            defender,
            f"Player {defender} took cards: {card_list_tuples_to_strs(cards_to_hand)}",
        )
        for card in cards_to_hand:
            hands[defender].append(card)

    # --- WINNER DETECTION AND REMOVAL ---
    # Helper to mark winners and remove them from the round
    def update_winners_and_remove():
        nonlocal hands, bots, bot_names, log, status, attacker, defender, curr_player, num_of_players
        # Mark as "WON" if hand is empty and not already marked
        for i, hand in enumerate(hands):
            if len(hand) == 0 and status[i] != "WON":
                status[i] = "WON"
                inform_all(
                    bots,
                    get_active_players(),
                    (Input_actions.WINNER_PASSIVE, curr_player),
                    get_params_list(),
                    bot_states,
                    log,
                )
                add_log(i, f"Player {i} has WON!")
        # Remove all players who have won from the round (but keep them in the state for UI)
        # Only active players participate in the round
        active_indices = [i for i, hand in enumerate(hands) if len(hand) > 0]
        if not active_indices:
            return

        def closest_active(idx):
            for offset in range(len(hands) + 1):
                ni = (idx + offset) % len(hands)
                if len(hands[ni]) > 0:
                    return ni
            return idx

        attacker = closest_active(attacker)
        defender = closest_active(defender)
        curr_player = closest_active(curr_player)
        # If only one player left, game is over (handled by frontend/end condition)

    # Helper to add a log entry for a specific bot
    def add_log(bot_idx, entry):
        if 0 <= bot_idx < len(log) and isinstance(entry, str):
            ts = time()
            log[bot_idx].append(f"[TS:{ts}]Game: {entry}")

    def add_logs(bot_idx, entries):
        if 0 <= bot_idx < len(log):
            log[bot_idx].extend(entries)

    # Helper to set a status entry for a specific bot
    def set_status(bot_idx, entry):
        if 0 <= bot_idx < len(status):
            status[bot_idx] = entry

    if curr_player == defender:
        if all(
            table_defence[index] != None or table_attack[index] == None
            for index in range(len(table_attack))
        ):
            burned_cards = tuple(real_cards(table_attack + table_defence))
            num_of_burned_cards += len(burned_cards)
            inform_all(
                bots,
                get_active_players(),
                (Input_actions.BURN, burned_cards),
                get_params_list(),
                bot_states,
                log,
            )
            state["burn"] = True
            add_log(
                defender,
                f"Player {defender} burned cards: {card_list_tuples_to_strs(burned_cards)}",
            )
            end_of_round = True
            is_defence_successful = True
        else:
            # Find the first attack card that is not defended
            attack_card = None
            for i in range(len(table_attack)):
                if table_attack[i] is not None and (table_defence[i] is None):
                    attack_card = table_attack[i]
                    break
            # Call bot with correct signature
            try:
                result = call_bot(
                    bots[curr_player],
                    (Input_actions.DEFENCE,),
                    hands[curr_player].copy(),
                    table_attack.copy(),
                    table_defence.copy(),
                    [len(hand) for hand in hands],
                    defender,
                    state["deck_count"],
                    bot_states[curr_player],
                )
            except Exception as e:
                add_log(curr_player, f"Error in defence of player {curr_player}: {e}")
                result = Output_actions.TAKE
            # If bot returns dict, extract log/status
            if isinstance(result, dict):
                action = result.get("action")
                bot_logs = result.get("log")
                bot_status = result.get("status")
                bot_states[curr_player] = result.get("state", bot_states[curr_player])
                if bot_logs:
                    add_logs(curr_player, bot_logs)
                if bot_status:
                    set_status(curr_player, bot_status)
            else:
                action = result
            if valid_action_format(action):
                if action[0] == Output_actions.DEFEND:
                    successful_defending_cards, successful_index_list = (
                        defend_with_card_list(
                            action[2],
                            action[1],
                            table_attack,
                            table_defence,
                            hands[curr_player],
                            trump_suit,
                        )
                    )
                    if len(successful_defending_cards) > 0:
                        inform_all(
                            bots,
                            get_active_players(),
                            (
                                Input_actions.DEFENCE_PASSIVE,
                                curr_player,
                                successful_defending_cards,
                                successful_index_list,
                            ),
                            get_params_list(),
                            bot_states,
                            log,
                        )
                        add_log(
                            curr_player,
                            f"Player {curr_player} defended with {card_list_tuples_to_strs(successful_defending_cards)}",
                        )
                    else:
                        take()
                        end_of_round = True
                        is_defence_successful = False

                        add_log(curr_player, f"Player {curr_player} took cards")
                elif action[0] == Output_actions.FORWARD:
                    num_of_allowed_forwarding_cards = len(
                        hands[get_next_player(defender)]
                    ) - len(real_cards(table_attack))

                    if (
                        any(c is not None for c in table_defence)
                        or num_of_allowed_forwarding_cards <= 0
                        or not valid_action_format(action)
                    ):
                        take()
                        end_of_round = True
                        is_defence_successful = False
                        add_log(defender, f"Player {defender} took cards")
                    else:
                        forwarding_card_list = action[1]
                        successful_forwarding_card_list = forward_with_card_list(
                            forwarding_card_list,
                            table_attack,
                            hands[defender],
                            num_of_allowed_forwarding_cards,
                        )
                        if len(successful_forwarding_card_list) > 0:
                            inform_all(
                                bots,
                                get_active_players(),
                                (
                                    Input_actions.FORWARD_PASSIVE,
                                    defender,
                                    successful_forwarding_card_list,
                                ),
                                get_params_list(),
                                bot_states,
                                log,
                            )
                            add_log(
                                defender,
                                f"Player {defender} forwarded cards {card_list_tuples_to_strs(successful_forwarding_card_list)}",
                            )
                            defender = get_next_player(defender)
                            allowed_attack_length = len(hands[defender])
                            assert (
                                len(table_attack) <= allowed_attack_length
                                or table_attack[allowed_attack_length] == None
                            )
                            table_attack = table_attack[:allowed_attack_length]
                            table_defence = table_defence[:allowed_attack_length]
                        else:
                            add_log(defender, "No valid forwarding cards, taking cards")
                            take()
                            end_of_round = True
                            is_defence_successful = False
                            add_log(defender, f"Player {defender} took cards")
                else:
                    take()
                    end_of_round = True
                    is_defence_successful = False
                    add_log(curr_player, f"Player {curr_player} took cards")

            else:
                add_log(curr_player, f"Invalid defence action: {action}. Taking cards.")
                take()
                end_of_round = True
                is_defence_successful = False
    else:  # If the current player is not the defender, they are attacking
        try:
            result = call_bot(
                bots[curr_player],
                (
                    (
                        Input_actions.FIRST_ATTACK
                        if all(card is None for card in table_attack)
                        else Input_actions.OPTIONAL_ATTACK
                    ),
                ),
                hands[curr_player].copy(),
                table_attack.copy(),
                table_defence.copy(),
                [len(hand) for hand in hands],
                defender,
                state["deck_count"],
                bot_states[curr_player],
            )
        except Exception as e:
            add_log(curr_player, f"Bot {bot_names[curr_player]} raised an exception during attack: {e}. Passing.\n")
            result = Output_actions.PASS
        if isinstance(result, dict):
            action = result.get("action")
            bot_logs = result.get("log")
            bot_status = result.get("status")
            bot_states[curr_player] = result.get("state", bot_states[curr_player])
            if bot_logs:
                add_logs(curr_player, bot_logs)
            if bot_status:
                set_status(curr_player, bot_status)
        else:
            action = result

        # The first attack case: player has to attack with at least 1 card.
        is_succesful_attack = False
        if all(card is None for card in table_attack):
            if valid_action_format(action) and action[0] == Output_actions.ATTACK:
                successful_attacking_cards = attack_with_card_list(
                    table_attack, table_defence, action[1], hands[curr_player]
                )
                is_succesful_attack = len(successful_attacking_cards) > 0
            if is_succesful_attack:
                inform_all(
                    bots,
                    get_active_players(),
                    (
                        Input_actions.FIRST_ATTACK_PASSIVE,
                        curr_player,
                        successful_attacking_cards,
                    ),
                    get_params_list(),
                    bot_states,
                    log,
                )
                add_log(
                    curr_player,
                    f"Player {curr_player} attacked with {card_list_tuples_to_strs(successful_attacking_cards)}",
                )
            if not is_succesful_attack:
                # If this is the first attack (all table_attack are None), pick a random card from hand and attack with it
                if hands[curr_player]:
                    random_card = choice(hands[curr_player])
                    add_log(
                        curr_player,
                        f"Invalid first attack action. Forcing attack with random card from hand: {random_card}"
                    )
                    card_singelton: List[Tuple[int, int]] = attack_with_card_list(
                        table_attack, table_defence, [random_card], hands[curr_player]
                    )
                    assert card_singelton == [
                        random_card
                    ], "Forced attack should always succeed"
                    inform_all(
                        bots,
                        get_active_players(),
                        (
                            Input_actions.FIRST_ATTACK_PASSIVE,
                            curr_player,
                            [random_card],
                        ),
                        get_params_list(),
                        bot_states,
                        log,
                    )
                    add_log(
                        curr_player,
                        f"Player {curr_player} attacked with {card_list_tuples_to_strs([random_card])} (forced random)",
                    )
                else:
                    raise ValueError(
                        f"Player {curr_player} has no cards to attack with in the first attack"
                    )

        # The regular attack case: player can attack with 0 or more cards.
        else:
            if valid_action_format(action) and action[0] == Output_actions.ATTACK:
                successful_attacking_cards = attack_with_card_list(
                    table_attack, table_defence, action[1], hands[curr_player]
                )
                is_succesful_attack = len(successful_attacking_cards) > 0

            if is_succesful_attack:
                inform_all(
                    bots,
                    get_active_players(),
                    (
                        Input_actions.OPTIONAL_ATTACK_PASSIVE,
                        curr_player,
                        successful_attacking_cards,
                    ),
                    get_params_list(),
                    bot_states,
                    log,
                )
                add_log(
                    curr_player,
                    f"Player {curr_player} attacked with {card_list_tuples_to_strs(successful_attacking_cards)}",
                )
            else:
                inform_all(
                    bots,
                    get_active_players(),
                    (Input_actions.PASS_PASSIVE, curr_player),
                    get_params_list(),
                    bot_states,
                    log,
                )
                add_log(curr_player, f"Unsuccessful attack. Player {curr_player} passes")
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
        # Deal to all players in cyclic order, starting from the attacker, skipping the defender.
        params_list = get_params_list()
        for i in range(num_of_players):
            player_index: int = (curr_attacker + i) % num_of_players
            if player_index == curr_defender:
                continue
            drawn_cards = []
            for _ in range(min(len(deck), CARDS_PER_HAND - len(hands[player_index]))):
                drawn_cards.append(deck.pop(0))
            hands[player_index].extend(drawn_cards)
            if len(drawn_cards) > 0:
                inform(
                    bots[player_index],
                    (Input_actions.TO_HAND, drawn_cards.copy()),
                    params_list[player_index],
                    bot_states[player_index],
                )
                add_log(
                    player_index,
                    f"Player {player_index} drew cards: {card_list_tuples_to_strs(drawn_cards)}",
                )
        # Deal to defender last
        drawn_cards = []
        for _ in range(min(len(deck), CARDS_PER_HAND - len(hands[curr_defender]))):
            drawn_cards.append(deck.pop(0))

        hands[curr_defender].extend(drawn_cards)
        if len(drawn_cards) > 0:
            inform(
                bots[curr_defender],
                (Input_actions.TO_HAND, drawn_cards.copy()),
                params_list[curr_defender],
                bot_states[curr_defender],
            )
            add_log(
                curr_defender,
                f"Player {curr_defender} drew cards: {card_list_tuples_to_strs(drawn_cards)}",
            )
        # Update deck in state
        state["deck"] = deck
        state["deck_count"] = len(deck)
        # Reset table attack and defence
        table_attack = []
        table_defence = []
        attacker = defender if is_defence_successful else get_next_player(defender)
        defender = get_next_player(attacker)
        curr_player = attacker  # Reset current player to the new attacker
    else:  # The round is not over, just increment curr_player and check for wins
        curr_player = get_next_player(curr_player)

    # Update winners and remove them from the round
    if state["deck_count"] == 0:
        update_winners_and_remove()
        pass

    # Always update deck_count before returning state
    state["deck_count"] = len(state.get("deck"))

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
        "did_game_init_occur": did_game_init_occur,
    }
