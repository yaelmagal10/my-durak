import React from "react";

// CardGameUI expects props: hands, table_attack, table_defence, log, attacker, defender, bots, compact, status
export default function CardGameUI({ hands, table_attack, table_defence, log, attacker, defender, bots, compact, status }) {
    const pad = compact ? 10 : 32;
    const cardPad = compact ? "6px 8px" : "16px 18px";
    const cardFont = compact ? 16 : 24;
    const minHandWidth = compact ? 90 : 180;
    const minHandHeight = compact ? 24 : 48;
    const h2Font = compact ? 20 : 36;
    const h3Font = compact ? 15 : 22;
    const boxPad = compact ? 10 : 24;
    const logHeight = compact ? 60 : 120;
    const tableFont = compact ? 15 : 22;
    const minTableWidth = compact ? 40 : 80;
    const maxHandBoxHeight = compact ? 170 : undefined;

    // Accept deck_count from props (passed via ...gameState.state)
    const deckCount = arguments[0].deck_count ?? 0;

    // Helper to display attack/defence pairs
    function renderTablePairs(table_attack, table_defence) {
        const pairs = [];
        const maxLen = Math.max(table_attack?.length || 0, table_defence?.length || 0);
        for (let i = 0; i < maxLen; ++i) {
            const attack = table_attack && table_attack[i] ? table_attack[i] : null;
            const defend = table_defence && table_defence[i] ? table_defence[i] : null;
            pairs.push(
                <div key={i} style={{ display: "flex", alignItems: "center", marginBottom: 2 }}>
                    <span style={{
                        minWidth: 32,
                        minHeight: 24,
                        padding: "2px 8px",
                        background: attack ? "#fbbf24" : "transparent",
                        borderRadius: 5,
                        marginRight: 6,
                        fontWeight: 600,
                        color: "#b45309"
                    }}>
                        {attack || ""}
                    </span>
                    <span style={{
                        minWidth: 32,
                        minHeight: 24,
                        padding: "2px 8px",
                        background: defend ? "#60a5fa" : "transparent",
                        borderRadius: 5,
                        fontWeight: 600,
                        color: "#1e40af"
                    }}>
                        {defend || ""}
                    </span>
                </div>
            );
        }
        return pairs;
    }

    // Flatten all bot logs into a single array for the game log (with bot/player info)
    function getGameLog(log, bots) {
        if (!Array.isArray(log)) return [];
        const entries = [];
        log.forEach((botLog, idx) => {
            if (Array.isArray(botLog)) {
                botLog.forEach((entry, eidx) => {
                    entries.push({
                        player: idx,
                        bot: bots && bots[idx] ? bots[idx] : `Player ${idx + 1}`,
                        text: entry,
                        order: eidx,
                    });
                });
            }
        });
        return entries;
    }

    const gameLogEntries = getGameLog(log, bots);

    return (
        <div
            style={{
                minHeight: compact ? "auto" : "100vh",
                padding: pad,
                fontFamily: "'Segoe UI', 'Roboto', 'Arial', sans-serif",
                background: compact
                    ? "linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)"
                    : "linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)",
            }}
        >
            <h2
                style={{
                    textAlign: "center",
                    fontWeight: 700,
                    fontSize: h2Font,
                    letterSpacing: 1,
                    color: "#3b3b5c",
                    marginBottom: compact ? 10 : 36,
                    textShadow: compact ? "none" : "0 2px 8px #b6b6e6",
                }}
            >
                Durak Game
            </h2>
            <div style={{ display: "flex", gap: compact ? 10 : 36, justifyContent: "center", alignItems: "flex-start" }}>
                {/* Main board area */}
                <div style={{ display: "flex", gap: compact ? 10 : 36 }}>
                    {hands.map((hand, idx) => (
                        <div
                            key={idx}
                            style={{
                                border: attacker === idx || defender === idx ? "2px solid #6366f1" : "none",
                                borderRadius: 12,
                                padding: boxPad,
                                background: "rgba(255,255,255,0.95)",
                                boxShadow: compact ? "0 2px 8px 0 #a5b4fc33" : "0 4px 24px 0 #a5b4fc66",
                                minWidth: minHandWidth,
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                maxHeight: maxHandBoxHeight,
                            }}
                        >
                            <h3
                                style={{
                                    fontWeight: 600,
                                    fontSize: h3Font,
                                    color: attacker === idx ? "#f59e42" : defender === idx ? "#3b82f6" : "#6366f1",
                                    marginBottom: compact ? 6 : 16,
                                    letterSpacing: 0.5,
                                }}
                            >
                                {`Player ${idx + 1} (${bots && bots[idx] ? bots[idx] : "?"})`}
                                {attacker === idx && " (Attacker)"}
                                {defender === idx && " (Defender)"}
                            </h3>
                            {/* Show status if available */}
                            {status && status[idx] && (
                                <div style={{
                                    color: "#0ea5e9",
                                    fontWeight: 500,
                                    fontSize: compact ? 11 : 15,
                                    marginBottom: compact ? 2 : 6,
                                }}>
                                    Status: {status[idx]}
                                </div>
                            )}
                            {/* HAND CARDS WRAPPED IN ROWS OF 4 */}
                            <div style={{ display: "flex", flexDirection: "column", gap: compact ? 2 : 8, marginBottom: compact ? 6 : 18 }}>
                                {Array.from({ length: Math.ceil(hand.length / 4) }).map((_, rowIdx) => (
                                    <div key={rowIdx} style={{ display: "flex", gap: compact ? 4 : 12, justifyContent: "center" }}>
                                        {hand.slice(rowIdx * 4, rowIdx * 4 + 4).map((card, cidx) => (
                                            <div
                                                key={cidx}
                                                style={{
                                                    border: "none",
                                                    borderRadius: 7,
                                                    padding: cardPad,
                                                    background: "linear-gradient(120deg, #f1f5f9 60%, #c7d2fe 100%)",
                                                    fontSize: cardFont,
                                                    boxShadow: compact ? "0 1px 3px #a5b4fc33" : "0 2px 8px #a5b4fc55",
                                                    color:
                                                        card && (card.includes("♥") || card.includes("♦"))
                                                            ? "#e11d48"
                                                            : "#1e293b",
                                                    fontWeight: 500,
                                                    display: "flex",
                                                    alignItems: "center",
                                                    justifyContent: "center",
                                                    minWidth: compact ? 18 : 36,
                                                    minHeight: minHandHeight,
                                                    transition: "transform 0.1s",
                                                }}
                                            >
                                                {card}
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                    <div
                        style={{
                            minWidth: compact ? 180 : 320,
                            background: "rgba(236, 239, 255, 0.85)",
                            borderRadius: 12,
                            boxShadow: compact ? "0 1px 4px #a5b4fc22" : "0 2px 12px #a5b4fc44",
                            padding: boxPad,
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            maxHeight: compact ? 200 : 340,
                        }}
                    >
                        <h3
                            style={{
                                fontWeight: 600,
                                fontSize: h3Font,
                                color: "#6366f1",
                                marginBottom: compact ? 4 : 12,
                                letterSpacing: 0.5,
                            }}
                        >
                            Table
                        </h3>
                        {/* Deck count display */}
                        <div style={{
                            color: "#16a34a",
                            fontWeight: 700,
                            fontSize: compact ? 15 : 22,
                            border: "2px solid #22c55e",
                            borderRadius: 6,
                            padding: "2px 10px",
                            background: "#f0fdf4",
                            marginBottom: compact ? 8 : 16,
                            minWidth: 80,
                            textAlign: "center"
                        }}>
                            Deck: {deckCount}
                        </div>
                        {/* Trump card display, always visible and not overlapped */}
                        {typeof arguments[0].trump_card === "string" && (
                            <div style={{
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                marginBottom: compact ? 8 : 18,
                                width: "100%"
                            }}>
                                <span style={{ fontWeight: 600, color: "#22c55e", fontSize: compact ? 13 : 18, marginBottom: 2 }}>Kozar card:</span>
                                <span style={{
                                    display: "inline-block",
                                    minWidth: 36,
                                    minHeight: 36,
                                    border: "2.5px solid #22c55e",
                                    borderRadius: 7,
                                    padding: compact ? "2px 7px" : "6px 14px",
                                    background: "#fff",
                                    fontSize: tableFont,
                                    fontWeight: 700,
                                    color: arguments[0].trump_card.includes("♥") || arguments[0].trump_card.includes("♦") ? "#e11d48" : "#222",
                                    textAlign: "center"
                                }}>{arguments[0].trump_card}</span>
                            </div>
                        )}
                        {/* Horizontal Attack/Defense Table */}
                        <div style={{ width: "100%", margin: compact ? "8px 0" : "18px 0", display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                            {/* Attack row */}
                            <div style={{ display: "flex", alignItems: "center", marginBottom: compact ? 4 : 10 }}>
                                <span style={{ fontWeight: 700, fontSize: tableFont, color: "#222", minWidth: 70, marginRight: 8 }}>Attack:</span>
                                <div style={{ display: "flex", gap: compact ? 4 : 10 }}>
                                    {(table_attack || []).map((card, i) => (
                                        <span key={i} style={{
                                            minWidth: 36,
                                            minHeight: 36,
                                            border: "2.5px solid #222",
                                            borderRadius: 7,
                                            padding: compact ? "2px 7px" : "6px 14px",
                                            background: card ? "#fff" : "#f1f5f9",
                                            fontSize: tableFont,
                                            fontWeight: 600,
                                            color: card && (card.includes("♥") || card.includes("♦")) ? "#e11d48" : "#222",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            marginRight: 2,
                                            opacity: card ? 1 : 0.3,
                                        }}>
                                            {card || <span>&#9633;</span>}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            {/* Defense row */}
                            <div style={{ display: "flex", alignItems: "center" }}>
                                <span style={{ fontWeight: 700, fontSize: tableFont, color: "#2563eb", minWidth: 70, marginRight: 8 }}>Defense:</span>
                                <div style={{ display: "flex", gap: compact ? 4 : 10 }}>
                                    {(table_defence || []).map((card, i) => (
                                        <span key={i} style={{
                                            minWidth: 36,
                                            minHeight: 36,
                                            border: "2.5px solid #2563eb",
                                            borderRadius: 7,
                                            padding: compact ? "2px 7px" : "6px 14px",
                                            background: card ? "#fff" : "#f1f5f9",
                                            fontSize: tableFont,
                                            fontWeight: 600,
                                            color: card && (card.includes("♥") || card.includes("♦")) ? "#e11d48" : "#2563eb",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            marginRight: 2,
                                            opacity: card ? 1 : 0.3,
                                        }}>
                                            {card || <span>&#9633;</span>}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                        {/* Game Log Box */}
                        <h3
                            style={{
                                fontWeight: 600,
                                fontSize: h3Font,
                                color: "#6366f1",
                                marginBottom: compact ? 4 : 8,
                                letterSpacing: 0.5,
                            }}
                        >
                            Game Log
                        </h3>
                        <div
                            style={{
                                background: "#f1f5f9",
                                border: "1px solid #e5e7eb",
                                borderRadius: 7,
                                height: logHeight,
                                minHeight: logHeight,
                                maxHeight: logHeight * 2,
                                overflowY: "auto",
                                padding: compact ? 4 : 12,
                                fontSize: compact ? 11 : 15,
                                width: "100%",
                                boxSizing: "border-box",
                                boxShadow: compact ? "0 1px 2px #a5b4fc11" : "0 1px 4px #a5b4fc22",
                                marginBottom: compact ? 6 : 12,
                                minWidth: 120,
                            }}
                        >
                            {gameLogEntries.length > 0
                                ? gameLogEntries.slice().reverse().map((entry, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            marginBottom: compact ? 2 : 6,
                                            color: "#475569",
                                            fontWeight: idx === 0 ? 600 : 400,
                                        }}
                                    >
                                        <span style={{ color: "#6366f1", fontWeight: 600 }}>
                                            {entry.bot}:
                                        </span>{" "}
                                        {entry.text}
                                    </div>
                                ))
                                : <div style={{ color: "#a1a1aa" }}>No log yet</div>
                            }
                        </div>
                        {/* Bot Logs Box */}
                        <h3
                            style={{
                                fontWeight: 600,
                                fontSize: h3Font,
                                color: "#6366f1",
                                marginBottom: compact ? 4 : 8,
                                letterSpacing: 0.5,
                            }}
                        >
                            Bot Logs
                        </h3>
                        <div
                            style={{
                                display: "flex",
                                gap: compact ? 6 : 18,
                                width: "100%",
                                marginBottom: compact ? 4 : 0,
                            }}
                        >
                            {log && Array.isArray(log) && log.length > 0
                                ? log.map((botLog, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            flex: 1,
                                            background: "#f1f5f9",
                                            border: "1px solid #e5e7eb",
                                            borderRadius: 7,
                                            height: logHeight,
                                            overflowY: "auto",
                                            padding: compact ? 4 : 12,
                                            fontSize: compact ? 11 : 15,
                                            boxSizing: "border-box",
                                            boxShadow: compact ? "0 1px 2px #a5b4fc11" : "0 1px 4px #a5b4fc22",
                                            minWidth: 0,
                                        }}
                                    >
                                        <div style={{ color: "#6366f1", fontWeight: 600, fontSize: compact ? 12 : 15, marginBottom: 4 }}>
                                            Player {idx + 1} {bots && bots[idx] ? `(${bots[idx]})` : ""}
                                        </div>
                                        {botLog && botLog.length > 0
                                            ? botLog.slice().reverse().map((entry, eidx) => (
                                                <div
                                                    key={eidx}
                                                    style={{
                                                        marginBottom: compact ? 2 : 6,
                                                        color: "#475569",
                                                        fontWeight: eidx === 0 ? 600 : 400,
                                                    }}
                                                >
                                                    {entry}
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
                </div>
                {/* Game Info area to the right */}
                <div style={{
                    minWidth: 180,
                    marginLeft: compact ? 10 : 36,
                    background: "rgba(255,255,255,0.92)",
                    borderRadius: 12,
                    boxShadow: "0 2px 12px #a5b4fc22",
                    padding: compact ? 10 : 24,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    fontSize: compact ? 14 : 18,
                    color: "#222",
                }}>
                    <div style={{ fontWeight: 700, fontSize: compact ? 15 : 22, color: "#6366f1", marginBottom: 10 }}>Game Info:</div>
                    <div style={{ marginBottom: 8 }}>
                        <span style={{ fontWeight: 500 }}>Burned Cards:</span> {arguments[0].num_of_burned_cards ?? arguments[0].state?.num_of_burned_cards ?? 0}
                    </div>
                    <div>
                        <span style={{ fontWeight: 500 }}>Trump Card:</span> <span style={{
                            display: "inline-block",
                            minWidth: 36,
                            minHeight: 28,
                            border: "2px solid #22c55e",
                            borderRadius: 7,
                            padding: compact ? "2px 7px" : "4px 12px",
                            background: "#fff",
                            fontSize: compact ? 16 : 22,
                            fontWeight: 700,
                            color: (arguments[0].trump_card ?? arguments[0].state?.trump_card ?? "").includes("♥") || (arguments[0].trump_card ?? arguments[0].state?.trump_card ?? "").includes("♦") ? "#e11d48" : "#222",
                            textAlign: "center"
                        }}>{(arguments[0].trump_card ?? arguments[0].state?.trump_card) || "?"}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}