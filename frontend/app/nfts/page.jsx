"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TIER_COLORS = {
    1: "#86efac", 2: "#4ade80", 3: "#22c55e", 4: "#16a34a", 5: "#f59e0b"
};

function NFTCard({ nft, index }) {
    const tier = nft.tier || { tier: 1, name: "Eco Spark", icon: "✨" };
    const color = nft.color || "#22c55e";
    const monthsOld = nft.months_old || 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            style={{
                padding: "20px", borderRadius: 18, marginBottom: 14,
                background: "linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,30,0,0.5))",
                border: `1px solid ${color}44`,
                position: "relative", overflow: "hidden",
            }}>

            {/* Glow */}
            <div style={{
                position: "absolute", top: -30, right: -30,
                width: 100, height: 100, borderRadius: "50%",
                background: `${color}15`,
                filter: "blur(20px)",
            }} />

            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
                <motion.div
                    animate={{ rotate: [0, 5, -5, 0] }}
                    transition={{ repeat: Infinity, duration: 4, delay: index * 0.5 }}
                    style={{ fontSize: 44 }}>
                    {nft.icon}
                </motion.div>
                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 11, letterSpacing: 3, color: "#4b5563", fontFamily: "monospace" }}>
                        {nft.month_name?.toUpperCase()} {nft.year} WINNER
                    </div>
                    <div style={{ fontSize: 18, fontWeight: 800, color }}>
                        {nft.theme}
                    </div>
                    <div style={{ fontSize: 11, color: "#6b7280" }}>
                        {tier.icon} {tier.name} — Stage {tier.tier}/5
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
                {[
                    { label: "XP Earned", value: nft.xp, icon: "⚡" },
                    { label: "CO₂ Saved", value: `${nft.carbon?.toFixed(1)}kg`, icon: "🌿" },
                    { label: "Age", value: `${monthsOld}mo`, icon: "⏳" },
                ].map(s => (
                    <div key={s.label} style={{
                        flex: 1, textAlign: "center", padding: "8px",
                        borderRadius: 10, background: "rgba(255,255,255,0.03)",
                        border: "1px solid rgba(255,255,255,0.05)",
                    }}>
                        <div style={{ fontSize: 14 }}>{s.icon}</div>
                        <div style={{ fontSize: 13, fontWeight: 700, color: "#f0fdf4" }}>{s.value}</div>
                        <div style={{ fontSize: 9, color: "#4b5563", fontFamily: "monospace" }}>{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Evolution progress */}
            <div style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#4b5563", fontFamily: "monospace", marginBottom: 4 }}>
                    <span>Evolution: Stage {tier.tier}/5</span>
                    <span>{monthsOld < 3 ? `${3 - monthsOld}mo to Stage 2` : monthsOld < 6 ? `${6 - monthsOld}mo to Stage 3` : "Evolved!"}</span>
                </div>
                <div style={{ height: 4, borderRadius: 2, background: "rgba(255,255,255,0.06)" }}>
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(100, (tier.tier / 5) * 100)}%` }}
                        transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                        style={{ height: "100%", borderRadius: 2, background: `linear-gradient(90deg, ${color}66, ${color})` }}
                    />
                </div>
            </div>

            {/* NFT ID */}
            <div style={{ fontSize: 10, color: "#22222", fontFamily: "monospace", opacity: 0.4 }}>
                {nft.nft_id}
            </div>
        </motion.div>
    );
}

function WinnerCard({ winner, index }) {
    const theme = winner.theme || {};
    return (
        <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.08 }}
            style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "12px 16px", borderRadius: 12, marginBottom: 8,
                background: index === 0 ? "rgba(245,158,11,0.08)" : "rgba(0,255,100,0.03)",
                border: index === 0 ? "1px solid #f59e0b33" : "1px solid rgba(0,255,100,0.06)",
            }}>
            <span style={{ fontSize: 28 }}>{index === 0 ? "🏆" : theme.icon || "🌱"}</span>
            <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0" }}>
                    {winner.user_name} — {winner.month_name} {winner.year}
                </div>
                <div style={{ fontSize: 11, color: "#6b7280" }}>{theme.theme}</div>
            </div>
            <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 12, color: "#4ade80", fontFamily: "monospace" }}>{winner.xp} XP</div>
                <div style={{ fontSize: 10, color: "#34d399", fontFamily: "monospace" }}>{winner.carbon?.toFixed(1)}kg</div>
            </div>
        </motion.div>
    );
}

export default function NFTsPage() {
    const [myNfts, setMyNfts] = useState([]);
    const [winners, setWinners] = useState([]);
    const [tab, setTab] = useState("my-nfts");
    const [minting, setMinting] = useState(false);
    const [toast, setToast] = useState(null);
    const userId = "user";

    useEffect(() => { fetchAll(); }, []);

    const fetchAll = async () => {
        try {
            const [nRes, wRes] = await Promise.all([
                fetch(`http://127.0.0.1:8000/api/nfts/${userId}`),
                fetch("http://127.0.0.1:8000/api/nft/winners"),
            ]);
            setMyNfts(await nRes.json());
            setWinners(await wRes.json());
        } catch (e) { }
    };

    const showToast = (msg, type = "success") => {
        setToast({ msg, type });
        setTimeout(() => setToast(null), 3000);
    };

    const mintWinner = async () => {
        setMinting(true);
        try {
            const res = await fetch("http://127.0.0.1:8000/api/nft/mint-winner", { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(`🎉 NFT Minted! ${data.icon} ${data.theme}`);
                fetchAll();
                setTab("my-nfts");
            } else {
                showToast(data.error, "error");
            }
        } catch (e) {
            showToast("Connection error", "error");
        } finally {
            setMinting(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
                minHeight: "100vh", background: "#030b03",
                backgroundImage: "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,80,20,0.3) 0%, transparent 70%)",
                fontFamily: "'Syne','Space Grotesk',sans-serif",
                color: "#f0fdf4", padding: "40px 20px 80px",
            }}>
            <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono&display=swap');
        .tab-btn.active{border-color:#22c55e!important;color:#22c55e!important;background:rgba(34,197,94,0.08)!important;}
      `}</style>

            {/* Toast */}
            <AnimatePresence>
                {toast && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                        style={{
                            position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)",
                            padding: "12px 24px", borderRadius: 12, zIndex: 9999,
                            background: toast.type === "error" ? "rgba(239,68,68,0.9)" : "rgba(34,197,94,0.9)",
                            color: "#fff", fontSize: 13, fontWeight: 600,
                        }}>
                        {toast.msg}
                    </motion.div>
                )}
            </AnimatePresence>

            <div style={{ maxWidth: 520, margin: "0 auto" }}>

                {/* Header */}
                <div style={{ textAlign: "center", marginBottom: 28 }}>
                    <div style={{ fontSize: 11, letterSpacing: 4, color: "#22c55e44", textTransform: "uppercase", marginBottom: 8, fontFamily: "monospace" }}>
                        GaiaVolt · Day 27 · Dynamic NFTs
                    </div>
                    <h1 style={{
                        margin: 0, fontSize: "clamp(22px,5vw,36px)", fontWeight: 800,
                        background: "linear-gradient(135deg,#f59e0b,#fde047,#f59e0b)",
                        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                    }}>Living NFTs</h1>
                    <p style={{ margin: "8px 0 0", fontSize: 12, color: "#374151", fontFamily: "monospace" }}>
                        Waqt ke saath evolve karte hain — 2050 tak!
                    </p>
                </div>

                {/* Mint button */}
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={mintWinner}
                    disabled={minting}
                    style={{
                        width: "100%", padding: "14px", borderRadius: 14, border: "none",
                        background: "linear-gradient(135deg,#92400e,#f59e0b,#fde047)",
                        color: "#000", fontWeight: 800, fontSize: 14, cursor: "pointer",
                        marginBottom: 20,
                    }}>
                    {minting ? "⏳ Minting..." : "🏆 Mint This Month's Winner NFT"}
                </motion.button>

                {/* Tabs */}
                <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
                    {[
                        { id: "my-nfts", label: `🎨 My NFTs ${myNfts.length > 0 ? `(${myNfts.length})` : ""}` },
                        { id: "winners", label: `🏆 Hall of Fame` },
                    ].map(t => (
                        <motion.button key={t.id} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                            className={`tab-btn${tab === t.id ? " active" : ""}`}
                            onClick={() => setTab(t.id)}
                            style={{
                                flex: 1, padding: "12px", borderRadius: 12, cursor: "pointer",
                                border: "1px solid #1a2e1a", background: "rgba(255,255,255,0.02)",
                                color: "#6b7280", fontSize: 12, fontWeight: 600, transition: "all 0.2s",
                            }}>
                            {t.label}
                        </motion.button>
                    ))}
                </div>

                <AnimatePresence mode="wait">
                    {tab === "my-nfts" && (
                        <motion.div key="nfts" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            {myNfts.length > 0 ? (
                                myNfts.map((n, i) => <NFTCard key={n.nft_id} nft={n} index={i} />)
                            ) : (
                                <div style={{ textAlign: "center", padding: 40, color: "#374151" }}>
                                    <div style={{ fontSize: 48, marginBottom: 10 }}>🎨</div>
                                    <div style={{ fontSize: 13 }}>No NFTs yet!</div>
                                    <div style={{ fontSize: 11, marginTop: 6, color: "#1f2937" }}>
                                        Be the monthly winner to get your first NFT
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}

                    {tab === "winners" && (
                        <motion.div key="winners" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            <div style={{ fontSize: 10, letterSpacing: 3, color: "#1f3a1f", textTransform: "uppercase", marginBottom: 12, fontFamily: "monospace" }}>
                                ▸ Monthly Champions
                            </div>
                            {winners.length > 0 ? (
                                winners.map((w, i) => <WinnerCard key={i} winner={w} index={i} />)
                            ) : (
                                <div style={{ textAlign: "center", padding: 40, color: "#374151" }}>
                                    <div style={{ fontSize: 48, marginBottom: 10 }}>🏆</div>
                                    <div style={{ fontSize: 13 }}>No winners yet!</div>
                                    <div style={{ fontSize: 11, marginTop: 6, color: "#1f2937" }}>
                                        First winner will be announced end of month
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Nav */}
                <div style={{ display: "flex", gap: 8, marginTop: 24 }}>
                    {[
                        { href: "/verify", label: "⚡ Earn XP", bg: "linear-gradient(135deg,#16a34a,#22c55e)", color: "#fff" },
                        { href: "/evolution", label: "🌱 Journey", bg: "transparent", color: "#6b7280", border: "1px solid #1a2e1a" },
                        { href: "/bridges", label: "🏪 Store", bg: "transparent", color: "#6b7280", border: "1px solid #1a2e1a" },
                    ].map(b => (
                        <motion.div key={b.href} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} style={{ flex: 1 }}>
                            <a href={b.href} style={{
                                display: "block", padding: "11px", borderRadius: 12,
                                textDecoration: "none", textAlign: "center",
                                background: b.bg, color: b.color,
                                fontWeight: 700, fontSize: 12,
                                border: b.border || "none",
                            }}>{b.label}</a>
                        </motion.div>
                    ))}
                </div>

                <div style={{ marginTop: 28, textAlign: "center", fontSize: 10, color: "#1a2e1a", fontFamily: "monospace", letterSpacing: 2 }}>
                    ERC-721 · POLYGON · EVOLVES UNTIL 2050
                </div>
            </div>
        </motion.div>
    );
}