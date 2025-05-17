// filepath: src/App.jsx
import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";

// Durak constants
const suits = ["♠", "♥", "♦", "♣"];
const ranks = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"];
const rankValue = (rank) => ranks.indexOf(rank);

function createDeck() {
    const deck = [];
    for (let suit of suits) {
        for (let rank of ranks) {
            deck.push({ suit, rank });
        }
    }
    return deck;
}
function shuffle(deck) {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
}

function dealPlayers(deck, numPlayers) {
    const hands = Array.from({ length: numPlayers }, () => []);
    for (let i = 0; i < 6 * numPlayers && deck.length; i++) {
        hands[i % numPlayers].push(deck.pop());
    }
    return hands;
}

function findFirstTrump(hands, trumpSuit) {
    let minTrump = null, minIdx = -1;
    hands.forEach((hand, idx) => {
        const trumps = hand.filter(c => c.suit === trumpSuit);
        if (trumps.length) {
            const lowest = trumps.reduce((a, b) => rankValue(a.rank) < rankValue(b.rank) ? a : b);
            if (!minTrump || rankValue(lowest.rank) < rankValue(minTrump.rank)) {
                minTrump = lowest;
                minIdx = idx;
            }
        }
    });
    return minIdx;
}

function Card({ card }) {
    return (
        <span style={{
            border: "1px solid #333",
            borderRadius: 4,
            padding: "2px 6px",
            margin: 2,
            background: "#fff",
            fontSize: 18,
            display: "inline-block"
        }}>
            {card.rank}{card.suit}
        </span>
    );
}

function PlayerHand({ hand, isUser, trumpSuit }) {
    return (
        <div>
            {isUser
                ? hand.map((c, i) => (
                    <Card key={i} card={c} />
                ))
                : <span>{hand.length} cards</span>
            }
        </div>
    );
}

// Bot logic: attack with lowest card, defend with lowest valid card, add cards if possible
function botAttack(hand, table, trumpSuit) {
    // If table is empty, play lowest card
    if (table.length === 0) {
        let min = hand.reduce((a, b) => rankValue(a.rank) < rankValue(b.rank) ? a : b);
        return min;
    }
    // Otherwise, play lowest card matching any rank on table
    const tableRanks = table.map(c => c.rank);
    const candidates = hand.filter(c => tableRanks.includes(c.rank));
    if (candidates.length) {
        return candidates.reduce((a, b) => rankValue(a.rank) < rankValue(b.rank) ? a : b);
    }
    return null;
}
function botDefend(hand, attackCard, trumpSuit) {
    // Try to beat attackCard
    const sameSuit = hand.filter(c => c.suit === attackCard.suit && rankValue(c.rank) > rankValue(attackCard.rank));
    if (sameSuit.length) {
        return sameSuit.reduce((a, b) => rankValue(a.rank) < rankValue(b.rank) ? a : b);
    }
    // Try to use trump if attackCard is not trump
    if (attackCard.suit !== trumpSuit) {
        const trumps = hand.filter(c => c.suit === trumpSuit);
        if (trumps.length) {
            return trumps.reduce((a, b) => rankValue(a.rank) < rankValue(b.rank) ? a : b);
        }
    }
    return null;
}

// Built-in bot logic
const builtinBots = [
    {
        name: "SimpleBot",
        attack: (hand, table, trumpSuit) => botAttack(hand, table, trumpSuit),
        defend: (hand, attackCard, trumpSuit) => botDefend(hand, attackCard, trumpSuit),
    }
];

// Load custom bots from localStorage
function loadCustomBots() {
    try {
        const arr = JSON.parse(localStorage.getItem("customBots") || "[]");
        return arr.map(b => ({
            name: b.name,
            attack: new Function("hand", "table", "trumpSuit", b.attack),
            defend: new Function("hand", "attackCard", "trumpSuit", b.defend),
        }));
    } catch {
        return [];
    }
}

