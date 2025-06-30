# To restore: main.py for FastAPI backend of Durak game
# This file serves as the main backend entry point for the Durak card game.
# It handles bot uploads, game creation, and game state management.
# It uses FastAPI to create RESTful endpoints for interacting with the game.
# It also manages CORS settings to allow cross-origin requests, which is useful for frontend applications.

import os
import uuid
import importlib.util, importlib.machinery
import sys
import io
import traceback

# Add this before importing durak_game
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status as fastapi_status
from typing import List
from pydantic import BaseModel
import random
from configurations import (
    SUITS,
    RANKS,
    CARDS_PER_HAND,
    USE_FIXED_DECK,
)
from durak_game import pretty_print_state, card_str_to_tuple, advance_game_step

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
    for i in range(CARDS_PER_HAND):
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
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    if filepath.endswith(".py"):
        spec = importlib.util.spec_from_file_location(module_name, filepath)
    elif filepath.endswith(".pyc"):
        loader = importlib.machinery.SourcelessFileLoader(module_name, filepath)
        spec = importlib.util.spec_from_loader(module_name, loader)
    else:
        raise ImportError(f"Unsupported file type for bot file: {filepath}")
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for bot file: {filepath}")
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        # Try to get 'bot' instance, else fallback to module
        bot_instance = getattr(module, "bot", module)
        return bot_instance
    except Exception as e:
        print(f"[ERROR] Failed to load bot from {filepath}: {e}")
        traceback.print_exc()
        return None


@app.get("/api/bots", response_model=List[BotInfo])
def list_bots():
    bots = []
    for fname in os.listdir(BOTS_DIR):
        # Exclude __pycache__ and any non-.py or non-.pyc files
        if fname == "__pycache__" or not (
            fname.endswith(".py") or fname.endswith(".pyc")
        ):
            continue
        # Try to read the display name from a .name file if it exists
        name_file = os.path.splitext(fname)[0] + ".name"
        name = None
        if os.path.exists(os.path.join(BOTS_DIR, name_file)):
            with open(os.path.join(BOTS_DIR, name_file), "r", encoding="utf-8") as f:
                name = f.read().strip()
        if not name:
            name = fname.split("_", 1)[-1].replace(".pyc", "").replace(".py", "")
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


