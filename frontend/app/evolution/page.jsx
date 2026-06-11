"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

function getApiBase() {
    if (process.env.NEXT_PUBLIC_API_URL) {
        return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
    }
    if (typeof window !== "undefined") {
        const h = window.location.hostname;
        if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:8000";
        return `https://sadafmashori-gaiavolt.hf.space`;
    }
    return "http://127.0.0.1:8000";
}

const API_BASE = getApiBase();

function getUserFromStorage() {
    if (typeof window === "undefined") return { userId: null, name: null, token: null };
    try {
        const token = localStorage.getItem("gv_token");
        const userRaw = localStorage.getItem("gv_user");
        if (!token) return { userId: null, name: null, token: null };
        if (userRaw) {
            const u = JSON.parse(userRaw);
            if (u?.user_id) return { userId: u.user_id, name: u.name, token };
        }
        const payloadB64 = token.split(".")[0];
        const payload = JSON.parse(atob(payloadB64.replace(/-/g, "+").replace(/_/g, "/")));
        return { userId: payload.user_id || null, name: payload.name || "Eco Hero", token };
    } catch {
        return { userId: null, name: null, token: null };
    }
}

const LEVELS = [
    { level: 1, name: "Seedling", icon: "🌱", xp_required: 0, color: "#86efac" },
    { level: 2, name: "Sapling", icon: "🌿", xp_required: 100, color: "#4ade80" },
    { level: 3, name: "Young Tree", icon: "🌳", xp_required: 300, color: "#22c55e" },
    { level: 4, name: "Forest Guardian", icon: "🌲", xp_required: 700, color: "#16a34a" },
    { level: 5, name: "Eco Warrior", icon: "🦅", xp_required: 1500, color: "#15803d" },
    { level: 6, name: "Planet Protector", icon: "🌍", xp_required: 3000, color: "#166534" },
    { level: 7, name: "Carbon Zero Hero", icon: "⚡", xp_required: 6000, color: "#f59e0b" },
];

function getLevelForXP(xp) {
    let cur = LEVELS[0];
    for (const l of LEVELS) { if (xp >= l.xp_required) cur = l; }
    return cur;
}
function getNextLevel(lvl) {
    return LEVELS.find(l => l.level === lvl + 1) || null;
}

function XPRing({ xp, level, color, size = 120 }) {
    const r = size / 2 - 8, c = size / 2, circ = 2 * Math.PI * r;
    const next = getNextLevel(level.level);
    const pct = next ? Math.min(100, ((xp - level.xp_required) / (next.xp_required - level.xp_required)) * 100) : 100;
    return (
        <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
            <circle cx={c} cy={c} r={r} fill="none" stroke="#1a2a1a" strokeWidth={8} />
            <circle cx={c} cy={c} r={r} fill="none" stroke={color} strokeWidth={8}
                strokeDasharray={`${circ * pct / 100} ${circ}`} strokeLinecap="round"
                style={{ transition: "stroke-dasharray 1.2s ease", filter: `drop-shadow(0 0 8px ${color})` }} />
        </svg>
    );
}

function StatCard({ icon, label, value, color }) {
    return (
        <div style={{ flex: 1, padding: "14px 10px", borderRadius: 12, textAlign: "center", background: "rgba(0,255,100,0.03)", border: "1px solid rgba(0,255,100,0.08)" }}>
            <div style={{ fontSize: 22 }}>{icon}</div>
            <div style={{ fontSize: 18, fontWeight: 800, color, fontFamily: "monospace", marginTop: 4 }}>{value}</div>
            <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: 1, marginTop: 2 }}>{label}</div>
        </div>
    );
}