// Save custom bot to localStorage
function saveCustomBot(name, attackCode, defendCode) {
    const arr = JSON.parse(localStorage.getItem("customBots") || "[]");
    arr.push({ name, attack: attackCode, defend: defendCode });
    localStorage.setItem("customBots", JSON.stringify(arr));
}

// Bot upload and selection UI
function BotManager({ bots, setBots, selectedBots, setSelectedBots, numPlayers, setNumPlayers }) {
    const [botName, setBotName] = useState("");
    const [attackCode, setAttackCode] = useState("// hand, table, trumpSuit\nreturn hand[0];");
    const [defendCode, setDefendCode] = useState("// hand, attackCard, trumpSuit\nreturn hand[0];");
    const [error, setError] = useState("");

    const handleAddBot = () => {
        try {
            // Test code
            // eslint-disable-next-line no-new-func
            new Function("hand", "table", "trumpSuit", attackCode);
            new Function("hand", "attackCard", "trumpSuit", defendCode);
            saveCustomBot(botName, attackCode, defendCode);
            setBots([...builtinBots, ...loadCustomBots()]);
            setBotName("");
            setAttackCode("// hand, table, trumpSuit\nreturn hand[0];");
            setDefendCode("// hand, attackCard, trumpSuit\nreturn hand[0];");
            setError("");
        } catch (e) {
            setError("Invalid code: " + e.message);
        }
    };

    return (
        <div style={{ margin: 24, padding: 24, background: "#f8fafc", borderRadius: 12, boxShadow: "0 2px 8px #e0e7ff" }}>
            <h2>Upload Your Bot</h2>
            <div>
                <input
                    placeholder="Bot Name"
                    value={botName}
                    onChange={e => setBotName(e.target.value)}
                    style={{ marginRight: 8, padding: 4, fontSize: 16 }}
                />
            </div>
            <div>
                <b>Attack Function:</b>
                <textarea
                    rows={3}
                    value={attackCode}
                    onChange={e => setAttackCode(e.target.value)}
                    style={{ width: 350, fontFamily: "monospace", fontSize: 14 }}
                />
            </div>
            <div>
                <b>Defend Function:</b>
                <textarea
                    rows={3}
                    value={defendCode}
                    onChange={e => setDefendCode(e.target.value)}
                    style={{ width: 350, fontFamily: "monospace", fontSize: 14 }}
                />
            </div>
            <button onClick={handleAddBot} style={{ marginTop: 8, padding: "6px 18px", fontSize: 16 }}>
                Save Bot
            </button>
            {error && <div style={{ color: "red" }}>{error}</div>}
            <hr style={{ margin: "24px 0" }} />
            <h2>Game Setup</h2>
            <div>
                <label>
                    Number of Players:&nbsp;
                    <input
                        type="number"
                        min={2}
                        max={bots.length}
                        value={numPlayers}
                        onChange={e => setNumPlayers(Number(e.target.value))}
                        style={{ width: 40, fontSize: 16 }}
                    />
                </label>
            </div>
            <div>
                <b>Select Bots for Game:</b>
                <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                    {bots.map((bot, idx) => (
                        <label key={bot.name} style={{ marginRight: 12 }}>
                            <input
                                type="checkbox"
                                checked={selectedBots.includes(idx)}
                                onChange={() => {
                                    if (selectedBots.includes(idx)) {
                                        setSelectedBots(selectedBots.filter(i => i !== idx));
                                    } else if (selectedBots.length < numPlayers) {
                                        setSelectedBots([...selectedBots, idx]);
                                    }
                                }}
                                disabled={
                                    !selectedBots.includes(idx) && selectedBots.length >= numPlayers
                                }
                            />
                            {bot.name}
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );
}

// Game with per-bot logs and hands
function GameWithBots({ bots, selectedBots, auto, setAuto, onBack }) {
    const numPlayers = selectedBots.length;
    const [gameState, setGameState] = useState(() => {
        let deck = shuffle(createDeck());
        let trumpCard = deck[deck.length - 1];
        let trumpSuit = trumpCard.suit;
        let hands = dealPlayers(deck, numPlayers);
        let attacker = findFirstTrump(hands, trumpSuit);
        if (attacker === -1) attacker = 0;
        return {
            hands,
            deck,
            trumpSuit,
            trumpCard,
            table: [],
            attacker,
            defender: (attacker + 1) % numPlayers,
            turnStage: "attack",
            log: [`Trump suit: ${trumpSuit}, Trump card: ${trumpCard.rank}${trumpCard.suit}`],
            winner: null,
            round: 1,
            perBotLogs: Array(numPlayers).fill().map(() => []),
        };
    });

    const { hands, deck, trumpSuit, trumpCard, table, attacker, defender, turnStage, log, winner, perBotLogs } = gameState;

    // Auto mode effect
    useEffect(() => {
        if (!auto || winner !== null) return;
        const timer = setTimeout(() => {
            nextTurn();
        }, 1000);
        return () => clearTimeout(timer);
    }, [gameState, auto, winner]);

    function addLog(idx, msg) {
        setGameState(state => {
            const newPerBotLogs = state.perBotLogs.map((l, i) =>
                i === idx ? [msg, ...l] : l
            );
            return { ...state, perBotLogs: newPerBotLogs };
        });
    }

    function nextTurn() {
        setGameState(state => {
            if (state.winner !== null) return state;
            let {
                hands, deck, trumpSuit, trumpCard, table,
                attacker, defender, turnStage, log, winner, round, perBotLogs
            } = state;

            // If only one player left, game over
            const activePlayers = hands.map((h, i) => h.length > 0 ? i : null).filter(i => i !== null);
            if (activePlayers.length === 1) {
                perBotLogs = perBotLogs.map((l, i) =>
                    [`Game Over! Winner: ${bots[selectedBots[activePlayers[0]]].name}`, ...l]
                );
                return {
                    ...state,
                    winner: activePlayers[0],
                    log: [...log, `Game Over! Winner: ${bots[selectedBots[activePlayers[0]]].name}`],
                    perBotLogs
                };
            }

            // If attacker's hand is empty, skip to next
            if (hands[attacker].length === 0) {
                attacker = (attacker + 1) % numPlayers;
                defender = (attacker + 1) % numPlayers;
                perBotLogs = perBotLogs.map((l, i) =>
                    i === attacker ? [`${bots[selectedBots[attacker]].name} is new attacker.`, ...l] : l
                );
                return { ...state, attacker, defender, log: [...log, `${bots[selectedBots[attacker]].name} is new attacker.`], perBotLogs };
            }

            // Attack phase
            if (turnStage === "attack") {
                let attackCard;
                const bot = bots[selectedBots[attacker]];
                attackCard = bot.attack(hands[attacker], table, trumpSuit);
                if (!attackCard) {
                    // Can't attack, pass
                    perBotLogs = perBotLogs.map((l, i) =>
                        i === attacker ? [`${bot.name} passes attack.`, ...l] : l
                    );
                    return {
                        ...state,
                        attacker: (attacker + 1) % numPlayers,
                        defender: (attacker + 2) % numPlayers,
                        turnStage: "attack",
                        table: [],
                        log: [...log, `${bot.name} passes attack.`],
                        perBotLogs
                    };
                }
                // Remove card from attacker's hand
                let newHands = hands.map((h, i) =>
                    i === attacker ? h.filter(c => c !== attackCard) : h
                );
                let newTable = [...table, { ...attackCard, by: attacker }];
                perBotLogs = perBotLogs.map((l, i) =>
                    i === attacker ? [`${bot.name} attacks with ${attackCard.rank}${attackCard.suit}`, ...l] : l
                );
                return {
                    ...state,
                    hands: newHands,
                    table: newTable,
                    turnStage: "defend",
                    log: [...log, `${bot.name} attacks with ${attackCard.rank}${attackCard.suit}`],
                    perBotLogs
                };
            }

            // Defend phase
            if (turnStage === "defend") {
                const attackCard = table[table.length - 1];
                const bot = bots[selectedBots[defender]];
                let defendCard = bot.defend(hands[defender], attackCard, trumpSuit);
                if (!defendCard) {
                    // Defender picks up all cards on table
                    let newHands = hands.map((h, i) =>
                        i === defender ? [...h, ...table.map(c => ({ rank: c.rank, suit: c.suit }))] : h
                    );
                    // Draw up to 6 cards for all
                    let newDeck = [...deck];
                    let refill = newHands.map(h => h.slice());
                    for (let p = 0; p < numPlayers; ++p) {
                        while (refill[p].length < 6 && newDeck.length) {
                            refill[p].push(newDeck.pop());
                        }
                    }
                    // Next attacker is next after defender
                    let nextAttacker = defender;
                    let nextDefender = (nextAttacker + 1) % numPlayers;
                    perBotLogs = perBotLogs.map((l, i) =>
                        i === defender ? [`${bot.name} picks up cards.`, ...l] : l
                    );
                    return {
                        ...state,
                        hands: refill,
                        deck: newDeck,
                        table: [],
                        attacker: nextAttacker,
                        defender: nextDefender,
                        turnStage: "attack",
                        log: [...log, `${bot.name} picks up cards.`],
                        round: round + 1,
                        perBotLogs
                    };
                }
                // Remove defendCard from defender's hand
                let newHands = hands.map((h, i) =>
                    i === defender ? h.filter(c => c !== defendCard) : h
                );
                let newTable = [...table, { ...defendCard, by: defender, defend: true }];
                perBotLogs = perBotLogs.map((l, i) =>
                    i === defender ? [`${bot.name} defends with ${defendCard.rank}${defendCard.suit}`, ...l] : l
                );
                return {
                    ...state,
                    hands: newHands,
                    table: newTable,
                    turnStage: "add",
                    log: [...log, `${bot.name} defends with ${defendCard.rank}${defendCard.suit}`],
                    perBotLogs
                };
            }

            // Add phase (other players can add cards of matching rank)
            if (turnStage === "add") {
                let tableRanks = table.map(c => c.rank);
                let canAdd = false;
                let addCard, addBy;
                for (let p = 0; p < numPlayers; ++p) {
                    if (p === defender || hands[p].length === 0) continue;
                    let candidates = hands[p].filter(c => tableRanks.includes(c.rank));
                    if (candidates.length && table.length / 2 < hands[defender].length) {
                        addCard = candidates[0];
                        addBy = p;
                        canAdd = true;
                        break;
                    }
                }
                if (!canAdd) {
                    // End of round, discard table, refill hands
                    let newHands = hands.map(h => h.slice());
                    let newDeck = [...deck];
                    for (let p = 0; p < numPlayers; ++p) {
                        while (newHands[p].length < 6 && newDeck.length) {
                            newHands[p].push(newDeck.pop());
                        }
                    }
                    let stillIn = newHands.map((h, i) => h.length > 0 ? i : null).filter(i => i !== null);
                    if (stillIn.length === 1) {
                        perBotLogs = perBotLogs.map((l, i) =>
                            [`Game Over! Winner: ${bots[selectedBots[stillIn[0]]].name}`, ...l]
                        );
                        return {
                            ...state,
                            hands: newHands,
                            deck: newDeck,
                            table: [],
                            winner: stillIn[0],
                            log: [...log, `Game Over! Winner: ${bots[selectedBots[stillIn[0]]].name}`],
                            perBotLogs
                        };
                    }
                    let nextAttacker = (attacker + 1) % numPlayers;
                    while (newHands[nextAttacker].length === 0) nextAttacker = (nextAttacker + 1) % numPlayers;
                    let nextDefender = (nextAttacker + 1) % numPlayers;
                    while (newHands[nextDefender].length === 0) nextDefender = (nextDefender + 1) % numPlayers;
                    perBotLogs = perBotLogs.map((l, i) =>
                        i === nextAttacker ? [`End of round. Next attacker: ${bots[selectedBots[nextAttacker]].name}`, ...l] : l
                    );
                    return {
                        ...state,
                        hands: newHands,
                        deck: newDeck,
                        table: [],
                        attacker: nextAttacker,
                        defender: nextDefender,
                        turnStage: "attack",
                        log: [...log, `End of round. Next attacker: ${bots[selectedBots[nextAttacker]].name}`],
                        round: round + 1,
                        perBotLogs
                    };
                }
                // Add card to table
                let newHands = hands.map((h, i) =>
                    i === addBy ? h.filter(c => c !== addCard) : h
                );
                let newTable = [...table, { ...addCard, by: addBy }];
                perBotLogs = perBotLogs.map((l, i) =>
                    i === addBy ? [`${bots[selectedBots[addBy]].name} adds ${addCard.rank}${addCard.suit}`, ...l] : l
                );
                return {
                    ...state,
                    hands: newHands,
                    table: newTable,
                    turnStage: "defend",
                    log: [...log, `${bots[selectedBots[addBy]].name} adds ${addCard.rank}${addCard.suit}`],
                    perBotLogs
                };
            }

            return state;
        });
    }

    return (
        <div style={{ fontFamily: "sans-serif", maxWidth: 1200, margin: "auto" }}>
            <h2>Durak (Custom Bots)</h2>
            <div style={{ marginBottom: 12 }}>
                <label>
                    <input
                        type="radio"
                        checked={!auto}
                        onChange={() => setAuto(false)}
                        style={{ marginRight: 4 }}
                    />
                    Step by Step
                </label>
                <label style={{ marginLeft: 16 }}>
                    <input
                        type="radio"
                        checked={auto}
                        onChange={() => setAuto(true)}
                        style={{ marginRight: 4 }}
                    />
                    Auto (every second)
                </label>
            </div>
            <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
                {hands.map((hand, i) => (
                    <div
                        key={i}
                        style={{
                            border: i === defender ? "2.5px solid #f59e42" : "1px solid #e5e7eb",
                            borderRadius: 12,
                            padding: 16,
                            background: i === defender ? "#fff7ed" : "#f9fafb",
                            minWidth: 180,
                            boxShadow: i === defender
                                ? "0 4px 16px #fbbf24aa"
                                : "0 2px 8px #e0e7ff44",
                            position: "relative"
                        }}
                    >
                        <b style={{ color: "#6366f1" }}>{bots[selectedBots[i]].name}</b>
                        {i === defender && (
                            <span
                                style={{
                                    position: "absolute",
                                    top: 10,
                                    right: 14,
                                    background: "#f59e42",
                                    color: "#fff",
                                    borderRadius: 6,
                                    padding: "2px 10px",
                                    fontSize: 13,
                                    fontWeight: 700,
                                    letterSpacing: 0.5,
                                    boxShadow: "0 1px 4px #fbbf2444"
                                }}
                            >
                                Defender
                            </span>
                        )}
                        <div style={{ margin: "8px 0" }}>
                            {hand.map((c, idx) => (
                                <span key={idx} style={{
                                    border: "1px solid #6366f1",
                                    borderRadius: 6,
                                    padding: "4px 10px",
                                    margin: 2,
                                    background: "#fff",
                                    fontSize: 18,
                                    display: "inline-block"
                                }}>{c.rank}{c.suit}</span>
                            ))}
                        </div>
                        <div style={{
                            background: "#eef2ff",
                            borderRadius: 8,
                            padding: 8,
                            fontSize: 13,
                            minHeight: 80,
                            maxHeight: 120,
                            overflowY: "auto"
                        }}>
                            <b>Log:</b>
                            <ul style={{ paddingLeft: 18 }}>
                                {perBotLogs[i].map((line, idx) => <li key={idx}>{line}</li>)}
                            </ul>
                        </div>
                    </div>
                ))}
                <div style={{
                    minWidth: 260,
                    background: "#f1f5f9",
                    borderRadius: 12,
                    boxShadow: "0 2px 12px #a5b4fc44",
                    padding: 16,
                    maxHeight: 340,
                }}>
                    <h3 style={{ color: "#6366f1" }}>Table</h3>
                    <div>
                        {table.map((c, i) => (
                            <span key={i} style={{ marginRight: 8 }}>
                                <span style={{
                                    border: "1px solid #6366f1",
                                    borderRadius: 6,
                                    padding: "4px 10px",
                                    background: "#fff",
                                    fontSize: 18,
                                    display: "inline-block"
                                }}>{c.rank}{c.suit}</span>
                                {c.defend ? " (defend)" : ""}
                            </span>
                        ))}
                    </div>
                    <div style={{ marginTop: 12 }}>
                        <b>Trump:</b> {trumpSuit} <b>Trump card:</b> {trumpCard.rank}{trumpCard.suit}
                        <br /><b>Deck:</b> {deck.length} cards
                    </div>
                    <div style={{
                        background: "#e0e7ff",
                        borderRadius: 8,
                        padding: 8,
                        fontSize: 13,
                        marginTop: 12,
                        maxHeight: 120,
                        overflowY: "auto"
                    }}>
                        <b>Game Log:</b>
                        <ul style={{ paddingLeft: 18 }}>
                            {log.map((line, i) => <li key={i}>{line}</li>)}
                        </ul>
                    </div>
                    <div style={{ marginTop: 12 }}>
                        {winner === null ? (
                            !auto && <button onClick={nextTurn}>Next Step</button>
                        ) : (
                            <div>
                                <b>Winner: {bots[selectedBots[winner]].name}</b>
                                <div style={{ marginTop: 16 }}>
                                    <button
                                        onClick={onBack}
                                        style={{
                                            padding: "8px 20px",
                                            fontSize: 16,
                                            borderRadius: 8,
                                            marginTop: 8,
                                            background: "#6366f1",
                                            color: "#fff",
                                            border: "none",
                                            cursor: "pointer"
                                        }}
                                    >
                                        Start New Game
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function App() {
    const [bots, setBots] = useState([...builtinBots, ...loadCustomBots()]);
    const [selectedBots, setSelectedBots] = useState([0, 0]);
    const [numPlayers, setNumPlayers] = useState(2);
    const [auto, setAuto] = useState(false);
    const [gameStarted, setGameStarted] = useState(false);

    useEffect(() => {
        // Reset selection if bots or numPlayers changes
        setSelectedBots(Array(numPlayers).fill(0).map((_, i) => bots[i] ? i : 0));
    }, [bots, numPlayers]);

    if (!gameStarted) {
        return (
            <div>
                <BotManager
                    bots={bots}
                    setBots={setBots}
                    selectedBots={selectedBots}
                    setSelectedBots={setSelectedBots}
                    numPlayers={numPlayers}
                    setNumPlayers={setNumPlayers}
                />
                <button
                    style={{ margin: 24, padding: "10px 32px", fontSize: 20, borderRadius: 8 }}
                    disabled={selectedBots.length !== numPlayers}
                    onClick={() => setGameStarted(true)}
                >
                    Start Game
                </button>
            </div>
        );
    }
    return (
        <GameWithBots
            bots={bots}
            selectedBots={selectedBots}
            auto={auto}
            setAuto={setAuto}
            onBack={() => setGameStarted(false)}
        />
    );
}

function ErrorBoundary({ children }) {
    const [error, setError] = React.useState(null);
    if (error) {
        return <div style={{ color: "red" }}><b>Error:</b> {error.message}</div>;
    }
    return (
        <React.Suspense fallback="Loading...">
            <React.Fragment>
                {React.Children.map(children, child =>
                    React.cloneElement(child, { onError: setError })
                )}
            </React.Fragment>
        </React.Suspense>
    );
}

const root = createRoot(document.getElementById("root"));
root.render(
    <ErrorBoundary>
        <App />
    </ErrorBoundary>
);