import React from "react";

// CardGameUI expects props: hands, table, log, attacker, defender, bots, compact
export default function CardGameUI({ hands, table, log, attacker, defender, bots, compact }) {
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
                            gap: compact ? 2 : 8,
                            flexWrap: "wrap",
                            justifyContent: "center",
                        }}
                    >
                        {table && table.length > 0
                            ? table.map((card, idx) => (
                                <span key={idx} style={{ margin: 2 }}>{card}</span>
                            ))
                            : <span style={{ color: "#a1a1aa" }}>No cards</span>
                        }
                    </div>
                    <h3
                        style={{
                            fontWeight: 600,
                            fontSize: h3Font,
                            color: "#6366f1",
                            marginBottom: compact ? 4 : 12,
                            letterSpacing: 0.5,
                        }}
                    >
                        Logs
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
                        }}
                    >
                        {log && log.length > 0
                            ? log.slice().reverse().map((entry, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        marginBottom: compact ? 2 : 6,
                                        color: "#475569",
                                        fontWeight: idx === 0 ? 600 : 400,
                                    }}
                                >
                                    {entry}
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