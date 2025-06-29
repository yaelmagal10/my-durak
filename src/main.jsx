//after change
// filepath: src/App.jsx
import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import CardGameUI from "./CardGameUI";
import TournamentUI from "./TournamentUI";

console.log("[main.jsx] App loaded");

const API_URL = "http://127.0.0.1:8000/api";

function BotManagerPage({ onStartGame, bots, setBots, selectedBots, setSelectedBots, numPlayers, setNumPlayers, botCounts, setBotCounts, setShowTournament }) {
    const [botFile, setBotFile] = useState(null);
    const [botName, setBotName] = useState("");
    const [error, setError] = useState("");
    // Only use playerOrder for bot selection/order
    const [playerOrder, setPlayerOrder] = useState([]);

    // Fetch bots from backend
    useEffect(() => {
        console.log("[BotManagerPage] Fetching bots from backend...");
        fetch(`${API_URL}/bots`)
            .then(res => res.json())
            .then(data => {
                setBots(data);
                console.log("[BotManagerPage] Bots fetched:", data);
            })
            .catch((err) => {
                setBots([]);
                console.log("[BotManagerPage] Failed to fetch bots", err);
            });
    }, [setBots]);

    // Upload bot to backend
    const handleUpload = async () => {
        console.log("[BotManagerPage] Uploading bot", botName, botFile);
        if (!botFile || !botName) {
            setError("Please select a file and enter a bot name.");
            return;
        }
        setError("");
        const formData = new FormData();
        formData.append("file", botFile);
        formData.append("name", botName);
        try {
            await fetch(`${API_URL}/bots`, { method: "POST", body: formData });
            // Refresh bot list
            const botsResp = await fetch(`${API_URL}/bots`);
            setBots(await botsResp.json());
            setBotFile(null);
            setBotName("");
            console.log("[BotManagerPage] Bot uploaded successfully");
        } catch (e) {
            setError("Failed to upload bot. Please ensure the file is a valid Python script.");
            console.log("[BotManagerPage] Bot upload failed", e);
        }
    };

    // Update bot counts when bots or numPlayers changes
    useEffect(() => {
        if (bots.length === 0) return;
        setBotCounts((prev) => {
            const newCounts = {};
            bots.forEach(bot => {
                newCounts[bot.filename] = prev && prev[bot.filename] ? prev[bot.filename] : 0;
            });
            return newCounts;
        });
        console.log("[BotManagerPage] Bot counts updated", bots);
    }, [bots, numPlayers, setBotCounts]);

    // Calculate total selected players
    const totalSelected = Object.values(botCounts).reduce((a, b) => a + b, 0);

    // Prepare selectedBots array for game
    useEffect(() => {
        const arr = [];
        bots.forEach(bot => {
            for (let i = 0; i < (botCounts[bot.filename] || 0); ++i) {
                arr.push(bot.filename);
            }
        });
        setSelectedBots(arr);
        // If playerOrder contains bots that are no longer selected, clear them
        setPlayerOrder(prev =>
            prev.map(fn => arr.includes(fn) ? fn : "")
        );
        console.log("[BotManagerPage] Selected bots array updated", arr);
    }, [botCounts, bots, setSelectedBots]);

    // When numPlayers or bots change, reset playerOrder if needed
    useEffect(() => {
        if (playerOrder.length !== numPlayers) {
            setPlayerOrder(Array(numPlayers).fill(""));
        }
    }, [numPlayers, bots]);

    // When playerOrder changes, update selectedBots to match
    useEffect(() => {
        setSelectedBots(playerOrder);
    }, [playerOrder, setSelectedBots]);

    // Handler for selecting a bot for a player slot
    const handlePlayerOrderChange = (idx, value) => {
        setPlayerOrder(prev => {
            const next = [...prev];
            next[idx] = value;
            return next;
        });
    };

    // Allow starting if all slots are filled (allowing duplicates)
    const canStart = () => {
        if (playerOrder.length !== numPlayers) return false;
        if (playerOrder.some(fn => !fn)) return false;
        return true;
    };

    // When starting game, use the chosen order
    const handleStartGame = () => {
        setSelectedBots(playerOrder);
        onStartGame();
    };

    // Remove bot handler
    const handleRemoveBot = async (filename) => {
        if (!window.confirm("Are you sure you want to delete this bot?")) return;
        try {
            await fetch(`${API_URL}/bots/${filename}`, { method: "DELETE" });
            // Refresh bot list
            const botsResp = await fetch(`${API_URL}/bots`);
            setBots(await botsResp.json());
            // Remove from playerOrder if present
            setPlayerOrder(prev => prev.map(fn => fn === filename ? "" : fn));
        } catch (e) {
            alert("Failed to delete bot.");
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'flex-start',
            fontFamily: "'Segoe UI', 'Roboto', 'Arial', sans-serif",
            padding: 0,
        }}>
            <div style={{
                marginTop: 48,
                background: 'rgba(255,255,255,0.97)',
                borderRadius: 18,
                boxShadow: '0 4px 32px #6366f133',
                padding: '36px 40px 32px 40px',
                minWidth: 380,
                maxWidth: 480,
                width: '100%',
                border: '1.5px solid #e0e7ff',
            }}>
                <h2 style={{ fontSize: 32, fontWeight: 800, color: '#6366f1', marginBottom: 18, letterSpacing: 1 }}>Upload Python Bot</h2>
                <div style={{ display: 'flex', gap: 10, marginBottom: 18 }}>
                    <input
                        type="text"
                        placeholder="Bot Name"
                        value={botName}
                        onChange={e => setBotName(e.target.value)}
                        style={{
                            flex: 1,
                            padding: '10px 14px',
                            fontSize: 17,
                            borderRadius: 8,
                            border: '1.5px solid #c7d2fe',
                            outline: 'none',
                            background: '#f1f5f9',
                            marginRight: 0,
                        }}
                    />
                    <input
                        type="file"
                        accept=".py, .pyc"
                        onChange={e => setBotFile(e.target.files[0])}
                        style={{
                            flex: 1,
                            fontSize: 15,
                            borderRadius: 8,
                            border: '1.5px solid #c7d2fe',
                            background: '#f1f5f9',
                            padding: '8px 0',
                        }}
                    />
                    <button
                        onClick={handleUpload}
                        style={{
                            padding: '10px 18px',
                            fontSize: 16,
                            borderRadius: 8,
                            background: '#6366f1',
                            color: '#fff',
                            border: 'none',
                            fontWeight: 700,
                            cursor: 'pointer',
                            boxShadow: '0 2px 8px #6366f122',
                            transition: 'background 0.2s',
                        }}
                    >
                        Upload Bot
                    </button>
                </div>
                {error && <div style={{ color: "#e11d48", fontWeight: 600, marginBottom: 10 }}>{error}</div>}
                <hr style={{ margin: "24px 0", border: 'none', borderTop: '1.5px solid #e0e7ff' }} />
                <h3 style={{ fontSize: 22, fontWeight: 700, color: '#3b3b5c', marginBottom: 18 }}>Game Setup</h3>
                <div style={{ marginBottom: 18, display: 'flex', alignItems: 'center', gap: 10 }}>
                    <label style={{ fontWeight: 500, fontSize: 17, color: '#222' }}>
                        Number of Players:&nbsp;
                        <input
                            type="number"
                            min={2}
                            max={bots.length * 4}
                            value={numPlayers}
                            onChange={e => setNumPlayers(Number(e.target.value))}
                            style={{
                                width: 60,
                                fontSize: 17,
                                borderRadius: 7,
                                border: '1.5px solid #c7d2fe',
                                background: '#f1f5f9',
                                padding: '6px 8px',
                                marginLeft: 4,
                            }}
                        />
                    </label>
                </div>
                {/* Player order selection */}
                <div style={{ marginBottom: 18 }}>
                    <b style={{ fontSize: 16, color: '#222' }}>Choose Bot for Each Player (Order Matters):</b>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {playerOrder.map((filename, idx) => (
                            <li key={idx} style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ color: '#888', marginRight: 10 }}>#{idx}</span>
                                <select
                                    value={filename}
                                    onChange={e => handlePlayerOrderChange(idx, e.target.value)}
                                    style={{
                                        minWidth: 120,
                                        fontSize: 16,
                                        borderRadius: 7,
                                        border: '1.5px solid #c7d2fe',
                                        background: '#f1f5f9',
                                        padding: '6px 8px',
                                        marginRight: 10,
                                    }}
                                >
                                    <option value="">-- Select Bot --</option>
                                    {bots.map(bot => (
                                        <option key={bot.filename} value={bot.filename}>
                                            {bot.name}
                                        </option>
                                    ))}
                                </select>
                                {filename && (
                                    <span style={{ color: '#6366f1', fontWeight: 500 }}>
                                        {bots.find(b => b.filename === filename)?.name || filename}
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
                <div style={{ marginBottom: 18 }}>
                    <b style={{ fontSize: 16, color: '#222' }}>Available Bots:</b>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {bots.map((bot, idx) => (
                            <li key={bot.filename} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                                <span style={{ marginRight: 10, fontWeight: 500, color: '#6366f1', minWidth: 90 }}>{bot.name}</span>
                                <button
                                    onClick={() => handleRemoveBot(bot.filename)}
                                    style={{
                                        marginLeft: 8,
                                        padding: '4px 10px',
                                        fontSize: 13,
                                        borderRadius: 6,
                                        background: '#ef4444',
                                        color: '#fff',
                                        border: 'none',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                    }}
                                >
                                    Remove
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 32, gap: 18 }}>
                    <button
                        style={{
                            flex: 1,
                            margin: 0,
                            padding: '14px 0',
                            fontSize: 20,
                            borderRadius: 10,
                            background: '#6366f1',
                            color: '#fff',
                            border: 'none',
                            fontWeight: 700,
                            cursor: canStart() ? 'pointer' : 'not-allowed',
                            opacity: canStart() ? 1 : 0.5,
                            boxShadow: '0 2px 8px #6366f122',
                            transition: 'background 0.2s',
                        }}
                        disabled={!canStart()}
                        onClick={handleStartGame}
                    >
                        Start Game
                    </button>
                    <button
                        style={{
                            flex: 1,
                            margin: 0,
                            padding: '14px 0',
                            fontSize: 20,
                            borderRadius: 10,
                            background: '#7c3aed',
                            color: '#fff',
                            border: 'none',
                            fontWeight: 700,
                            cursor: 'pointer',
                            marginLeft: 18,
                            boxShadow: '0 2px 8px #7c3aed22',
                            transition: 'background 0.2s',
                        }}
                        onClick={() => setShowTournament(true)}
                    >
                        Run Tournament
                    </button>
                </div>
            </div>
        </div>
    );
}

function GamePage({ onBack, selectedBots }) {
    const [gameState, setGameState] = useState(null);
    const [playMode, setPlayMode] = useState("step"); // "step" or "auto"
    const [gameStarted, setGameStarted] = useState(false);
    const [autoSpeed, setAutoSpeed] = useState(200); // ms delay for autoplay

    // Start game when user clicks "Start"
    const startGame = () => {
        setGameState(null);
        setGameStarted(true);
    };

    useEffect(() => {
        if (!gameStarted || !selectedBots || selectedBots.length < 2) return;
        console.log("[GamePage] Creating new game with bots:", selectedBots);
        fetch(`${API_URL}/games`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(selectedBots)
        })
            .then(res => res.json())
            .then(data => {
                setGameState(data);
                console.log("[GamePage] Game created, state:", data);
            });
    }, [selectedBots, gameStarted]);

    // When switching to auto, finish the game from current state
    useEffect(() => {
        if (!gameState?.id || playMode !== "auto" || !gameStarted) return;
        let cancelled = false;
        async function autoStep() {
            let state = gameState;
            while (
                state &&
                state.state &&
                state.state.hands.filter(h => h.length > 0).length > 1
            ) {
                const resp = await fetch(`${API_URL}/games/${state.id}/step`, { method: "POST" });
                const data = await resp.json();
                if (cancelled) return;
                setGameState(data);
                state = data;
                console.log("[GamePage] Auto step, new state:", data);
                await new Promise(res => setTimeout(res, autoSpeed));
            }
        }
        autoStep();
        return () => { cancelled = true; };
    }, [playMode, gameState?.id, gameStarted, autoSpeed]);

    const handleNextStep = async () => {
        if (!gameState?.id) return;
        const resp = await fetch(`${API_URL}/games/${gameState.id}/step`, { method: "POST" });
        const data = await resp.json();
        setGameState(data);
        console.log("[GamePage] Step button pressed, new state:", data);
    };

    // Helper: get winner and loser indices
    function getWinnersAndLoser(gameState) {
        if (!gameState?.state?.hands) return { winners: [], loser: null };
        const hands = gameState.state.hands;
        const bots = gameState.bots || [];
        const winners = [];
        let loser = null;
        hands.forEach((hand, idx) => {
            if (hand.length === 0) winners.push(idx);
        });
        if (hands.filter(h => h.length > 0).length === 1) {
            loser = hands.findIndex(h => h.length > 0);
        }
        return { winners, loser };
    }

    // Show play mode selection before starting the game
    if (!gameStarted) {
        return (
            <div style={{ margin: 8, maxWidth: 600 }}>
                <h2 style={{ fontSize: 22, marginBottom: 12 }}>Choose Play Mode</h2>
                <div style={{ marginBottom: 18 }}>
                    <label>
                        <input
                            type="radio"
                            name="playmode"
                            value="step"
                            checked={playMode === "step"}
                            onChange={() => setPlayMode("step")}
                            style={{ marginRight: 4 }}
                        />
                        Step by Step
                    </label>
                    <label style={{ marginLeft: 18 }}>
                        <input
                            type="radio"
                            name="playmode"
                            value="auto"
                            checked={playMode === "auto"}
                            onChange={() => setPlayMode("auto")}
                            style={{ marginRight: 4 }}
                        />
                        Auto Play
                    </label>
                </div>
                {playMode === "auto" && (
                    <div style={{ marginBottom: 18 }}>
                        <label>
                            Autoplay Speed (ms):&nbsp;
                            <input
                                type="number"
                                min={0}
                                max={2000}
                                step={50}
                                value={autoSpeed}
                                onChange={e => setAutoSpeed(Number(e.target.value))}
                                style={{ width: 70, fontSize: 16 }}
                            />
                        </label>
                    </div>
                )}
                <button
                    style={{ padding: "10px 32px", fontSize: 20, borderRadius: 8, marginRight: 12 }}
                    onClick={startGame}
                >
                    Start Game
                </button>
                <button
                    style={{ padding: "8px 20px", fontSize: 16, borderRadius: 8 }}
                    onClick={onBack}
                >
                    Back to Bot Manager
                </button>
            </div>
        );
    }

    // Check for loser state
    const { winners, loser } = getWinnersAndLoser(gameState);

    if (gameState && gameState.state && loser !== null) {
        // Only one player left with cards: show LOSER screen
        const bots = gameState.bots || [];
        return (
            <div style={{
                margin: 0,
                minHeight: "100vh",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                background: "linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)"
            }}>
                <div style={{
                    fontSize: 48,
                    fontWeight: 900,
                    color: "#dc2626",
                    marginBottom: 24,
                    letterSpacing: 2,
                    textShadow: "0 2px 12px #fca5a5"
                }}>
                    LOSER: Player {loser} {bots[loser] ? `(${bots[loser]})` : ""}
                </div>
                <div style={{
                    fontSize: 28,
                    fontWeight: 700,
                    color: "#22c55e",
                    marginBottom: 18,
                    letterSpacing: 1
                }}>
                    Winners:
                </div>
                <ul style={{ fontSize: 22, color: "#2563eb", fontWeight: 600, marginBottom: 32 }}>
                    {winners.map(idx => (
                        <li key={idx}>
                            Player {idx} {bots[idx] ? `(${bots[idx]})` : ""}
                        </li>
                    ))}
                </ul>
                <div style={{
                    width: "100%",
                    maxWidth: 700,
                    background: "#f1f5f9",
                    border: "1px solid #e5e7eb",
                    borderRadius: 10,
                    padding: 18,
                    marginBottom: 32,
                    boxShadow: "0 2px 12px #a5b4fc22"
                }}>
                    <div style={{ fontWeight: 700, fontSize: 20, color: "#6366f1", marginBottom: 10 }}>Game Log:</div>
                    <div style={{
                        maxHeight: 300,
                        overflowY: "auto",
                        fontSize: 15,
                        color: "#475569"
                    }}>
                        {/* Show all logs for all bots */}
                        {gameState.state.log && Array.isArray(gameState.state.log) && gameState.state.log.length > 0
                            ? gameState.state.log.map((botLog, idx) => (
                                <div key={idx} style={{ marginBottom: 10 }}>
                                    <div style={{ color: "#6366f1", fontWeight: 600, fontSize: 16, marginBottom: 2 }}>
                                        Player {idx} {bots && bots[idx] ? `(${bots[idx]})` : ""}
                                    </div>
                                    {botLog && botLog.length > 0
                                        ? botLog.map((entry, eidx) => (
                                            <div key={eidx} style={{ marginBottom: 2 }}>
                                                {entry.replace(/^\[TS:\d+(\.\d+)?\]/, "")}
                                            </div>
                                        ))
                                        : <div style={{ color: "#a1a1aa" }}>No log yet</div>
                                    }
                                </div>
                            ))
                            : <div style={{ color: "#a1a1aa" }}>No log yet</div>
                        }
                    </div>
                </div>
                <button
                    style={{
                        padding: "12px 40px",
                        fontSize: 22,
                        borderRadius: 10,
                        background: "#6366f1",
                        color: "#fff",
                        fontWeight: 700,
                        border: "none",
                        boxShadow: "0 2px 8px #a5b4fc44"
                    }}
                    onClick={onBack}
                >
                    Back to Bot Manager
                </button>
            </div>
        );
    }

    return (
        <div style={{ margin: 8, maxWidth: 1100 }}>
            <h2 style={{ fontSize: 22, marginBottom: 12 }}>Durak Game (Python Backend)</h2>
            <div style={{ marginBottom: 10 }}>
                <label>
                    <input
                        type="radio"
                        name="playmode"
                        value="step"
                        checked={playMode === "step"}
                        onChange={() => setPlayMode("step")}
                        style={{ marginRight: 4 }}
                    />
                    Step by Step
                </label>
                <label style={{ marginLeft: 18 }}>
                    <input
                        type="radio"
                        name="playmode"
                        value="auto"
                        checked={playMode === "auto"}
                        onChange={() => setPlayMode("auto")}
                        style={{ marginRight: 4 }}
                    />
                    Auto Play
                </label>
                {playMode === "auto" && (
                    <span style={{ marginLeft: 18 }}>
                        <label>
                            Speed (ms):&nbsp;
                            <input
                                type="number"
                                min={0}
                                max={2000}
                                step={50}
                                value={autoSpeed}
                                onChange={e => setAutoSpeed(Number(e.target.value))}
                                style={{ width: 70, fontSize: 14 }}
                            />
                        </label>
                    </span>
                )}
            </div>
            {gameState && gameState.state ? (
                <>
                    <div style={{ marginBottom: 12 }}>
                        {playMode === "step" && (
                            <button
                                style={{ padding: "6px 18px", fontSize: 15, borderRadius: 6, marginRight: 10 }}
                                onClick={handleNextStep}
                            >
                                Next Step
                            </button>
                        )}
                        <button
                            style={{ padding: "5px 14px", fontSize: 13, borderRadius: 6 }}
                            onClick={onBack}
                        >
                            Back to Bot Manager
                        </button>
                    </div>
                    <CardGameUI
                        hands={gameState.state.hands}
                        table_attack={gameState.state.table_attack}
                        table_defence={gameState.state.table_defence}
                        log={gameState.state.log}
                        attacker={gameState.state.attacker}
                        defender={gameState.state.defender}
                        bots={gameState.bots}
                        compact
                        status={gameState.state.status}
                        deck_count={gameState.state.deck_count}
                        trump_card={gameState.state.trump_card}
                        num_of_burned_cards={gameState.state.num_of_burned_cards}
                        curr_player={gameState.state.curr_player}
                    />
                </>
            ) : (
                <div>Loading game...</div>
            )}
        </div>
    );
}

function App() {
    const [page, setPage] = useState("bots"); // "bots" or "game"
    const [bots, setBots] = useState([]);
    const [selectedBots, setSelectedBots] = useState([]);
    const [numPlayers, setNumPlayers] = useState(2);
    const [botCounts, setBotCounts] = useState({});
    const [showTournament, setShowTournament] = useState(false);

    useEffect(() => {
        console.log("[App] App mounted");
    }, []);

    if (showTournament) {
        return (
            <TournamentUI bots={bots} onBack={() => setShowTournament(false)} />
        );
    }

    return (
        page === "bots"
            ? <BotManagerPage
                onStartGame={() => setPage("game")}
                bots={bots}
                setBots={setBots}
                selectedBots={selectedBots}
                setSelectedBots={setSelectedBots}
                numPlayers={numPlayers}
                setNumPlayers={setNumPlayers}
                botCounts={botCounts}
                setBotCounts={setBotCounts}
                setShowTournament={setShowTournament}
            />
            : <GamePage
                onBack={() => setPage("bots")}
                selectedBots={selectedBots}
            />
    );
}

const root = createRoot(document.getElementById("root"));
root.render(
    <App />
);
