import React, { useState } from "react";

const API_URL = "http://127.0.0.1:8000/api";

function TournamentUI({ bots, onBack }) {
    const [selectedBots, setSelectedBots] = useState([]);
    const [numGames, setNumGames] = useState(10);
    const [results, setResults] = useState(null);
    const [running, setRunning] = useState(false);
    const [error, setError] = useState("");

    const handleBotToggle = idx => {
        setSelectedBots(selectedBots.includes(idx)
            ? selectedBots.filter(i => i !== idx)
            : [...selectedBots, idx]
        );
    };

    const runTournament = async () => {
        setError("");
        setResults(null);
        if (selectedBots.length < 2) {
            setError("Select at least 2 bots.");
            console.log("[TournamentUI] Not enough bots selected");
            return;
        }
        setRunning(true);
        try {
            console.log("[TournamentUI] Sending request to backend", selectedBots.map(i => bots[i]));
            const res = await fetch(`${API_URL}/tournament`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    bots: selectedBots.map(i => bots[i]?.filename),
                    numGames
                })
            });
            console.log("[TournamentUI] Response status:", res.status);
            if (!res.ok) {
                let err = {};
                try {
                    err = await res.json();
                } catch (e) {
                    console.log("[TournamentUI] Error parsing error JSON", e);
                }
                console.log("[TournamentUI] Backend error:", err);
                throw new Error(err.error || "Tournament failed");
            }
            let data = {};
            try {
                data = await res.json();
            } catch (e) {
                console.log("[TournamentUI] Error parsing result JSON", e);
                throw new Error("Could not parse tournament results");
            }
            console.log("[TournamentUI] Tournament results:", data);
            setResults(data);
        } catch (e) {
            setError(e.message);
            console.log("[TournamentUI] Exception:", e);
        }
        setRunning(false);
    };

    return (
        <div style={{ margin: 24, padding: 24, background: "#f8fafc", borderRadius: 12, boxShadow: "0 2px 8px #e0e7ff" }}>
            <button onClick={onBack} style={{ marginBottom: 18, padding: "8px 20px", fontSize: 16, borderRadius: 8 }}>
                Back
            </button>
            <h2>Run Tournament</h2>
            <div style={{ marginBottom: 12 }}>
                <b>Select Bots:</b>
                <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
                    {bots.map((bot, idx) => (
                        <label key={bot.filename} style={{ marginRight: 12 }}>
                            <input
                                type="checkbox"
                                checked={selectedBots.includes(idx)}
                                onChange={() => handleBotToggle(idx)}
                            />
                            {bot.name}
                        </label>
                    ))}
                </div>
            </div>
            <div style={{ marginBottom: 12 }}>
                <b>Number of Games:</b>
                <input
                    type="number"
                    min={1}
                    max={1000}
                    value={numGames}
                    onChange={e => setNumGames(Number(e.target.value))}
                    style={{ width: 60, fontSize: 16, marginLeft: 8 }}
                />
            </div>
            <button
                onClick={runTournament}
                disabled={running || selectedBots.length < 2}
                style={{ padding: "8px 24px", fontSize: 18, borderRadius: 8, background: "#6366f1", color: "#fff", border: "none", cursor: "pointer" }}
            >
                {running ? "Running..." : "Start Tournament"}
            </button>
            {error && <div style={{ color: "red", marginTop: 12 }}>{error}</div>}
            {results && (
                <div style={{ marginTop: 24 }}>
                    <h3>Results</h3>
                    <ul>
                        {results.loser_count_lst && results.loser_count_lst.map((count, i) => (
                            <li key={i}>{bots[selectedBots[i]] ? bots[selectedBots[i]].name : `Bot ${i}`}:    {count} losses</li>
                        ))}
                    </ul>
                    <div>Total games: {results.total_games}</div>
                    <div>Games with no loser (max steps reached): {results.infinite_games}</div>
                </div>
            )}
        </div>
    );
}

export default TournamentUI;