@app.delete("/api/bots/{filename}")
def delete_bot(filename: str):
    filepath = os.path.join(BOTS_DIR, filename)
    name_file = os.path.splitext(filepath)[0] + ".name"
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(name_file):
            os.remove(name_file)
        return {"success": True}
    except Exception as e:
        return JSONResponse(
            {"error": str(e)}, status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def create_game_state(num_bots):
    deck = shuffle(create_deck())
    if USE_FIXED_DECK:
        with open("deck.txt","r") as f:
            deck_str = f.read()
        deck = [tuple([int(x) for x in s.split(",")]) for s in deck_str.split()]
        deck = [{"rank": RANKS[c[0]], "suit": SUITS[c[1]]} for c in deck]

    with open("deck.txt", "w") as file:
        for c in deck:
            r, s = card_str_to_tuple(f"{c['rank']}{c['suit']}")
            file.write(f"{r},{s} ")
    trump_card_obj = deck[-1]
    trump_card = f"{trump_card_obj['rank']}{trump_card_obj['suit']}"
    trump_suit = trump_card_obj["suit"]
    hands = deal_players(deck, num_bots)
    # Find attacker: player with the lowest trump card (lowest rank of trump suit)
    lowest_trump = 20
    attacker = random.randint(0, num_bots - 1)
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
    if lowest_trump > len(trump_rank_order):
        lowest_trump = -1
    defender = (attacker + 1) % num_bots
    return {
        "trump_suit": trump_suit,
        "trump_card": trump_card,  # always a string like '7♠'
        "lowest_trump": lowest_trump,  # if there is no trump, it is marked as -1.
        "hands": [[f"{c['rank']}{c['suit']}" for c in h] for h in hands],
        "table_attack": [],
        "table_defence": [],
        "attacker": attacker,
        "defender": defender,
        "curr_player": attacker,
        "log": [[] for _ in range(num_bots)],  # log is now a list of lists, one per bot
        "bot_states": [{} for _ in range(num_bots)],
        "burn": False,
        "num_of_burned_cards": 0,
        "deck": [f"{c['rank']}{c['suit']}" for c in deck],
        "deck_count": len(deck),  # Add deck count to state
    }


@app.post("/api/games", response_model=GameState)
async def create_game(request: Request):
    bot_filenames = await request.json()
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
            bot_name = fname.split("_", 1)[-1].replace(".pyc", "").replace(".py", "")
        bot_names.append(bot_name)
    state = create_game_state(len(bot_filenames))
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


max_steps_achieved = 0


def main(to_print: bool = False, randomize_order: bool = False):
    global max_steps_achieved

    import argparse
    import time

    MAX_NUM_OF_STEPS = 700  # Limit to prevent infinite loops

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
            bot_name = fname.split("_", 1)[-1].replace(".pyc", "").replace(".py", "")
        bot_names.append(bot_name)

    bot_names = [f"Player {i}: {bot_names[i]}" for i in range(len(bot_names))]

    state = create_game_state(len(bot_filenames))

    if to_print:
        print("=== Durak CLI Game ===")
        print(f"Trump card: {state['trump_card']}")
        print(f"Trump suit: {state['trump_suit']}")
        print(f"Bots: {bot_names}")
        print("Starting game...\n")

    step = 0
    while True:
        if to_print:
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
        # A player is only out if their hand is empty AND the deck is empty
        alive = [
            i
            for i, h in enumerate(state["hands"])
            if len(h) > 0 or len(state["deck"]) > 0
        ]
        if len(alive) <= 1 or step >= MAX_NUM_OF_STEPS:
            if to_print:
                print("\n=== GAME OVER ===")
            # Print all winners
            if step == MAX_NUM_OF_STEPS:
                if to_print:
                    print("Game ended due to reaching max steps.\nNo one loses.")
                return -1  # Indicate game ended without a loser
            else:
                max_steps_achieved = max(max_steps_achieved, step)
                for idx, h in enumerate(state["hands"]):
                    if len(h) == 0:
                        if to_print:
                            print(f"WINNER: {bot_names[idx]}")
                # Print the loser (the only one with cards left)
                if len(alive) == 1:
                    if to_print:
                        print(f"\nLOSER: {bot_names[alive[0]]}")
                    return alive[0]  # Return the index of the loser
        # Advance game step
        state = advance_game_step(state, bots, bot_names)
        step += 1


def tournament(num_of_games=10, to_print=False):
    loser_count_lst = [0 for _ in range(len(sys.argv) - 1)]
    count_proper_games = 0
    max_total_games = 2 * num_of_games
    game_idx = 0
    bot_filenames_orig = sys.argv[1:]  # Save original order
    while count_proper_games < num_of_games and game_idx < max_total_games:
        if to_print:
            print(f"Game {game_idx + 1} of {num_of_games}:")

        # Randomize player order for this game
        bot_filenames = bot_filenames_orig[:]
        random.shuffle(bot_filenames)
        sys.argv = ["main.py"] + bot_filenames
        loser = main(to_print=False)
        # `sys.stdout = sys.__stdout__
        if loser != -1:
            if to_print:
                print(f"Game {game_idx + 1} ended with loser: {loser}")
            # Map loser index back to original bot order
            orig_idx = bot_filenames_orig.index(bot_filenames[loser])
            loser_count_lst[orig_idx] += 1
            count_proper_games += 1
        elif to_print:
            print(f"Game {game_idx + 1} ended without a loser (max steps reached).")
        game_idx += 1
    print("\n=== Tournament Results ===")
    for i, count in enumerate(loser_count_lst):
        print(f"Player {i} lost {count} times.")
    num_of_infinite_games = game_idx - count_proper_games
    print(f"\n{num_of_infinite_games} games got caught in an infinite loop.")

    return loser_count_lst, num_of_infinite_games


@app.post("/api/tournament")
async def run_tournament(request: Request):
    data = await request.json()
    bot_filenames = data.get("bots", [])
    num_games = int(data.get("numGames", 10))
    if len(bot_filenames) < 2:
        return JSONResponse({"error": "At least 2 bots required"}, status_code=400)
    # Prepare sys.argv for tournament
    sys_argv_backup = sys.argv
    sys.argv = ["main.py"] + bot_filenames
    # Redirect stdout to capture tournament output
    # old_stdout = sys.stdout
    # stdout_capture = io.StringIO()
    # sys.stdout = stdout_capture
    try:
        loser_count_lst, num_of_infinite_games = tournament(
            num_of_games=num_games, to_print=True
        )
        # output = stdout_capture.getvalue()
    except Exception as e:
        # sys.stdout = old_stdout
        # sys.argv = sys_argv_backup
        return JSONResponse({"error": str(e)}, status_code=500)
    # sys.stdout = old_stdout
    sys.argv = sys_argv_backup
    # Count infinite games from output
    # infinite_games = 0
    # total_games = num_games
    # for line in output.splitlines():
    #     if "infinite loop" in line:
    #         try:
    #             infinite_games = int(line.split()[0])
    #         except Exception:
    #             pass
    return {
        "loser_count_lst": loser_count_lst,
        "total_games": sum(loser_count_lst) + num_of_infinite_games,
        "infinite_games": num_of_infinite_games,
        # "output": output,
    }


if __name__ == "__main__":
    import time

    start_time = time.time()
    tournament(num_of_games=100)  # Run tournament with 100 games
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")
    print(f"Max steps achieved in any game: {max_steps_achieved}")
