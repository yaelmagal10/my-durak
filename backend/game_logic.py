def advance_game_step(state, bots, bot_names=None):
    # This is a minimal example for step-by-step play
    # You should expand this for full Durak logic!
    if bot_names is None:
        bot_names = [f"Bot {i+1}" for i in range(len(bots))]
    attacker = state["attacker"]
    defender = state["defender"]
    hands = [[{"rank": c[:-1], "suit": c[-1]} for c in h] for h in state["hands"]]
    trump_suit = state["trump_suit"]
    table = (
        [{"rank": c[:-1], "suit": c[-1]} for c in state["table"]]
        if state["table"]
        else []
    )
    log = state["log"][:]

    # If table is empty, attacker attacks
    if not table:
        attack_card = bots[attacker].attack(hands[attacker], [], trump_suit)
        if attack_card:
            table.append(attack_card)
            hands[attacker] = [
                c
                for c in hands[attacker]
                if not (
                    c["rank"] == attack_card["rank"]
                    and c["suit"] == attack_card["suit"]
                )
            ]
            log.append(
                f"Player {attacker+1} ({bot_names[attacker]}) attacks with {attack_card['rank']}{attack_card['suit']}"
            )
    else:
        # Defender tries to defend
        attack_card = table[-1]
        defend_card = bots[defender].defend(hands[defender], attack_card, trump_suit)
        if defend_card:
            table.append(defend_card)
            hands[defender] = [
                c
                for c in hands[defender]
                if not (
                    c["rank"] == defend_card["rank"]
                    and c["suit"] == defend_card["suit"]
                )
            ]
            log.append(
                f"Player {defender+1} ({bot_names[defender]}) defends with {defend_card['rank']}{defend_card['suit']}"
            )
        else:
            log.append(
                f"Player {defender+1} ({bot_names[defender]}) cannot defend and takes the cards."
            )
            hands[defender].extend(table)
            table = []
            # Next round: attacker stays, defender moves to next
            defender = (defender + 1) % len(hands)
            if defender == attacker:
                attacker = (attacker + 1) % len(hands)
                defender = (attacker + 1) % len(hands)

    # Convert hands and table back to string format
    hands_str = [[f"{c['rank']}{c['suit']}" for c in h] for h in hands]
    table_str = [f"{c['rank']}{c['suit']}" for c in table]
    return {
        **state,
        "hands": hands_str,
        "table": table_str,
        "attacker": attacker,
        "defender": defender,
        "log": log,
    }
