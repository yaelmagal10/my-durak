import os
import uuid
import importlib.util
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import random
from game_logic import advance_game_step  # Import the helper

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

BOTS_DIR = "bots"
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
    suits = ["♠", "♥", "♦", "♣"]
    ranks = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    return [{"suit": s, "rank": r} for s in suits for r in ranks]


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
    spec = importlib.util.spec_from_file_location("bot", filepath)
    bot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bot)
    return bot


@app.post("/api/bots")
async def upload_bot(file: UploadFile, name: str = Form(...)):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(BOTS_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return {"name": name, "filename": filename}


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
    trump_card = deck[-1]
    trump_suit = trump_card["suit"]
    hands = deal_players(deck, len(bot_filenames))
    bots = []
    bot_names = []
    for fname in bot_filenames:
        bot_path = os.path.join(BOTS_DIR, fname)
        bots.append(load_bot(bot_path))
        # Use the uploaded name (strip uuid and .py)
        bot_names.append(fname.split("_", 1)[-1].replace(".py", ""))
    attacker = 0
    defender = 1
    table = []
    # First attack
    attack_card = bots[attacker].attack(
        [dict(card) for card in hands[attacker]], [], trump_suit
    )
    table.append(attack_card)
    # Remove attack card from attacker's hand
    for idx, c in enumerate(hands[attacker]):
        if c["rank"] == attack_card["rank"] and c["suit"] == attack_card["suit"]:
            hands[attacker].pop(idx)
            break
    state = {
        "trump_suit": trump_suit,
        "trump_card": trump_card,
        "hands": [[f"{c['rank']}{c['suit']}" for c in h] for h in hands],
        "table": [f"{attack_card['rank']}{attack_card['suit']}"],
        "attacker": attacker,
        "defender": defender,
        "log": [
            f"Trump: {trump_card['rank']}{trump_card['suit']}",
            f"Player {attacker+1} ({bot_names[attacker]}) attacks with {attack_card['rank']}{attack_card['suit']}",
        ],
    }
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
