import React from "react";

// CardGameUI expects props: hands, table_attack, table_defence, log, attacker, defender, bots, compact, status, deck_count, trump_card
export default function CardGameUI({ hands, table_attack, table_defence, log, attacker, defender, bots, compact, status, deck_count, trump_card, num_of_burned_cards, curr_player }) {
    const pad = compact ? 10 : 32;
    const cardPad = compact ? "6px 8px" : "16px 18px";
    const cardFont = compact ? 16 : 24;
    const minHandWidth = compact ? 90 : 180;
    const minHandHeight = compact ? 24 : 48;
    const h2Font = compact ? 20 : 36;
    const h3Font = compact ? 15 : 22;
    const boxPad = compact ? 10 : 24;
    const logHeight = compact ? 200 : 120;
    const tableFont = compact ? 15 : 22;
    const minTableWidth = compact ? 40 : 80;
    const maxHandBoxHeight = compact ? 170 : undefined;

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

    // Helper to chunk an array into rows of n
    function chunkArray(arr, n) {
        const result = [];
        for (let i = 0; i < arr.length; i += n) {
            result.push(arr.slice(i, i + n));
        }
        return result;
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
                marginLeft: "5cm", // Move everything 5cm to the right
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
                {/* Hands area (left), Table+Logs (middle), Game Info (right) */}
                <div style={{ display: "flex", flexDirection: "row", gap: compact ? 10 : 36 }}>
                    {/* Player hands in rows of 2 */}
                    <div style={{ display: "flex", flexDirection: "column", gap: compact ? 10 : 36 }}>
                        {chunkArray(hands, 2).map((handsRow, rowIdx) => (
                            <div key={rowIdx} style={{ display: "flex", gap: compact ? 10 : 36, marginBottom: compact ? 6 : 18, justifyContent: "center" }}>
                                {handsRow.map((hand, idxInRow) => {
                                    const playerIdx = rowIdx * 2 + idxInRow;
                                    const isCurrent = curr_player === playerIdx;
                                    return (
                                        <div
                                            key={playerIdx}
                                            style={{
                                                border: isCurrent ? "3px solid #f59e42" : "2px solid #e5e7eb",
                                                boxShadow: isCurrent ? "0 0 12px 2px #f59e4288" : undefined,
                                                borderRadius: 10,
                                                background: isCurrent ? "#fff7ed" : "#f8fafc",
                                                padding: compact ? 4 : 12,
                                                minWidth: 90,
                                                minHeight: 60,
                                                display: "flex",
                                                flexDirection: "column",
                                                alignItems: "center",
                                                transition: "box-shadow 0.2s, border 0.2s, background 0.2s",
                                            }}
                                        >
                                            <div style={{ fontWeight: 700, color: isCurrent ? "#f59e42" : "#222", marginBottom: 4 }}>
                                                Player {playerIdx + 1} {bots && bots[playerIdx] ? `(${bots[playerIdx]})` : ""}
                                                {isCurrent && <span style={{ marginLeft: 6, fontSize: 13, color: "#f59e42" }}>(Current)</span>}
                                            </div>
                                            <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                                                {hand.map((card, cidx) => (
                                                    <span key={cidx} style={{
                                                        border: "1.5px solid #cbd5e1",
                                                        borderRadius: 5,
                                                        background: "#fff",
                                                        padding: compact ? "1px 5px" : "3px 10px",
                                                        fontSize: compact ? 15 : 22,
                                                        fontWeight: 600,
                                                        color: card && (card.includes("♥") || card.includes("♦")) ? "#e11d48" : "#222",
                                                        marginRight: 2,
                                                        marginBottom: 2,
                                                    }}>{card}</span>
                                                ))}
                                            </div>
                                            {status && status[playerIdx] && (
                                                <div style={{ fontSize: 12, color: "#6366f1", marginTop: 2 }}>{status[playerIdx]}</div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                    {/* Table and logs area (middle) */}
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
                            Deck: {deck_count}
                        </div>
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
                                            color: card && (card.includes("♥") || card.includes("♦")) ? "#e11d48" : "#222", // black for non-red suits
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
                                            background: curr_player === idx ? "#fff7ed" : "#f1f5f9",
                                            border: curr_player === idx ? "2.5px solid #f59e42" : "1px solid #e5e7eb",
                                            borderRadius: 7,
                                            height: logHeight,
                                            overflowY: "auto",
                                            padding: compact ? 4 : 12,
                                            fontSize: compact ? 11 : 15,
                                            boxSizing: "border-box",
                                            boxShadow: curr_player === idx ? "0 0 8px 1px #f59e4288" : (compact ? "0 1px 2px #a5b4fc11" : "0 1px 4px #a5b4fc22"),
                                            minWidth: 0,
                                            transition: "box-shadow 0.2s, border 0.2s, background 0.2s",
                                        }}
                                    >
                                        <div style={{ color: curr_player === idx ? "#f59e42" : "#6366f1", fontWeight: 600, fontSize: compact ? 12 : 15, marginBottom: 4 }}>
                                            Player {idx + 1} {bots && bots[idx] ? `(${bots[idx]})` : ""}
                                            {curr_player === idx && <span style={{ marginLeft: 6, fontSize: 13, color: "#f59e42" }}>(Current)</span>}
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
                    {/* Game Info area (right) */}
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
                            <span style={{ fontWeight: 500 }}>Burned Cards:</span> {num_of_burned_cards}
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
                                color: trump_card && (trump_card.includes("♥") || trump_card.includes("♦")) ? "#e11d48" : "#222",
                                textAlign: "center"
                            }}>{trump_card || "?"}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}