# A very detailed explanation about this file:
# This FastAPI application serves as the backend for a Durak card game.
# It allows users to upload bot scripts, create game instances, and advance game steps.
# The application handles CORS, manages game state, and provides endpoints for bot management and game actions.
# it uses the `durak_game` module to handle game logic, including deck creation, shuffling, dealing cards, and advancing game steps.
# The bots are expected to be Python scripts that implement a bot interface for playing the game.
# The application also includes error handling for game not found scenarios and provides a structured response for game states.
# The application is structured to allow easy addition of new bots and game instances, making it flexible for testing different strategies.
# This file is part of the my-durak project, which is a web-based implementation of the Durak card game.
# my-durak/backend/main.py
# some more detailed explanation:
# This file is the main entry point for the FastAPI application that serves the backend for the Durak card game.
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
from durak_game import advance_game_step, SUITS, RANKS  # Import the helper
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
    return [{"suit": s, "rank": r} for s in SUITS for r in RANKS]


def shuffle(deck):
    d = deck[:]
    random.shuffle(d)
    return d


def deal_players(deck, num_players):
    hands = [[] for _ in range(num_players)]
    for i in range(6 * num_players):
        hands[i % num_players].append(deck.pop())
    return hands


def load_bot(filepath):
    # Ensure backend dir is in sys.path for bot imports
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    spec = importlib.util.spec_from_file_location("bot", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Try to get 'bot' instance, else fallback to module
    bot_instance = getattr(module, "bot", module)
    return bot_instance


def pretty_print_state(state):
    print("Game State:")
    print(f"Trump Suit: {state['trump_suit']}")
    print(f"Trump Card: {state['trump_card']}")
    print("Hands:")
    for i, hand in enumerate(state["hands"]):
        print(f"  Player {i}: {', '.join(hand)}")
    print(f"Attacker: Player {state['attacker']}")
    print(f"Defender: Player {state['defender']}")
    print(f"Table Attack: {state['table_attack']}")
    print(f"Table Defence: {state['table_defence']}")
    print(f"Burn: {state['burn']}")
    print("Deck:")
    for i, card in enumerate(state["deck"]):
        print(f"{card}", end="  " if i % 10 != 9 else "\n")
    print(f"Deck Count: {state['deck_count']}")


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


@app.get("/api/bots", response_model=List[BotInfo])
def list_bots():
    bots = []
    for fname in os.listdir(BOTS_DIR):
        bots.append(
            BotInfo(name=fname.split("_", 1)[-1].replace(".py", ""), filename=fname)
        )
    return bots


@app.get("/api/bots/{filename}")
def get_bot_file(filename: str):
    return FileResponse(os.path.join(BOTS_DIR, filename))


@app.post("/api/games", response_model=GameState)
async def create_game(request: Request):
    bot_filenames = await request.json()
    deck = shuffle(create_deck())
    print("Currently using a fixed deck (DECK1) for testing")
    # deck = DECK1
    trump_card = deck[-1]
    trump_suit = trump_card["suit"]
    hands = deal_players(deck, len(bot_filenames))
    bots = []
    bot_names = []
    for fname in bot_filenames:
        bot_path = os.path.join(BOTS_DIR, fname)
        bot_instance = load_bot(bot_path)
        bots.append(bot_instance)
        # Use bot.name if available, else fallback to filename
        bot_name = getattr(
            bot_instance, "name", fname.split("_", 1)[-1].replace(".py", "")
        )
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
        "trump_card": trump_card,
        "hands": [[f"{c['rank']}{c['suit']}" for c in h] for h in hands],
        "table_attack": [],
        "table_defence": [],
        "attacker": attacker,
        "defender": defender,
        "log": [[] for _ in bots],  # log is now a list of lists, one per bot
        "bot_states": [{} for _ in bots],
        "burn": False,
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
