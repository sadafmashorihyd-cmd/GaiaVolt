"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

function PartnerCard({ partner, userCoins, onClaim, claiming }) {
    const [expanded, setExpanded] = useState(false);
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
                borderRadius: 16, marginBottom: 14, overflow: "hidden",
                border: `1px solid ${partner.color}33`,
                background: "rgba(0,0,0,0.4)",
            }}>
            {/* Header */}
            <div
                onClick={() => setExpanded(!expanded)}
                style={{
                    padding: "16px 18px", cursor: "pointer",
                    display: "flex", alignItems: "center", gap: 14,
                    background: `${partner.color}08`,
                }}>
                <span style={{ fontSize: 32 }}>{partner.icon}</span>
                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "#f0fdf4" }}>{partner.name}</div>
                    <div style={{ fontSize: 12, color: "#6b7280" }}>{partner.description}</div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{
                        fontSize: 11, padding: "4px 10px", borderRadius: 20,
                        background: `${partner.color}22`, color: partner.color,
                        fontFamily: "monospace",
                    }}>
                        {partner.deals.length} deals
                    </span>
                    <span style={{ color: "#4b5563", fontSize: 14 }}>{expanded ? "▲" : "▼"}</span>
                </div>
            </div>

            {/* Deals */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        style={{ overflow: "hidden" }}>
                        {partner.deals.map(deal => (
                            <div key={deal.id} style={{
                                padding: "14px 18px",
                                borderTop: `1px solid ${partner.color}11`,
                                display: "flex", alignItems: "center", gap: 12,
                            }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0" }}>{deal.title}</div>
                                    <div style={{ fontSize: 11, color: "#6b7280", marginTop: 3 }}>{deal.description}</div>
                                    <div style={{ fontSize: 11, color: "#4b5563", marginTop: 4, fontFamily: "monospace" }}>
                                        Valid: {deal.valid_days} days
                                    </div>
                                </div>
                                <div style={{ textAlign: "center", minWidth: 80 }}>
                                    <div style={{
                                        fontSize: 14, fontWeight: 700, color: partner.color,
                                        fontFamily: "monospace",
                                    }}>
                                        🪙 {deal.eco_coins}
                                    </div>
                                    <div style={{ fontSize: 10, color: "#4b5563", marginBottom: 6 }}>GAIA coins</div>
                                    <motion.button
                                        whileHover={{ scale: userCoins >= deal.eco_coins ? 1.05 : 1 }}
                                        whileTap={{ scale: 0.97 }}
                                        onClick={() => onClaim(partner.id, deal.id, deal.eco_coins)}
                                        disabled={userCoins < deal.eco_coins || claiming}
                                        style={{
                                            padding: "7px 14px", borderRadius: 8, border: "none",
                                            cursor: userCoins >= deal.eco_coins ? "pointer" : "not-allowed",
                                            background: userCoins >= deal.eco_coins
                                                ? `linear-gradient(135deg, ${partner.color}cc, ${partner.color})`
                                                : "rgba(255,255,255,0.05)",
                                            color: userCoins >= deal.eco_coins ? "#fff" : "#374151",
                                            fontSize: 11, fontWeight: 700,
                                        }}>
                                        {userCoins >= deal.eco_coins ? "Claim" : "Coming Soon"}
                                    </motion.button>
                                </div>
                            </div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

function CouponCard({ coupon }) {
    const [copied, setCopied] = useState(false);
    const copy = () => {
        navigator.clipboard.writeText(coupon.coupon_code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{
                padding: "16px", borderRadius: 14, marginBottom: 10,
                background: "linear-gradient(135deg, rgba(0,0,0,0.5), rgba(0,40,0,0.3))",
                border: "1px solid #22c55e33",
            }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", marginBottom: 6 }}>
                {coupon.deal_title}
            </div>
            <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "10px 14px", borderRadius: 10,
                background: "rgba(0,0,0,0.4)", border: "1px solid #22c55e22",
                marginBottom: 8,
            }}>
                <span style={{ fontFamily: "monospace", fontSize: 16, fontWeight: 700, color: "#22c55e", letterSpacing: 2 }}>
                    {coupon.coupon_code}
                </span>
                <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={copy}
                    style={{
                        padding: "5px 12px", borderRadius: 6, border: "none",
                        background: copied ? "#22c55e" : "rgba(34,197,94,0.2)",
                        color: copied ? "#fff" : "#22c55e",
                        fontSize: 11, cursor: "pointer", fontWeight: 600,
                    }}>
                    {copied ? "Copied!" : "Copy"}
                </motion.button>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#4b5563", fontFamily: "monospace" }}>
                <span>🪙 {coupon.eco_coins} GAIA spent</span>
                <span style={{ color: coupon.days_left <= 3 ? "#ef4444" : "#6b7280" }}>
                    {coupon.days_left}d left
                </span>
            </div>
        </motion.div>
    );
}

export default function BridgesPage() {
    const [partners, setPartners] = useState([]);
    const [coupons, setCoupons] = useState([]);
    const [userCoins, setUserCoins] = useState(0);
    const [tab, setTab] = useState("store");
    const [claiming, setClaiming] = useState(false);
    const [toast, setToast] = useState(null);
    const userId = "user";

    useEffect(() => {
        fetchAll();
    }, []);

    const fetchAll = async () => {
        try {
            const [pRes, cRes, pRes2] = await Promise.all([
                fetch("http://127.0.0.1:8000/api/partners"),
                fetch(`http://127.0.0.1:8000/api/coupons/${userId}`),
                fetch(`http://127.0.0.1:8000/api/profile/${userId}`),
            ]);
            setPartners(await pRes.json());
            setCoupons(await cRes.json());
            const profile = await pRes2.json();
            setUserCoins(profile?.user?.coins_total || 0);
        } catch (e) { console.error(e); }
    };

    const showToast = (msg, type = "success") => {
        setToast({ msg, type });
        setTimeout(() => setToast(null), 3000);
    };

    const handleClaim = async (partnerId, dealId, cost) => {
        if (userCoins < cost) { showToast("Not enough GAIA coins!", "error"); return; }
        setClaiming(true);
        try {
            const res = await fetch("http://127.0.0.1:8000/api/claim-coupon", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, partner_id: partnerId, deal_id: dealId }),
            });
            const data = await res.json();
            if (data.success) {
                showToast(`✅ Coupon claimed! Code: ${data.coupon_code}`);
                setUserCoins(prev => prev - data.coins_spent);
                fetchAll();
                setTab("my-coupons");
            } else {
                showToast(data.error, "error");
            }
        } catch (e) {
            showToast("Connection error", "error");
        } finally {
            setClaiming(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
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
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        style={{
                            position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)",
                            padding: "12px 24px", borderRadius: 12, zIndex: 9999,
                            background: toast.type === "error" ? "rgba(239,68,68,0.9)" : "rgba(34,197,94,0.9)",
                            color: "#fff", fontSize: 13, fontWeight: 600,
                            boxShadow: "0 4px 20px rgba(0,0,0,0.4)",
                        }}>
                        {toast.msg}
                    </motion.div>
                )}
            </AnimatePresence>

            <div style={{ maxWidth: 520, margin: "0 auto" }}>

                {/* Header */}
                <div style={{ textAlign: "center", marginBottom: 28 }}>
                    <div style={{ fontSize: 11, letterSpacing: 4, color: "#22c55e44", textTransform: "uppercase", marginBottom: 8, fontFamily: "monospace" }}>
                        GaiaVolt · Day 26 · Real-World Bridges
                    </div>
                    <h1 style={{
                        margin: 0, fontSize: "clamp(22px,5vw,36px)", fontWeight: 800,
                        background: "linear-gradient(135deg,#86efac,#22c55e,#4ade80)",
                        WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                    }}>GaiaVolt Rewards Store</h1>
                    <p style={{ margin: "8px 0 0", fontSize: 12, color: "#374151", fontFamily: "monospace" }}>
                        Redeem GaiaVolt coins for real-world discounts
                    </p>
                </div>

                {/* Coins balance */}
                <motion.div
                    style={{
                        display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
                        padding: "14px 20px", borderRadius: 14, marginBottom: 20,
                        background: "linear-gradient(135deg,rgba(34,197,94,0.1),rgba(74,222,128,0.05))",
                        border: "1px solid rgba(34,197,94,0.2)",
                    }}>
                    <span style={{ fontSize: 24 }}>🪙</span>
                    <span style={{ fontSize: 22, fontWeight: 800, color: "#22c55e", fontFamily: "monospace" }}>
                        {userCoins.toFixed(1)} GAIA
                    </span>
                    <span style={{ fontSize: 12, color: "#4b5563" }}>available</span>
                </motion.div>

                {/* Tabs */}
                <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
                    {[
                        { id: "store", label: "🏪 Store" },
                        { id: "my-coupons", label: `🎟️ My Coupons ${coupons.length > 0 ? `(${coupons.length})` : ""}` },
                    ].map(t => (
                        <motion.button
                            key={t.id}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
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

                {/* Store */}
                <AnimatePresence mode="wait">
                    {tab === "store" && (
                        <motion.div key="store" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            {partners.map(p => (
                                <PartnerCard
                                    key={p.id} partner={p}
                                    userCoins={userCoins}
                                    onClaim={handleClaim}
                                    claiming={claiming}
                                />
                            ))}
                        </motion.div>
                    )}

                    {tab === "my-coupons" && (
                        <motion.div key="coupons" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                            {coupons.length > 0 ? (
                                coupons.map((c, i) => <CouponCard key={i} coupon={c} />)
                            ) : (
                                <div style={{ textAlign: "center", padding: 40, color: "#374151" }}>
                                    <div style={{ fontSize: 40, marginBottom: 10 }}>🎟️</div>
                                    <div style={{ fontSize: 13 }}>No coupons yet!</div>
                                    <div style={{ fontSize: 11, marginTop: 6, color: "#1f2937" }}>
                                        Earn GAIA coins → claim discounts
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Back buttons */}
                <div style={{ display: "flex", gap: 8, marginTop: 20 }}>
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ flex: 1 }}>
                        <a href="/verify" style={{
                            display: "block", padding: "12px", borderRadius: 12,
                            textDecoration: "none", textAlign: "center",
                            background: "linear-gradient(135deg,#16a34a,#22c55e)",
                            color: "#fff", fontWeight: 700, fontSize: 13,
                        }}>⚡ Earn More GAIA</a>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} style={{ flex: 1 }}>
                        <a href="/evolution" style={{
                            display: "block", padding: "12px", borderRadius: 12,
                            textDecoration: "none", textAlign: "center",
                            border: "1px solid #1a2e1a", background: "transparent",
                            color: "#6b7280", fontWeight: 600, fontSize: 13,
                        }}>🌱 My Journey</a>
                    </motion.div>
                </div>

                <div style={{ marginTop: 32, textAlign: "center", fontSize: 10, color: "#1a2e1a", fontFamily: "monospace", letterSpacing: 2 }}>
                    6 GAIAVOLT PARTNERS · REAL DISCOUNTS · COMING SOON: MORE
                </div>
            </div>
        </motion.div>
    );
}