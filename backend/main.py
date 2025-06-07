# To restore: main.py for FastAPI backend of Durak game
# This file serves as the main backend entry point for the Durak card game.
# It handles bot uploads, game creation, and game state management.
# It uses FastAPI to create RESTful endpoints for interacting with the game.
# It also manages CORS settings to allow cross-origin requests, which is useful for frontend applications.

import os
import uuid
import importlib.util
import sys

# Add this before importing durak_game
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import random
from durak_game import advance_game_step, SUITS, RANKS, pretty_print_state
from const_decks import DECK1

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set BOTS_DIR to the absolute path of the backend/bots directory
BOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bots")
GAMES = {}

os.makedirs(BOTS_DIR, exist_ok=True)


class BotInfo(BaseModel):
    name: str
    filename: str


class GameState(BaseModel):
    id: str
    bots: List[str]
    state: dict


def create_deck():
    deck = [{"rank": r, "suit": s} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def shuffle(deck):
    random.shuffle(deck)
    return deck


def deal_players(deck, num_players):
    hands = [[] for _ in range(num_players)]
    for i in range(6):
        for j in range(num_players):
            if deck:
                hands[j].append(deck.pop(0))
    return hands


def load_bot(filepath):
    # Ensure backend dir is in sys.path for bot imports
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Bot file not found: {filepath}")
    spec = importlib.util.spec_from_file_location("bot", filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for bot file: {filepath}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Try to get 'bot' instance, else fallback to module
    bot_instance = getattr(module, "bot", module)
    return bot_instance


@app.get("/api/bots", response_model=List[BotInfo])
def list_bots():
    bots = []
    for fname in os.listdir(BOTS_DIR):
        # Exclude __pycache__ and any non-.py files
        if fname == "__pycache__" or not fname.endswith(".py"):
            continue
        # Try to read the display name from a .name file if it exists
        name_file = os.path.splitext(fname)[0] + ".name"
        name = None
        if os.path.exists(os.path.join(BOTS_DIR, name_file)):
            with open(os.path.join(BOTS_DIR, name_file), "r", encoding="utf-8") as f:
                name = f.read().strip()
        if not name:
            name = fname.split("_", 1)[-1].replace(".py", "")
        bots.append(BotInfo(name=name, filename=fname))
    return bots


@app.post("/api/bots")
async def upload_bot(file: UploadFile, name: str = Form(...)):
    try:
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(BOTS_DIR, filename)
        print(f"[UPLOAD] Saving bot to: {filepath}")
        file_content = await file.read()
        print(
            f"[UPLOAD] Received file: {file.filename}, size: {len(file_content)} bytes"
        )
        with open(filepath, "wb") as f:
            f.write(file_content)
        # Save the display name in a .name file
        name_file = os.path.splitext(filepath)[0] + ".name"
        with open(name_file, "w", encoding="utf-8") as f:
            f.write(name)
        # Confirm file was written
        if not os.path.exists(filepath):
            print(f"[UPLOAD ERROR] File not found after write: {filepath}")
            return JSONResponse({"error": "File not saved."}, status_code=500)
        print(f"[UPLOAD] File saved successfully: {filepath}")
        return {"name": name, "filename": filename}
    except Exception as e:
        import traceback

        print("[UPLOAD ERROR] Exception occurred during upload:")
        traceback.print_exc()
        print(f"[UPLOAD ERROR] Exception details: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/bots/{filename}")
def get_bot_file(filename: str):
    return FileResponse(os.path.join(BOTS_DIR, filename))


@app.post("/api/games", response_model=GameState)
async def create_game(request: Request):
    bot_filenames = await request.json()
    deck = shuffle(create_deck())
    print("Currently using a fixed deck (DECK1) for testing")
    # deck = DECK1
    trump_card_obj = deck[-1]
    trump_card = f"{trump_card_obj['rank']}{trump_card_obj['suit']}"
    trump_suit = trump_card_obj["suit"]
    hands = deal_players(deck, len(bot_filenames))
    bots = []
    bot_names = []
    for fname in bot_filenames:
        bot_path = os.path.join(BOTS_DIR, fname)
        bot_instance = load_bot(bot_path)
        bots.append(bot_instance)
        # Use bot.name if available, else fallback to .name file, else fallback to filename
        bot_name = getattr(bot_instance, "name", None)
        if not bot_name:
            name_file = os.path.splitext(bot_path)[0] + ".name"
            if os.path.exists(name_file):
                with open(name_file, "r", encoding="utf-8") as f:
                    bot_name = f.read().strip()
        if not bot_name:
            bot_name = fname.split("_", 1)[-1].replace(".py", "")
        bot_names.append(bot_name)
    # Find attacker: player with the lowest trump card (lowest rank of trump suit)
    lowest_trump = 20
    attacker = 0
    trump_rank_order = RANKS
    for i, hand in enumerate(hands):
        trump_cards = [
            trump_rank_order.index(c["rank"]) for c in hand if c["suit"] == trump_suit
        ]
        if trump_cards:
            min_trump = min(trump_cards)
            if min_trump < lowest_trump:
                lowest_trump = min_trump
                attacker = i
    defender = (attacker + 1) % len(bots)
    state = {
        "trump_suit": trump_suit,
        "trump_card": trump_card,  # always a string like '7♠'
        "hands": [[f"{c['rank']}{c['suit']}" for c in h] for h in hands],
        "table_attack": [],
        "table_defence": [],
        "attacker": attacker,
        "defender": defender,
        "curr_player": attacker,
        "log": [[] for _ in bots],  # log is now a list of lists, one per bot
        "bot_states": [{} for _ in bots],
        "burn": False,
        "num_of_burned_cards": 0,
        "deck": [f"{c['rank']}{c['suit']}" for c in deck],
        "deck_count": len(deck),  # Add deck count to state
    }
    # Pretty print the initial state for debugging
    pretty_print_state(state)
    game_id = uuid.uuid4().hex
    GAMES[game_id] = {"bots": bot_filenames, "bot_names": bot_names, "state": state}
    return GameState(id=game_id, bots=bot_names, state=state)


@app.get("/api/games/{game_id}", response_model=GameState)
def get_game(game_id: str):
    game = GAMES.get(game_id)
    if not game:
        return {"error": "Game not found"}
    return GameState(id=game_id, bots=game["bots"], state=game["state"])


@app.post("/api/games/{game_id}/step", response_model=GameState)
async def step_game(game_id: str):
    game = GAMES.get(game_id)
    if not game:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    bots = [load_bot(os.path.join(BOTS_DIR, fname)) for fname in game["bots"]]
    state = game["state"]
    # Pass bot_names for display
    new_state = advance_game_step(state, bots, game.get("bot_names", []))
    game["state"] = new_state
    return GameState(id=game_id, bots=game.get("bot_names", []), state=new_state)


if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Run Durak game in CLI mode (no UI).")
    parser.add_argument(
        "bots", nargs="+", help="List of bot .py files (from backend/bots/)"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between steps (seconds)"
    )
    args = parser.parse_args()

    # Prepare bot filenames and paths
    bot_filenames = args.bots
    bot_paths = [os.path.join(BOTS_DIR, fname) for fname in bot_filenames]
    bots = [load_bot(path) for path in bot_paths]
    bot_names = []
    for bot_instance, fname in zip(bots, bot_filenames):
        bot_name = getattr(bot_instance, "name", None)
        if not bot_name:
            name_file = os.path.splitext(os.path.join(BOTS_DIR, fname))[0] + ".name"
            if os.path.exists(name_file):
                with open(name_file, "r", encoding="utf-8") as f:
                    bot_name = f.read().strip()
        if not bot_name:
            bot_name = fname.split("_", 1)[-1].replace(".py", "")
        bot_names.append(bot_name)

    # Create deck and initial state (reuse logic from create_game)
    deck = shuffle(create_deck())
    trump_card_obj = deck[-1]
    trump_card = f"{trump_card_obj['rank']}{trump_card_obj['suit']}"
    trump_suit = trump_card_obj["suit"]
    hands = deal_players(deck, len(bot_filenames))
    # Build initial state
    state = {
        "trump_suit": trump_suit,
        "trump_card": trump_card,
        "hands": [[f"{c['rank']}{c['suit']}" for c in h] for h in hands],
        "table_attack": [],
        "table_defence": [],
        "attacker": 0,
        "defender": 1,
        "curr_player": 0,
        "log": [[] for _ in bots],
        "bot_states": [{} for _ in bots],
        "burn": False,
        "num_of_burned_cards": 0,
        "deck": [f"{c['rank']}{c['suit']}" for c in deck],
        "deck_count": len(deck),
    }
    # Find attacker: player with the lowest trump card
    lowest_trump = 20
    trump_rank_order = RANKS
    for i, hand in enumerate(hands):
        trump_cards = [
            trump_rank_order.index(c["rank"]) for c in hand if c["suit"] == trump_suit
        ]
        if trump_cards:
            min_trump = min(trump_cards)
            if min_trump < lowest_trump:
                lowest_trump = min_trump
                state["attacker"] = i
    state["defender"] = (state["attacker"] + 1) % len(bots)
    state["curr_player"] = state["attacker"]

    print("=== Durak CLI Game ===")
    print(f"Trump card: {state['trump_card']}")
    print(f"Trump suit: {state['trump_suit']}")
    print(f"Bots: {bot_names}")
    print("Starting game...\n")

    step = 0
    while True:
        print(f"\n--- Step {step} ---")
        print(
            f"Attacker: {bot_names[state['attacker']]} | Defender: {bot_names[state['defender']]}"
        )
        print(f"Hands: {[len(h) for h in state['hands']]}")
        print(f"Deck count: {state['deck_count']}")
        print(f"Table attack: {state['table_attack']}")
        print(f"Table defence: {state['table_defence']}")
        # Print last log entries for each bot
        for idx, bot_log in enumerate(state["log"]):
            if bot_log:
                print(f"Log [{bot_names[idx]}]: {bot_log[-1]}")
        # Check for game end
        alive = [i for i, h in enumerate(state["hands"]) if len(h) > 0]
        if len(alive) <= 1:
            print("\n=== GAME OVER ===")
            for idx, h in enumerate(state["hands"]):
                if len(h) == 0:
                    print(f"WINNER: {bot_names[idx]}")
            break
        # Advance game step
        state = advance_game_step(state, bots, bot_names)
        step += 1
        time.sleep(args.delay)
