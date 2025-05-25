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
            <div style={{ display: "flex", gap: compact ? 10 : 36, justifyContent: "center" }}>
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
                        <div style={{ display: "flex", gap: compact ? 4 : 12, marginBottom: compact ? 6 : 18 }}>
                            {hand.map((card, cidx) => (
                                <div
                                    key={cidx}
                                    style={{
                                        border: "none",
                                        borderRadius: 7,
                                        padding: cardPad,
                                        background: "linear-gradient(120deg, #f1f5f9 60%, #c7d2fe 100%)",
                                        fontSize: cardFont,
                                        boxShadow: compact ? "0 1px 3px #a5b4fc33" : "0 2px 8px #a5b4fc55",
                                        color: "#1e293b",
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
                    </div>
                ))}
                <div
                    style={{
                        minWidth: compact ? 120 : 260,
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
                        marginBottom: compact ? 4 : 10,
                        color: "#0f172a",
                        fontWeight: 600,
                        fontSize: compact ? 13 : 18,
                    }}>
                        Deck left: {deckCount}
                    </div>
                    <div
                        style={{
                            background: "#f1f5f9",
                            border: "1px solid #e5e7eb",
                            borderRadius: 7,
                            minHeight: minHandHeight,
                            minWidth: minTableWidth,
                            padding: compact ? 4 : 12,
                            fontSize: tableFont,
                            marginBottom: compact ? 6 : 16,
                            display: "flex",
                            flexDirection: "column",
                            gap: compact ? 2 : 8,
                            flexWrap: "nowrap",
                            justifyContent: "center",
                        }}
                    >
                        {table_attack && table_attack.length > 0
                            ? renderTablePairs(table_attack, table_defence)
                            : <span style={{ color: "#a1a1aa" }}>No cards</span>
                        }
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
                            overflowY: "auto",
                            padding: compact ? 4 : 12,
                            fontSize: compact ? 11 : 15,
                            width: "100%",
                            boxSizing: "border-box",
                            boxShadow: compact ? "0 1px 2px #a5b4fc11" : "0 1px 4px #a5b4fc22",
                            marginBottom: compact ? 6 : 12,
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
        </div>
    );
}