function ActivityRow({ act }) {
    const icons = { plantation: "🌱", recycling: "♻️", cycling: "🚲", solar_panels: "☀️", led_lighting: "💡", ocean_cleanup: "🌊" };
    const t = new Date(act.time);
    const timeStr = isNaN(t) ? act.time : t.toLocaleDateString("en-PK", { month: "short", day: "numeric" });
    return (
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", borderRadius: 10, marginBottom: 6, background: "rgba(0,255,100,0.02)", border: "1px solid rgba(0,255,100,0.06)" }}>
            <span style={{ fontSize: 20 }}>{icons[act.activity] || "🌿"}</span>
            <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 600, textTransform: "capitalize" }}>{act.activity.replace(/_/g, " ")}</div>
                <div style={{ fontSize: 11, color: "#4b5563" }}>{timeStr}</div>
            </div>
            <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 12, color: "#22c55e", fontFamily: "monospace" }}>+{act.xp} XP</div>
                <div style={{ fontSize: 11, color: "#6ee7b7" }}>+{act.coins?.toFixed(1)} GAIA</div>
            </div>
        </div>
    );
}

export default function EvolutionPage() {
    const router = useRouter();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [tab, setTab] = useState("profile");
    const [leaderboard, setLeaderboard] = useState([]);
    const [userId, setUserId] = useState(null);
    const [name, setName] = useState(null);
    const [token, setToken] = useState(null);

    // ── AUTH GUARD ────────────────────────────────────────────────────────────
    useEffect(() => {
        const u = getUserFromStorage();
        if (!u.token) {
            router.push('/auth');
            return;
        }
        setUserId(u.userId);
        setName(u.name);
        setToken(u.token);
    }, [router]);

    const fetchProfile = async () => {
        if (!userId) { setError("Login required."); setLoading(false); return; }
        try {
            setLoading(true);
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const res = await fetch(`${API_BASE}/api/profile/${userId}`, { headers });
            if (!res.ok) throw new Error(`Server error ${res.status}`);
            const data = await res.json();
            setProfile(data); setError(null);
        } catch (e) {
            setError(`Cannot load profile — ${e.message}`);
        } finally {
            setLoading(false);
        }
    };

    const fetchLeaderboard = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/leaderboard/global`);
            const data = await res.json();
            setLeaderboard(data.leaderboard || []);
        } catch { }
    };

    useEffect(() => {
        if (userId === null) return;
        fetchProfile();
        fetchLeaderboard();
        const iv = setInterval(() => { fetchProfile(); fetchLeaderboard(); }, 30000);
        return () => clearInterval(iv);
    }, [userId]);

    const user = profile?.user;
    const xp = user?.xp || 0;
    const level = getLevelForXP(xp);
    const nextLvl = getNextLevel(level.level);
    const xpProgress = profile?.xp_progress ?? (nextLvl ? Math.min(100, Math.round(((xp - level.xp_required) / (nextLvl.xp_required - level.xp_required)) * 100)) : 100);

    return (
        <div style={{ minHeight: "100vh", background: "#030b03", backgroundImage: "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,80,20,0.35) 0%, transparent 70%)", fontFamily: "'Syne','Space Grotesk',sans-serif", color: "#f0fdf4", padding: "48px 20px 80px" }}>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono&display=swap');
                @keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
                @keyframes spin{to{transform:rotate(360deg)}}
                .tab-btn:hover{color:#22c55e!important;}
            `}</style>
            <div style={{ maxWidth: 520, margin: "0 auto" }}>
                <div style={{ textAlign: "center", marginBottom: 28 }}>
                    <div style={{ fontSize: 11, letterSpacing: 4, color: "#22c55e66", textTransform: "uppercase", marginBottom: 8, fontFamily: "monospace" }}>GaiaVolt · Evolution · Day 25</div>
                    <h1 style={{ margin: 0, fontSize: "clamp(24px,6vw,36px)", fontWeight: 800, background: "linear-gradient(135deg,#86efac,#22c55e,#4ade80)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Your Evolution</h1>
                    {userId && <div style={{ fontSize: 12, color: "#4b5563", marginTop: 6, fontFamily: "monospace" }}>{user?.display_name || name || userId}</div>}
                </div>

                <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
                    {[["profile", "👤 Profile"], ["leaderboard", "🏆 Leaderboard"]].map(([id, label]) => (
                        <button key={id} className="tab-btn" onClick={() => setTab(id)} style={{ flex: 1, padding: "11px", borderRadius: 10, cursor: "pointer", border: `1px solid ${tab === id ? "#22c55e" : "#1a2e1a"}`, background: tab === id ? "rgba(34,197,94,0.1)" : "rgba(255,255,255,0.02)", color: tab === id ? "#22c55e" : "#6b7280", fontSize: 13, fontWeight: 600, transition: "all 0.2s" }}>{label}</button>
                    ))}
                </div>

                {error && <div style={{ padding: "12px 16px", borderRadius: 10, marginBottom: 16, background: "rgba(239,68,68,0.08)", border: "1px solid #ef444433", fontSize: 12, color: "#fca5a5", fontFamily: "monospace" }}>⚠️ {error}</div>}

                {loading && (
                    <div style={{ textAlign: "center", padding: 40 }}>
                        <span style={{ display: "inline-block", width: 24, height: 24, border: "3px solid rgba(34,197,94,0.2)", borderTopColor: "#22c55e", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                        <div style={{ fontSize: 12, color: "#4b5563", marginTop: 12, fontFamily: "monospace" }}>Loading evolution data…</div>
                    </div>
                )}

                {!loading && tab === "profile" && user && (
                    <AnimatePresence>
                        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 20, padding: "24px", borderRadius: 18, marginBottom: 16, background: "rgba(34,197,94,0.04)", border: "1px solid rgba(34,197,94,0.1)" }}>
                                <div style={{ position: "relative", width: 120, height: 120, flexShrink: 0 }}>
                                    <XPRing xp={xp} level={level} color={level.color} size={120} />
                                    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                                        <span style={{ fontSize: 34 }}>{level.icon}</span>
                                        <span style={{ fontSize: 10, color: "#4b5563", fontFamily: "monospace", marginTop: 2 }}>Lv.{level.level}</span>
                                    </div>
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: 18, fontWeight: 800, color: level.color }}>{level.name}</div>
                                    <div style={{ fontSize: 13, color: "#6b7280", marginTop: 2 }}>{xp.toLocaleString()} XP total</div>
                                    {nextLvl && (
                                        <>
                                            <div style={{ marginTop: 10, height: 5, borderRadius: 3, background: "#0d1a0d", overflow: "hidden" }}>
                                                <div style={{ height: "100%", borderRadius: 3, background: level.color, width: `${xpProgress}%`, transition: "width 1s ease", boxShadow: `0 0 8px ${level.color}` }} />
                                            </div>
                                            <div style={{ fontSize: 10, color: "#4b5563", marginTop: 4, fontFamily: "monospace" }}>{xpProgress}% → {nextLvl.name} ({(nextLvl.xp_required - xp).toLocaleString()} XP left)</div>
                                        </>
                                    )}
                                </div>
                            </div>

                            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                                <StatCard icon="🪙" label="GAIA COINS" value={(user.coins_total || 0).toFixed(1)} color="#f59e0b" />
                                <StatCard icon="🌿" label="CO₂ SAVED" value={`${(user.carbon_total || 0).toFixed(1)}kg`} color="#22c55e" />
                                <StatCard icon="🔥" label="STREAK" value={`${user.streak_days || 0}d`} color="#f97316" />
                            </div>

                            <div style={{ padding: "16px", borderRadius: 14, marginBottom: 16, background: "rgba(0,255,100,0.02)", border: "1px solid rgba(0,255,100,0.06)" }}>
                                <div style={{ fontSize: 10, letterSpacing: 3, color: "#1f3a1f", marginBottom: 12, fontFamily: "monospace" }}>EVOLUTION PATH</div>
                                {LEVELS.map((l) => {
                                    const done = xp >= l.xp_required;
                                    const active = level.level === l.level;
                                    return (
                                        <div key={l.level} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8, opacity: done ? 1 : 0.35 }}>
                                            <span style={{ fontSize: 18, width: 28 }}>{l.icon}</span>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: 12, fontWeight: active ? 700 : 500, color: active ? l.color : "#4b5563" }}>
                                                    {l.name}{active && <span style={{ marginLeft: 6, fontSize: 10, color: l.color }}>← YOU</span>}
                                                </div>
                                            </div>
                                            <div style={{ fontSize: 10, color: "#374151", fontFamily: "monospace" }}>{l.xp_required.toLocaleString()} XP</div>
                                            {done && <span style={{ fontSize: 10, color: "#22c55e" }}>✓</span>}
                                        </div>
                                    );
                                })}
                            </div>

                            {profile?.recent_activities?.length > 0 && (
                                <div>
                                    <div style={{ fontSize: 10, letterSpacing: 3, color: "#1f3a1f", marginBottom: 10, fontFamily: "monospace" }}>RECENT ACTIVITY</div>
                                    {profile.recent_activities.map((a, i) => <ActivityRow key={i} act={a} />)}
                                </div>
                            )}

                            <button onClick={fetchProfile} style={{ width: "100%", marginTop: 16, padding: "12px", borderRadius: 12, border: "1px solid rgba(34,197,94,0.2)", background: "rgba(34,197,94,0.05)", color: "#22c55e", fontSize: 12, cursor: "pointer", fontFamily: "monospace" }}>↺ Refresh Data</button>
                        </motion.div>
                    </AnimatePresence>
                )}

                {!loading && tab === "leaderboard" && (
                    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                        <div style={{ fontSize: 10, letterSpacing: 3, color: "#1f3a1f", marginBottom: 12, fontFamily: "monospace" }}>GLOBAL LEADERBOARD</div>
                        {leaderboard.length === 0 ? (
                            <div style={{ textAlign: "center", padding: 32, color: "#374151", fontSize: 13 }}>No heroes yet — be the first! 🌱</div>
                        ) : leaderboard.map((u, i) => {
                            const lv = getLevelForXP(u.xp || 0);
                            const medals = ["🥇", "🥈", "🥉"];
                            const isMe = u.user_id === userId;
                            return (
                                <div key={u.user_id} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", borderRadius: 12, marginBottom: 8, background: isMe ? "rgba(34,197,94,0.08)" : "rgba(0,255,100,0.02)", border: `1px solid ${isMe ? "rgba(34,197,94,0.3)" : "rgba(0,255,100,0.06)"}` }}>
                                    <span style={{ fontSize: 18, width: 28 }}>{medals[i] || `#${i + 1}`}</span>
                                    <span style={{ fontSize: 22 }}>{lv.icon}</span>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontSize: 13, fontWeight: 700, color: isMe ? "#22c55e" : "#e2e8f0" }}>{u.name} {isMe && "← You"}</div>
                                        <div style={{ fontSize: 10, color: "#4b5563" }}>{u.city || "Planet Earth"} · Lv.{u.level}</div>
                                    </div>
                                    <div style={{ textAlign: "right" }}>
                                        <div style={{ fontSize: 13, color: lv.color, fontFamily: "monospace", fontWeight: 700 }}>{(u.xp || 0).toLocaleString()} XP</div>
                                        <div style={{ fontSize: 10, color: "#6b7280" }}>{(u.carbon || 0).toFixed(1)} kg CO₂</div>
                                    </div>
                                </div>
                            );
                        })}
                    </motion.div>
                )}

                <div style={{ marginTop: 36, textAlign: "center", fontSize: 10, color: "#1a2e1a", fontFamily: "monospace", letterSpacing: 2 }}>
                    EVOLUTION · XP · NFTs · GAIA COINS · POLYGON
                </div>
            </div>
        </div>
    );
}