// filepath: src/App.jsx
import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import CardGameUI from "./CardGameUI";

const API_URL = "http://127.0.0.1:8000/api";

function BotManagerPage({ onStartGame, bots, setBots, selectedBots, setSelectedBots, numPlayers, setNumPlayers, botCounts, setBotCounts }) {
    const [botFile, setBotFile] = useState(null);
    const [botName, setBotName] = useState("");
    const [error, setError] = useState("");

    // Fetch bots from backend
    useEffect(() => {
        fetch(`${API_URL}/bots`)
            .then(res => res.json())
            .then(data => setBots(data))
            .catch(() => setBots([]));
    }, [setBots]);

    // Upload bot to backend
    const handleUpload = async () => {
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
        } catch (e) {
            setError("Upload failed");
        }
    };

    // Update bot counts when bots or numPlayers changes
    useEffect(() => {
        if (bots.length === 0) return;
        // Reset counts if bots or numPlayers changes
        setBotCounts((prev) => {
            const newCounts = {};
            bots.forEach(bot => {
                newCounts[bot.filename] = prev && prev[bot.filename] ? prev[bot.filename] : 0;
            });
            return newCounts;
        });
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
    }, [botCounts, bots, setSelectedBots]);

    return (
        <div style={{ margin: 32 }}>
            <h2>Upload Python Bot</h2>
            <input
                type="text"
                placeholder="Bot Name"
                value={botName}
                onChange={e => setBotName(e.target.value)}
                style={{ marginRight: 8 }}
            />
            <input
                type="file"
                accept=".py"
                onChange={e => setBotFile(e.target.files[0])}
                style={{ marginRight: 8 }}
            />
            <button onClick={handleUpload}>Upload Bot</button>
            {error && <div style={{ color: "red" }}>{error}</div>}
            <hr style={{ margin: "24px 0" }} />
            <h3>Game Setup</h3>
            <div style={{ marginBottom: 16 }}>
                <label>
                    Number of Players:&nbsp;
                    <input
                        type="number"
                        min={2}
                        max={bots.length * 4}
                        value={numPlayers}
                        onChange={e => setNumPlayers(Number(e.target.value))}
                        style={{ width: 60, fontSize: 16 }}
                    />
                </label>
            </div>
            <div>
                <b>Choose how many of each bot:</b>
                <ul>
                    {bots.map((bot, idx) => (
                        <li key={bot.filename}>
                            <span style={{ marginRight: 8 }}>{bot.name}</span>
                            <input
                                type="number"
                                min={0}
                                max={numPlayers}
                                value={botCounts[bot.filename] || 0}
                                onChange={e => {
                                    let val = Number(e.target.value);
                                    // Clamp so total does not exceed numPlayers
                                    const otherTotal = totalSelected - (botCounts[bot.filename] || 0);
                                    if (val < 0) val = 0;
                                    if (val > numPlayers - otherTotal) val = numPlayers - otherTotal;
                                    setBotCounts({ ...botCounts, [bot.filename]: val });
                                }}
                                style={{ width: 40, fontSize: 16 }}
                            />
                        </li>
                    ))}
                </ul>
            </div>
            <button
                style={{ marginTop: 24, padding: "10px 32px", fontSize: 20, borderRadius: 8 }}
                disabled={totalSelected !== numPlayers || numPlayers < 2}
                onClick={onStartGame}
            >
                Start Game
            </button>
        </div>
    );
}

function GamePage({ onBack, selectedBots }) {
    const [gameState, setGameState] = useState(null);

    // Start game on mount
    useEffect(() => {
        if (!selectedBots || selectedBots.length < 2) return;
        fetch(`${API_URL}/games`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(selectedBots)
        })
            .then(res => res.json())
            .then(data => setGameState(data));
    }, [selectedBots]);

    // Advance to next step
    const handleNextStep = async () => {
        if (!gameState?.id) return;
        const resp = await fetch(`${API_URL}/games/${gameState.id}/step`, { method: "POST" });
        const data = await resp.json();
        setGameState(data);
    };

    return (
        <div style={{ margin: 8, maxWidth: 1100 }}>
            <h2 style={{ fontSize: 22, marginBottom: 12 }}>Durak Game (Python Backend)</h2>
            {gameState && gameState.state ? (
                <>
                    <CardGameUI
                        hands={gameState.state.hands}
                        table={gameState.state.table}
                        log={gameState.state.log}
                        attacker={gameState.state.attacker}
                        defender={gameState.state.defender}
                        bots={gameState.bots}
                        compact
                    />
                    <div style={{ marginTop: 12 }}>
                        <button
                            style={{ padding: "6px 18px", fontSize: 15, borderRadius: 6, marginRight: 10 }}
                            onClick={handleNextStep}
                        >
                            Next Step
                        </button>
                        <button
                            style={{ padding: "5px 14px", fontSize: 13, borderRadius: 6 }}
                            onClick={onBack}
                        >
                            Back to Bot Manager
                        </button>
                    </div>
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