# Durak Game Logic & Bot Integration Documentation

## What the Game Logic Needs to Provide

- **Game State Management:**  
  - Maintain the state of the game, including hands, table, trump suit, attacker, defender, and log.
  - Advance the game by one step (attack or defend) when requested.
  - Support step-by-step play and auto-play (repeated steps until game end).

- **API Endpoints (see `main.py`):**
  - `/api/games` (POST): Start a new game with a list of bot filenames.
  - `/api/games/{game_id}/step` (POST): Advance the game by one step.
  - `/api/bots` (POST): Upload a new bot.
  - `/api/bots` (GET): List available bots.

- **Bot Integration:**  
  - Dynamically load Python files implementing the bot interface.
  - Call `attack` and `defend` functions on each bot as needed.

## What is Currently Implemented

- **Minimal Step-by-Step Logic:**  
  - The function `advance_game_step(state, bots, bot_names)` in `game_logic.py` advances the game by one attack or defend action.
  - The game state tracks hands, table, attacker, defender, trump suit, and log.
  - The backend supports uploading and listing bots, and running games with any combination of uploaded bots.

- **Bot Interface:**  
  - Each bot must be a Python file with a function:
    - `def bot(input_data: dict) -> dict`
      - `input_data` contains:
        - `"action"`: `"attack"` or `"defend"`
        - `"hand"`: list of card dicts
        - `"table"` or `"attack_card"`: cards on table or card to defend against
        - `"trump_suit"`: str
        - `"bot_state"`: dict (optional, for persistent state)
      - Return a dict:
        - `"action"`: action string
        - `"card"`: card dict or None
        - `"bot_state"`: dict (state to save for next turn)
  - For compatibility, you may also provide `attack` and `defend` wrappers.
  - Example bot: `backend/example_bot.py`

- **Frontend:**  
  - Allows uploading bots, selecting bots for a game, and running games step-by-step or in auto mode.

## How to Create a Bot

1. **Write a Python file with the following interface:**
    ```python
    # my_bot.py
    def bot(input_data):
        # input_data: dict with keys "action", "hand", "table"/"attack_card", "trump_suit", "bot_state"
        # Return a dict: {"action": ..., "card": ..., "bot_state": ...}
        pass

    # Optionally, for compatibility:
    attack = lambda hand, table, trump_suit, bot_state=None: bot({
        "action": "attack",
        "hand": hand,
        "table": table,
        "trump_suit": trump_suit,
        "bot_state": bot_state or {},
    })
    defend = lambda hand, attack_card, trump_suit, bot_state=None: bot({
        "action": "defend",
        "hand": hand,
        "attack_card": attack_card,
        "trump_suit": trump_suit,
        "bot_state": bot_state or {},
    })
    ```

2. **Upload the bot using the web interface.**
    - Go to the app, enter a bot name, and upload your `.py` file.

3. **Select your bot for a game and start playing.**

## Example Bot

See `backend/example_bot.py` for a simple bot implementation.

## Extending the Game Logic

- The current logic is minimal and does not implement all Durak rules.
- To support full Durak, expand `advance_game_step` in `game_logic.py` to handle:
  - Multiple attacks per round
  - Card drawing from the deck
  - End-of-game detection
  - More complex attack/defend logic

---
