import React, { useState } from "react";

// Example card data: each player has an array of card strings
const initialHands = [
    ["2♠", "K♥", "7♦"],
    ["A♣", "10♠", "5♥"],
    ["J♦", "3♣", "Q♠"],
];

const botNames = ["Bot 1", "Bot 2", "Bot 3"];

export default function CardGameUI() {
    const [hands, setHands] = useState(initialHands);
    const [logs, setLogs] = useState([
        "Bot 1 played 2♠",
        "Bot 2 played A♣",
        "Bot 3 played J♦",
    ]);

    // Example: simulate a bot playing a card
    const playCard = (botIdx) => {
        if (hands[botIdx].length === 0) return;
        const card = hands[botIdx][0];
        const newHands = hands.map((hand, idx) =>
            idx === botIdx ? hand.slice(1) : hand
        );
        setHands(newHands);
        setLogs((prev) => [`${botNames[botIdx]} played ${card}`, ...prev]);
    };

    return (
        <div
            style={{
                minHeight: "100vh",
                padding: 32,
                fontFamily: "'Segoe UI', 'Roboto', 'Arial', sans-serif",
                background: "linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)",
            }}
        >
            <h2
                style={{
                    textAlign: "center",
                    fontWeight: 700,
                    fontSize: 36,
                    letterSpacing: 1,
                    color: "#3b3b5c",
                    marginBottom: 36,
                    textShadow: "0 2px 8px #b6b6e6",
                }}
            >
                Bot Card Game
            </h2>
            <div style={{ display: "flex", gap: 36, justifyContent: "center" }}>
                {hands.map((hand, idx) => (
                    <div
                        key={idx}
                        style={{
                            border: "none",
                            borderRadius: 18,
                            padding: 24,
                            background: "rgba(255,255,255,0.95)",
                            boxShadow: "0 4px 24px 0 #a5b4fc66",
                            minWidth: 180,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                        }}
                    >
                        <h3
                            style={{
                                fontWeight: 600,
                                fontSize: 22,
                                color: "#6366f1",
                                marginBottom: 16,
                                letterSpacing: 0.5,
                            }}
                        >
                            {botNames[idx]}
                        </h3>
                        <div style={{ display: "flex", gap: 12, marginBottom: 18 }}>
                            {hand.map((card, cidx) => (
                                <div
                                    key={cidx}
                                    style={{
                                        border: "none",
                                        borderRadius: 10,
                                        padding: "16px 18px",
                                        background: "linear-gradient(120deg, #f1f5f9 60%, #c7d2fe 100%)",
                                        fontSize: 24,
                                        boxShadow: "0 2px 8px #a5b4fc55",
                                        color: "#1e293b",
                                        fontWeight: 500,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        minWidth: 36,
                                        minHeight: 48,
                                        transition: "transform 0.1s",
                                    }}
                                >
                                    {card}
                                </div>
                            ))}
                        </div>
                        <button
                            onClick={() => playCard(idx)}
                            disabled={hand.length === 0}
                            style={{
                                marginTop: 10,
                                padding: "8px 18px",
                                fontSize: 16,
                                borderRadius: 8,
                                border: "none",
                                background: hand.length
                                    ? "linear-gradient(90deg, #6366f1 60%, #818cf8 100%)"
                                    : "#e5e7eb",
                                color: hand.length ? "#fff" : "#a1a1aa",
                                fontWeight: 600,
                                boxShadow: hand.length
                                    ? "0 2px 8px #818cf888"
                                    : "none",
                                cursor: hand.length ? "pointer" : "not-allowed",
                                transition: "background 0.2s, color 0.2s",
                            }}
                        >
                            Play Card
                        </button>
                    </div>
                ))}
                <div
                    style={{
                        minWidth: 260,
                        background: "rgba(236, 239, 255, 0.85)",
                        borderRadius: 18,
                        boxShadow: "0 2px 12px #a5b4fc44",
                        padding: 24,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        maxHeight: 340,
                    }}
                >
                    <h3
                        style={{
                            fontWeight: 600,
                            fontSize: 22,
                            color: "#6366f1",
                            marginBottom: 12,
                            letterSpacing: 0.5,
                        }}
                    >
                        Logs
                    </h3>
                    <div
                        style={{
                            background: "#f1f5f9",
                            border: "1px solid #e5e7eb",
                            borderRadius: 10,
                            height: 220,
                            overflowY: "auto",
                            padding: 12,
                            fontSize: 15,
                            width: "100%",
                            boxSizing: "border-box",
                            boxShadow: "0 1px 4px #a5b4fc22",
                        }}
                    >
                        {logs.map((log, idx) => (
                            <div
                                key={idx}
                                style={{
                                    marginBottom: 6,
                                    color: "#475569",
                                    fontWeight: idx === 0 ? 600 : 400,
                                }}
                            >
                                {log}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}