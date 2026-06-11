'use client'
import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://sadafmashori-gaiavolt.hf.space'

export default function AuthPage() {
    const router = useRouter()
    const [mode, setMode] = useState("login") // login | signup | genesis
    const [form, setForm] = useState({ name: "", email: "", password: "", city: "", country: "", age: "", commitment: "" })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")
    const [genesisStep, setGenesisStep] = useState(0)
    const [particles, setParticles] = useState([])
    const canvasRef = useRef(null)

    // Particle effect
    useEffect(() => {
        const pts = Array.from({ length: 40 }, (_, i) => ({
            id: i,
            x: Math.random() * 100,
            y: Math.random() * 100,
            size: Math.random() * 2 + 0.5,
            speed: Math.random() * 0.3 + 0.1,
            opacity: Math.random() * 0.5 + 0.2
        }))
        setParticles(pts)
    }, [])

    const genesisMessages = [
        { icon: "🌍", title: "Welcome to GaiaVolt", msg: "The world's first AI + Blockchain planetary impact verifier." },
        { icon: "🔒", title: "Your Data is Sacred", msg: "Zero-Knowledge proofs protect your identity. We verify actions, not spy on people." },
        { icon: "⛓️", title: "Every Action is Permanent", msg: "Your eco-actions are minted on Polygon blockchain — immutable proof of your impact forever." },
        { icon: "🌱", title: "You are now a Planet Guardian", msg: "Your first verified action will cool a 1mm patch of the Arctic. Let's begin." }
    ]

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            const endpoint = mode === "signup" ? "/auth/signup" : "/auth/login"
            const body = mode === "signup"
                ? { name: form.name, email: form.email, password: form.password, city: form.city }
                : { email: form.email, password: form.password }

            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
                // credentials: "include"
            })

            const data = await res.json()

            if (!res.ok) {
                setError(data.error || "Something went wrong")
                setLoading(false)
                return
            }

            // Save token
            localStorage.setItem("gv_token", data.token)
            localStorage.setItem("gv_user", JSON.stringify(data.user))

            if (mode === "signup") {
                setMode("genesis")
                setGenesisStep(0)
            } else {
                router.push("/")
            }
        } catch (err) {
            setError("Cannot connect to server")
        }
        setLoading(false)
    }

    const nextGenesis = () => {
        if (genesisStep < genesisMessages.length - 1) {
            setGenesisStep(s => s + 1)
        } else {
            router.push("/")
        }
    }

    // Genesis onboarding screen
    if (mode === "genesis") {
        const step = genesisMessages[genesisStep]
        return (
            <div style={{
                minHeight: "100vh",
                background: "#000",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: "'Courier New', monospace",
                position: "relative",
                overflow: "hidden"
            }}>
                {particles.map(p => (
                    <div key={p.id} style={{
                        position: "absolute",
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: `${p.size}px`,
                        height: `${p.size}px`,
                        borderRadius: "50%",
                        background: "#00ff88",
                        opacity: p.opacity,
                        animation: `float ${3 + p.speed * 10}s ease-in-out infinite`,
                        animationDelay: `${p.id * 0.1}s`
                    }} />
                ))}

                <style>{`
          @keyframes float { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-15px); } }
          @keyframes fadeIn { from { opacity:0; transform: translateY(20px); } to { opacity:1; transform: translateY(0); } }
          @keyframes pulse { 0%,100% { box-shadow: 0 0 20px #00ff88; } 50% { box-shadow: 0 0 40px #00ff88, 0 0 80px #00ff8855; } }
        `}</style>

                <div style={{
                    textAlign: "center",
                    padding: "2rem",
                    maxWidth: "480px",
                    animation: "fadeIn 0.8s ease",
                    key: genesisStep
                }}>
                    <div style={{ fontSize: "80px", marginBottom: "1.5rem" }}>{step.icon}</div>
                    <h1 style={{
                        color: "#00ff88",
                        fontSize: "24px",
                        fontWeight: "bold",
                        marginBottom: "1rem",
                        textTransform: "uppercase",
                        letterSpacing: "3px"
                    }}>{step.title}</h1>
                    <p style={{
                        color: "rgba(255,255,255,0.8)",
                        fontSize: "16px",
                        lineHeight: "1.8",
                        marginBottom: "2.5rem"
                    }}>{step.msg}</p>

                    <div style={{ display: "flex", justifyContent: "center", gap: "8px", marginBottom: "2rem" }}>
                        {genesisMessages.map((_, i) => (
                            <div key={i} style={{
                                width: i === genesisStep ? "24px" : "8px",
                                height: "8px",
                                borderRadius: "4px",
                                background: i === genesisStep ? "#00ff88" : "rgba(0,255,136,0.3)",
                                transition: "all 0.3s ease"
                            }} />
                        ))}
                    </div>

                    <button
                        onClick={nextGenesis}
                        style={{
                            background: "transparent",
                            border: "1px solid #00ff88",
                            color: "#00ff88",
                            padding: "14px 40px",
                            fontSize: "14px",
                            letterSpacing: "2px",
                            cursor: "pointer",
                            textTransform: "uppercase",
                            borderRadius: "4px",
                            transition: "all 0.3s ease",
                            animation: "pulse 2s infinite"
                        }}
                    >
                        {genesisStep < genesisMessages.length - 1 ? "Continue →" : "Begin My Mission 🌱"}
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div style={{
            minHeight: "100vh",
            background: "linear-gradient(135deg, #000 0%, #0a0a0a 50%, #001a0d 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "'Courier New', monospace",
            padding: "1rem",
            position: "relative",
            overflow: "hidden"
        }}>
            <style>{`
        @keyframes glow { 0%,100% { text-shadow: 0 0 10px #00ff88; } 50% { text-shadow: 0 0 20px #00ff88, 0 0 40px #00ff8844; } }
        @keyframes scanline { 0% { top: -10%; } 100% { top: 110%; } }
        input::placeholder { color: rgba(0,255,136,0.3); }
        input:focus { outline: none; border-color: #00ff88 !important; box-shadow: 0 0 10px rgba(0,255,136,0.2); }
        .gv-btn:hover { background: rgba(0,255,136,0.15) !important; transform: translateY(-1px); }
        .gv-btn:active { transform: translateY(0); }
        .toggle-btn:hover { color: #00ff88 !important; }
      `}</style>

            {/* Scanline effect */}
            <div style={{
                position: "fixed", left: 0, right: 0, height: "3px",
                background: "linear-gradient(transparent, rgba(0,255,136,0.1), transparent)",
                animation: "scanline 4s linear infinite", pointerEvents: "none", zIndex: 0
            }} />

            {/* Grid background */}
            <div style={{
                position: "fixed", inset: 0,
                backgroundImage: "linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px)",
                backgroundSize: "40px 40px", pointerEvents: "none"
            }} />

            <div style={{
                width: "100%", maxWidth: "420px",
                background: "rgba(0,0,0,0.85)",
                border: "1px solid rgba(0,255,136,0.3)",
                borderRadius: "8px",
                padding: "2.5rem",
                position: "relative",
                zIndex: 1,
                backdropFilter: "blur(10px)"
            }}>
                {/* Logo */}
                <div style={{ textAlign: "center", marginBottom: "2rem" }}>
                    <div style={{ fontSize: "40px", marginBottom: "8px" }}>🌍</div>
                    <h1 style={{
                        color: "#00ff88",
                        fontSize: "22px",
                        fontWeight: "bold",
                        letterSpacing: "4px",
                        textTransform: "uppercase",
                        animation: "glow 3s infinite",
                        margin: "0 0 6px"
                    }}>GaiaVolt</h1>
                    <p style={{ color: "rgba(0,255,136,0.5)", fontSize: "11px", letterSpacing: "2px", margin: 0 }}>
                        PROOF OF PLANET PROTOCOL
                    </p>
                </div>

                {/* Mode toggle */}
                <div style={{
                    display: "flex", gap: "0",
                    background: "rgba(0,255,136,0.05)",
                    border: "1px solid rgba(0,255,136,0.15)",
                    borderRadius: "6px",
                    marginBottom: "2rem",
                    overflow: "hidden"
                }}>
                    {["login", "signup"].map(m => (
                        <button key={m} onClick={() => { setMode(m); setError("") }} style={{
                            flex: 1, padding: "10px",
                            background: mode === m ? "rgba(0,255,136,0.15)" : "transparent",
                            border: "none",
                            color: mode === m ? "#00ff88" : "rgba(0,255,136,0.4)",
                            fontSize: "12px", letterSpacing: "2px",
                            textTransform: "uppercase", cursor: "pointer",
                            borderRight: m === "login" ? "1px solid rgba(0,255,136,0.15)" : "none",
                            transition: "all 0.2s ease", fontFamily: "inherit"
                        }}>
                            {m === "login" ? "Login" : "Sign Up"}
                        </button>
                    ))}
                </div>

                <form onSubmit={handleSubmit}>
                    {mode === "signup" && (
                        <div style={{ marginBottom: "1rem" }}>
                            <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>
                                YOUR NAME
                            </label>
                            <input
                                type="text" required placeholder="Planet Guardian"
                                value={form.name}
                                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                                style={{
                                    width: "100%", padding: "12px", boxSizing: "border-box",
                                    background: "rgba(0,255,136,0.05)",
                                    border: "1px solid rgba(0,255,136,0.2)",
                                    borderRadius: "4px", color: "#00ff88",
                                    fontSize: "14px", fontFamily: "inherit"
                                }}
                            />
                        </div>
                    )}

                    <div style={{ marginBottom: "1rem" }}>
                        <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>
                            EMAIL
                        </label>
                        <input
                            type="email" required placeholder="guardian@planet.earth"
                            value={form.email}
                            onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                            style={{
                                width: "100%", padding: "12px", boxSizing: "border-box",
                                background: "rgba(0,255,136,0.05)",
                                border: "1px solid rgba(0,255,136,0.2)",
                                borderRadius: "4px", color: "#00ff88",
                                fontSize: "14px", fontFamily: "inherit"
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: mode === "signup" ? "1rem" : "1.5rem" }}>
                        <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>
                            PASSWORD
                        </label>
                        <input
                            type="password" required placeholder="••••••••"
                            value={form.password}
                            onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                            style={{
                                width: "100%", padding: "12px", boxSizing: "border-box",
                                background: "rgba(0,255,136,0.05)",
                                border: "1px solid rgba(0,255,136,0.2)",
                                borderRadius: "4px", color: "#00ff88",
                                fontSize: "14px", fontFamily: "inherit"
                            }}
                        />
                    </div>

                    {mode === "signup" && (
                        <>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "1rem" }}>
                                <div>
                                    <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>CITY *</label>
                                    <input type="text" required placeholder="Karachi"
                                        value={form.city} onChange={e => setForm(f => ({ ...f, city: e.target.value }))}
                                        style={{ width: "100%", padding: "12px", boxSizing: "border-box", background: "rgba(0,255,136,0.05)", border: "1px solid rgba(0,255,136,0.2)", borderRadius: "4px", color: "#00ff88", fontSize: "14px", fontFamily: "inherit" }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>AGE *</label>
                                    <input type="number" required placeholder="25" min="13" max="120"
                                        value={form.age} onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                                        style={{ width: "100%", padding: "12px", boxSizing: "border-box", background: "rgba(0,255,136,0.05)", border: "1px solid rgba(0,255,136,0.2)", borderRadius: "4px", color: "#00ff88", fontSize: "14px", fontFamily: "inherit" }}
                                    />
                                </div>
                            </div>
                            <div style={{ marginBottom: "1rem" }}>
                                <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>COUNTRY *</label>
                                <select required value={form.country} onChange={e => setForm(f => ({ ...f, country: e.target.value }))}
                                    style={{ width: "100%", padding: "12px", background: "rgba(0,255,136,0.05)", border: "1px solid rgba(0,255,136,0.2)", borderRadius: "4px", color: form.country ? "#00ff88" : "rgba(0,255,136,0.3)", fontSize: "14px", fontFamily: "inherit" }}>
                                    <option value="">Select your country</option>
                                    <option>Pakistan</option><option>India</option><option>Bangladesh</option>
                                    <option>United States</option><option>United Kingdom</option><option>Canada</option>
                                    <option>Australia</option><option>Germany</option><option>France</option>
                                    <option>UAE</option><option>Saudi Arabia</option><option>Turkey</option>
                                    <option>Indonesia</option><option>Nigeria</option><option>Brazil</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div style={{ marginBottom: "1.5rem" }}>
                                <label style={{ display: "block", color: "rgba(0,255,136,0.6)", fontSize: "11px", letterSpacing: "1px", marginBottom: "6px" }}>MY COMMITMENT TO THE PLANET *</label>
                                <select required value={form.commitment} onChange={e => setForm(f => ({ ...f, commitment: e.target.value }))}
                                    style={{ width: "100%", padding: "12px", background: "rgba(0,255,136,0.05)", border: "1px solid rgba(0,255,136,0.2)", borderRadius: "4px", color: form.commitment ? "#00ff88" : "rgba(0,255,136,0.3)", fontSize: "14px", fontFamily: "inherit" }}>
                                    <option value="">I commit to...</option>
                                    <option value="plant_trees">🌱 Plant at least 10 trees this year</option>
                                    <option value="reduce_plastic">♻️ Reduce plastic use by 50%</option>
                                    <option value="cycle_commute">🚲 Cycle to work/school weekly</option>
                                    <option value="solar_home">☀️ Switch to solar energy at home</option>
                                    <option value="zero_waste">🌿 Achieve zero waste lifestyle</option>
                                    <option value="carbon_neutral">⚡ Become carbon neutral by 2030</option>
                                    <option value="ocean_cleanup">🌊 Join monthly ocean/river cleanup</option>
                                    <option value="organic_food">🌾 Grow or buy organic food</option>
                                </select>
                            </div>
                        </>
                    )}

                    {error && (
                        <div style={{
                            background: "rgba(255,50,50,0.1)",
                            border: "1px solid rgba(255,50,50,0.3)",
                            borderRadius: "4px",
                            padding: "10px",
                            marginBottom: "1rem",
                            color: "#ff6666",
                            fontSize: "13px",
                            textAlign: "center"
                        }}>{error}</div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="gv-btn"
                        style={{
                            width: "100%", padding: "14px",
                            background: loading ? "rgba(0,255,136,0.1)" : "rgba(0,255,136,0.12)",
                            border: "1px solid #00ff88",
                            borderRadius: "4px",
                            color: "#00ff88",
                            fontSize: "13px", letterSpacing: "3px",
                            textTransform: "uppercase",
                            cursor: loading ? "not-allowed" : "pointer",
                            fontFamily: "inherit",
                            transition: "all 0.2s ease"
                        }}
                    >
                        {loading ? "⏳ Processing..." : mode === "login" ? "⚡ Enter GaiaVolt" : "🌱 Join the Mission"}
                    </button>
                </form>

                {mode === "signup" && (
                    <p style={{
                        color: "rgba(0,255,136,0.3)",
                        fontSize: "10px",
                        textAlign: "center",
                        marginTop: "1.5rem",
                        lineHeight: "1.6"
                    }}>
                        🔒 Zero-Knowledge Privacy — Your data is encrypted & never sold.<br />
                        Your eco-actions are permanently recorded on Polygon blockchain.
                    </p>
                )}
            </div>
        </div>
    )
}