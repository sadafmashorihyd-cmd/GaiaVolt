"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

async function sha256(file) {
  const buf = await file.arrayBuffer();
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, "0")).join("");
}

// ── Get auth token from localStorage ─────────────────────────────────────────
function getAuthToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("gv_token") || null;
}

const CLASS_META = {
  solar_panels: { icon: "☀️", label: "Solar Panel", color: "#f59e0b" },
  cycling: { icon: "🚲", label: "Cycling", color: "#22c55e" },
  utility_bills: { icon: "📄", label: "Utility Bill", color: "#60a5fa" },
  ev_charging: { icon: "⚡", label: "EV Charging", color: "#a78bfa" },
  recycling: { icon: "♻️", label: "Recycling", color: "#34d399" },
  tree_planting: { icon: "🌱", label: "Tree Planting", color: "#4ade80" },
  wind_turbine: { icon: "💨", label: "Wind Turbine", color: "#67e8f9" },
  public_transit: { icon: "🚌", label: "Public Transit", color: "#fb923c" },
  composting: { icon: "🌍", label: "Composting", color: "#a3e635" },
  led_lighting: { icon: "💡", label: "LED Lighting", color: "#fde047" },
  rainwater: { icon: "💧", label: "Rainwater Harvest", color: "#38bdf8" },
  insulation: { icon: "🏠", label: "Insulation", color: "#e879f9" },
  other_eco: { icon: "🌿", label: "Eco Action", color: "#86efac" },
};

function ModuleRow({ icon, name, status }) {
  const color = { pass: "#22c55e", fail: "#ef4444", pending: "#374151" }[status];
  const label = { pass: "PASS ✓", fail: "FAIL ✗", pending: "· · ·" }[status];
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "9px 14px", borderRadius: 8, marginBottom: 5,
      background: "rgba(0,255,100,0.02)", border: "1px solid rgba(0,255,100,0.06)"
    }}>
      <span style={{ fontSize: 13, color: "#9ca3af" }}>{icon} {name}</span>
      <span style={{
        fontSize: 11, fontWeight: 700, letterSpacing: 2, color,
        fontFamily: "monospace", textShadow: status === "pass" ? `0 0 8px ${color}` : "none",
        transition: "color 0.4s"
      }}>{label}</span>
    </div>
  );
}

function ConfidenceRing({ value, color }) {
  const r = 34, c = 42, circ = 2 * Math.PI * r;
  return (
    <svg width={c * 2} height={c * 2} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={c} cy={c} r={r} fill="none" stroke="#1a2a1a" strokeWidth={5} />
      <circle cx={c} cy={c} r={r} fill="none" stroke={color} strokeWidth={5}
        strokeDasharray={`${circ * (value / 100)} ${circ}`} strokeLinecap="round"
        style={{ transition: "stroke-dasharray 1s ease", filter: `drop-shadow(0 0 6px ${color})` }} />
    </svg>
  );
}

function ResultCard({ result }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => { if (result) setTimeout(() => setVisible(true), 80); else setVisible(false); }, [result]);
  if (!result) return null;
  const ok = result.verdict === "VERIFIED";
  const meta = CLASS_META[result.class] || CLASS_META["other_eco"];
  const conf = Math.round((result.confidence || 0) * 100);
  const txHash = result?.tx_hash || null;
  return (
    <div style={{
      marginTop: 24, padding: "22px 24px", borderRadius: 18,
      border: `1px solid ${ok ? "#22c55e33" : "#ef444433"}`,
      background: ok ? "rgba(34,197,94,0.05)" : "rgba(239,68,68,0.05)",
      opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(18px)",
      transition: "all 0.55s cubic-bezier(.4,0,.2,1)"
    }}>
      {ok ? (
        <>
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
            <div style={{ fontSize: 38 }}>{meta.icon}</div>
            <div>
              <div style={{ fontSize: 10, letterSpacing: 3, color: "#4b5563", textTransform: "uppercase" }}>Detected</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: meta.color }}>{meta.label}</div>
            </div>
            <div style={{ marginLeft: "auto", textAlign: "center" }}>
              <ConfidenceRing value={conf} color={meta.color} />
              <div style={{ fontSize: 10, color: "#6b7280", marginTop: -6, fontFamily: "monospace" }}>{conf}% CONF</div>
            </div>
          </div>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            padding: "16px", borderRadius: 12, marginBottom: 14,
            background: "linear-gradient(135deg,rgba(34,197,94,0.12),rgba(74,222,128,0.05))",
            border: "1px solid rgba(34,197,94,0.2)"
          }}>
            <span style={{ fontSize: 30 }}>🪙</span>
            <span style={{
              fontSize: 34, fontWeight: 900, color: "#22c55e",
              fontFamily: "monospace", textShadow: "0 0 20px #22c55e55"
            }}>+{result.reward_coins} GAIA</span>
          </div>
          <div style={{
            display: "flex", justifyContent: "center", gap: 6,
            fontSize: 13, color: "#6ee7b7", marginBottom: 14
          }}>
            🌿 <strong style={{ color: "#a3e635" }}>{result.carbon_kg} kg</strong> CO₂ offset saved
          </div>
          <div style={{
            padding: "11px 16px", borderRadius: 10, background: "rgba(0,255,100,0.04)",
            fontSize: 12, color: "#6ee7b7", fontStyle: "italic", textAlign: "center",
            borderLeft: "3px solid #22c55e44"
          }}>
            ❄️ "Your action just cooled a 1mm patch of the Arctic."
            {txHash && (
              <div style={{ marginTop: 12, padding: "8px 12px", background: "rgba(0,255,136,0.05)", border: "1px solid rgba(0,255,136,0.2)", borderRadius: 6 }}>
                <div style={{ fontSize: 10, color: "rgba(0,255,136,0.5)", marginBottom: 4, letterSpacing: 2 }}>BLOCKCHAIN PROOF</div>
                <a href={`https://amoy.polygonscan.com/tx/${txHash}`} target="_blank" rel="noreferrer"
                  style={{ fontSize: 11, color: "#00ff88", wordBreak: "break-all", textDecoration: "none" }}>
                  🔗 {txHash.slice(0, 20)}...{txHash.slice(-8)}
                </a>
              </div>
            )}
          </div>
        </>
      ) : (
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 40, marginBottom: 10 }}>🚨</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: "#ef4444", marginBottom: 8 }}>FRAUD DETECTED</div>
          <div style={{ fontSize: 13, color: "#fca5a5" }}>{result.fraud_reason || "Validation failed."}</div>
        </div>
      )}
    </div>
  );
}

export default function VerifyPage() {
  const [mode, setMode] = useState("photo"); // "photo" | "video"
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [phase, setPhase] = useState("idle");
  const [modules, setModules] = useState({ spatial: "pending", liveness: "pending", ai: "pending", ocr: "pending", zk: "pending" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [gps, setGps] = useState(null);
  const [gpsStatus, setGpsStatus] = useState("idle"); // idle|getting|got|denied
  const [recording, setRecording] = useState(false);
  const [videoBlob, setVideoBlob] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [recordSeconds, setRecordSeconds] = useState(0);

  const inputRef = useRef();
  const activityRef = useRef(null);
  const videoRef = useRef();
  const mediaRecRef = useRef();
  const streamRef = useRef();
  const timerRef = useRef();

  const reset = () => {
    setPhase("idle"); setResult(null); setError(null);
    setModules({ spatial: "pending", liveness: "pending", ai: "pending", ocr: "pending", zk: "pending" });
  };

  // ── GPS ───────────────────────────────────────────────────────────────────
  const gpsTrackRef = useRef([]);

  const haversine = (lat1, lon1, lat2, lon2) => {
    const R = 6371000, dLat = (lat2 - lat1) * Math.PI / 180, dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.asin(Math.sqrt(a));
  };

  const getGPS = useCallback(() => {
    setGpsStatus("getting");
    if (!navigator.geolocation) { setGpsStatus("denied"); return; }

    // Watch position — track distance
    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude: lat, longitude: lon, speed } = pos.coords;
        const track = gpsTrackRef.current;
        let distance_m = 0;

        if (track.length > 0) {
          distance_m = track.reduce((acc, p, i) => {
            if (i === 0) return 0;
            return acc + haversine(track[i - 1].lat, track[i - 1].lon, p.lat, p.lon);
          }, 0);
        }

        track.push({ lat, lon });
        setGps({ lat, lon, speed_kmh: (speed || 0) * 3.6, distance_m });
        setGpsStatus("got");
      },
      () => setGpsStatus("denied"),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  useEffect(() => { getGPS(); }, []);

  // ── Video recording ───────────────────────────────────────────────────────
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      videoRef.current.play();

      const chunks = [];
      const rec = new MediaRecorder(stream, { mimeType: "video/webm" });
      mediaRecRef.current = rec;

      rec.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
      rec.onstop = () => {
        const blob = new Blob(chunks, { type: "video/webm" });
        setVideoBlob(blob);
        setVideoUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach(t => t.stop());
        videoRef.current.srcObject = null;
      };

      rec.start();
      setRecording(true);
      setRecordSeconds(0);
      timerRef.current = setInterval(() => setRecordSeconds(s => s + 1), 1000);
    } catch (e) {
      setError("Camera access denied — allow camera permission.");
    }
  };

  const stopRecording = () => {
    mediaRecRef.current?.stop();
    setRecording(false);
    clearInterval(timerRef.current);
  };

  // ── File upload ───────────────────────────────────────────────────────────
  const handleFile = useCallback((f) => {
    if (!f) return;
    reset(); setFile(f);
    const reader = new FileReader();
    reader.onload = e => setPreview(e.target.result);
    reader.readAsDataURL(f);
  }, []);

  // ── Animate modules ───────────────────────────────────────────────────────
  const animateModules = async (mods) => {
    for (const key of ["spatial", "liveness", "ai", "ocr", "zk"]) {
      await new Promise(r => setTimeout(r, 400));
      setModules(prev => ({ ...prev, [key]: mods[key] || "pass" }));
    }
  };

  // ── Main verify ───────────────────────────────────────────────────────────
  const runVerify = async () => {
    const uploadFile = mode === "video" ? videoBlob : file;
    if (!uploadFile || ["hashing", "uploading", "verifying"].includes(phase)) return;

    reset();
    setError(null);

    try {
      setPhase("hashing");
      const hash = await sha256(uploadFile);

      setPhase("uploading");
      const selectedActivity = activityRef.current?.value || "plantation";

      // Fix: Client-side size validation
      const maxSize = mode === "video" ? 20 * 1024 * 1024 : 10 * 1024 * 1024;
      if (uploadFile.size > maxSize) {
        setError(`File too large — max ${mode === "video" ? "20MB" : "10MB"}. ${mode === "video" ? "Record shorter video." : "Compress image."}`);
        setPhase("error");
        return;
      }

      const fd = new FormData();

      if (mode === "video") {
        fd.append("video", uploadFile, "activity.webm");
        fd.append("activity", selectedActivity);
      } else {
        fd.append("image", uploadFile);
        fd.append("proof_type", selectedActivity);
      }

      fd.append("sha256", hash);
      fd.append("mode", mode);

      if (gps) {
        fd.append("lat", gps.lat.toString());
        fd.append("lon", gps.lon.toString());
        fd.append("speed_kmh", gps.speed_kmh.toString());
      }

      const endpoint = mode === "video" ? "/verify-video" : "/upload-ecox";
      const flaskBase = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        ? 'http://127.0.0.1:8000'
        : `http://${window.location.hostname}:8000`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 min timeout
      const token = getAuthToken();
      const res = await fetch(`${flaskBase}${endpoint}`, {
        method: "POST",
        body: fd,
        signal: controller.signal,
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      clearTimeout(timeoutId);
      const data = await res.json();

      setPhase("verifying");
      await animateModules(data.modules || { spatial: "pass", liveness: "pass", ai: "pass", ocr: "pass", zk: "pass" });

      if (data.verdict === "VERIFIED") {
        setResult({ verdict: "VERIFIED", ...data });
        setPhase("done");
      } else {
        setResult({ verdict: "FRAUD", fraud_reason: data.fraud_reason || data.error || "Validation failed." });
        setPhase("fraud");
      }
    } catch (err) {
      setError("Cannot connect to Flask. Run: python app.py");
      setPhase("error");
    }
  };

  const busy = ["hashing", "uploading", "verifying"].includes(phase);
  const canVerify = mode === "video" ? (videoBlob && !busy) : (file && !busy);

  const phaseText = {
    idle: "Ready", hashing: "Fingerprinting…", uploading: "Sending to AI…",
    verifying: "Verifying…", done: "Done ✓", fraud: "Fraud", error: "Error"
  }[phase];

  const gpsColor = { idle: "#374151", getting: "#f59e0b", got: "#22c55e", denied: "#ef4444" }[gpsStatus];
  const gpsText = { idle: "Getting GPS…", getting: "Getting GPS…", got: `GPS ✓ ${gps?.lat?.toFixed(3)},${gps?.lon?.toFixed(3)}`, denied: "GPS denied" }[gpsStatus];

  return (
    <div style={{
      minHeight: "100vh", background: "#030b03",
      backgroundImage: "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,80,20,0.35) 0%, transparent 70%)",
      fontFamily: "'Syne','Space Grotesk',sans-serif", color: "#f0fdf4", padding: "48px 20px 80px"
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono&display=swap');
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
        .drop-zone:hover{border-color:#22c55e66!important;}
        .vbtn:hover:not(:disabled){background:linear-gradient(135deg,#15803d,#16a34a)!important;transform:translateY(-1px);}
        .mode-btn.active{border-color:#22c55e!important;color:#22c55e!important;background:rgba(34,197,94,0.1)!important;}
      `}</style>

      <div style={{ maxWidth: 520, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 11, letterSpacing: 4, color: "#22c55e66", textTransform: "uppercase", marginBottom: 8, fontFamily: "monospace" }}>
            GaiaVolt · Proof of Planet · Day 24
          </div>
          <h1 style={{
            margin: 0, fontSize: "clamp(26px,6vw,40px)", fontWeight: 800,
            background: "linear-gradient(135deg,#86efac,#22c55e,#4ade80)",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
          }}>
            Upload & Verify
          </h1>

          {/* GPS status */}
          <div style={{
            marginTop: 10, display: "inline-flex", alignItems: "center", gap: 6,
            padding: "5px 14px", borderRadius: 20, background: "rgba(0,0,0,0.3)",
            border: `1px solid ${gpsColor}44`, fontSize: 11, color: gpsColor, fontFamily: "monospace"
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: "50%", background: gpsColor,
              animation: gpsStatus === "getting" ? "pulse 1s infinite" : "none", display: "inline-block"
            }} />
            {gpsText}
            {gpsStatus === "denied" && (
              <button onClick={getGPS} style={{ marginLeft: 6, color: "#f59e0b", background: "none", border: "none", cursor: "pointer", fontSize: 10 }}>Retry</button>
            )}
          </div>
        </div>

        {/* Mode selector */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          {[{ id: "photo", icon: "📸", label: "Photo Proof" }, { id: "video", icon: "🎥", label: "Video Proof" }].map(m => (
            <button key={m.id} className={`mode-btn${mode === m.id ? " active" : ""}`}
              onClick={() => { setMode(m.id); reset(); setFile(null); setPreview(null); setVideoBlob(null); setVideoUrl(null); }}
              style={{
                flex: 1, padding: "12px", borderRadius: 12, cursor: "pointer",
                border: "1px solid #1a2e1a", background: "rgba(255,255,255,0.02)",
                color: "#6b7280", fontSize: 13, fontWeight: 600, transition: "all 0.2s"
              }}>
              {m.icon}<br /><span style={{ fontSize: 11 }}>{m.label}</span>
            </button>
          ))}
        </div>

        {/* Photo mode */}
        {mode === "photo" && (
          <>
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 10, letterSpacing: 3, color: "#4b5563", fontFamily: "monospace", marginBottom: 6 }}>
                SELECT ACTIVITY:
              </div>
              <select ref={activityRef} onChange={(e) => {
                const COMING_SOON_MSGS = {
                  coming_soon_led: "💡 LED Lighting coming soon! We'll verify real energy savings via smart meter data. Every watt counts! 🔋",
                  coming_soon_cycling: "🚲 Cycling coming soon! GPS-powered proof of every km you ride for the planet. 🌍",
                  coming_soon_solar: "☀️ Solar Panels coming soon! Real-time energy output verified on blockchain. ⚡",
                  coming_soon_ocean: "🌊 Ocean Cleanup coming soon! Geo-tagged proof from real cleanup sites. Every piece of trash matters! 🐋",
                  coming_soon_wind: "💨 Wind Energy coming soon! Live turbine rotation data anchored on-chain. 🌬️",
                  coming_soon_ev: "⚡ EV Charging coming soon! Smart meter proof of every clean mile driven. 🚗",
                  coming_soon_transit: "🚌 Public Transport coming soon! GPS-verified commute tracking for greener cities. 🗺️",
                  coming_soon_water: "💧 Water Conservation coming soon! Smart meter integration to reward every drop saved. 🌊",
                  coming_soon_farming: "🌾 Organic Farming coming soon! Soil sensor + GPS verification for real farmers. 🌿",
                  coming_soon_bills: "📄 Utility Bills coming soon! AI-powered bill authentication to reward energy savers. 💚",
                  recycling: "♻️ Recycling verification coming soon! We're building ultra fraud-proof bin detection. Every recycled item will be verified with AI + GPS. Stay tuned! 🌱",
                };
                if (COMING_SOON_MSGS[e.target.value]) {
                  alert(COMING_SOON_MSGS[e.target.value]);
                  e.target.value = "plantation";
                }
              }} style={{
                width: "100%", padding: "12px 14px", borderRadius: 10,
                background: "rgba(0,0,0,0.5)", border: "1px solid #22c55e33",
                color: "#e2e8f0", fontSize: 13, outline: "none", cursor: "pointer",
              }}>
                <option value="plantation">🌱 Plantation ✅</option>
                <option value="recycling">♻️ Recycling — Coming Soon</option>
                <option value="coming_soon_led">💡 LED Lighting — Coming Soon</option>
                <option value="coming_soon_cycling">🚲 Cycling — Coming Soon</option>
                <option value="coming_soon_solar">☀️ Solar Panels — Coming Soon</option>
                <option value="coming_soon_ocean">🌊 Ocean Cleanup — Coming Soon</option>
                <option value="coming_soon_wind">💨 Wind Energy — Coming Soon</option>
                <option value="coming_soon_ev">⚡ EV Charging — Coming Soon</option>
                <option value="coming_soon_transit">🚌 Public Transport — Coming Soon</option>
                <option value="coming_soon_water">💧 Water Conservation — Coming Soon</option>
                <option value="coming_soon_farming">🌾 Organic Farming — Coming Soon</option>
                <option value="coming_soon_bills">📄 Utility Bills — Coming Soon</option>
              </select>
            </div>

            <div className="drop-zone"
              onClick={() => inputRef.current?.click()}
              style={{
                position: "relative", borderRadius: 16, cursor: "pointer", overflow: "hidden",
                border: "1.5px dashed #1a2e1a", background: "rgba(0,255,100,0.015)",
                minHeight: preview ? 0 : 160,
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
              {preview ? (
                <img src={preview} alt="preview" style={{ width: "100%", display: "block", borderRadius: 15, maxHeight: 300, objectFit: "cover" }} />
              ) : (
                <div style={{ textAlign: "center", padding: 32 }}>
                  <div style={{ fontSize: 42, marginBottom: 10 }}>📸</div>
                  <div style={{ fontSize: 13, color: "#4b5563" }}>Tap to upload photo</div>
                  <div style={{ fontSize: 11, marginTop: 6, color: "#1f2937", fontFamily: "monospace" }}>Must be fresh — GPS required</div>
                </div>
              )}
              <input ref={inputRef} type="file" accept="image/*" capture="environment"
                style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
            </div>
          </>
        )}

        {/* Activity Selector — Video mode */}
        {mode === "video" && (
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 10, letterSpacing: 3, color: "#4b5563", fontFamily: "monospace", marginBottom: 6 }}>
              SELECT ACTIVITY:
            </div>
            <select ref={activityRef} onChange={(e) => {
              const COMING_SOON_MSGS = {
                recycling: "♻️ Recycling verification coming soon! We're building ultra fraud-proof bin detection. Every recycled item will be verified with AI + GPS. Stay tuned! 🌱",
                led_lighting: "💡 LED Lighting coming soon! We'll verify real energy savings via smart meter data. Every watt counts! 🔋",
                cycling: "🚲 Cycling coming soon! GPS-powered proof of every km you ride for the planet. 🌍",
                solar_panels: "☀️ Solar Panels coming soon! Real-time energy output verified on blockchain. ⚡",
                ocean_cleanup: "🌊 Ocean Cleanup coming soon! Geo-tagged proof from real cleanup sites. Every piece of trash matters! 🐋",
                wind_energy: "💨 Wind Energy coming soon! Live turbine rotation data anchored on-chain. 🌬️",
                ev_charging: "⚡ EV Charging coming soon! Smart meter proof of every clean mile driven. 🚗",
                public_transport: "🚌 Public Transport coming soon! GPS-verified commute tracking for greener cities. 🗺️",
                water_conservation: "💧 Water Conservation coming soon! Smart meter integration to reward every drop saved. 🌊",
                organic_farming: "🌾 Organic Farming coming soon! Soil sensor + GPS verification for real farmers. 🌿",
              };
              if (COMING_SOON_MSGS[e.target.value]) {
                alert(COMING_SOON_MSGS[e.target.value]);
                e.target.value = "plantation";
              }
            }} style={{
              width: "100%", padding: "12px 14px", borderRadius: 10,
              background: "rgba(0,0,0,0.5)", border: "1px solid #22c55e33",
              color: "#e2e8f0", fontSize: 13, outline: "none", cursor: "pointer",
            }}>
              <option value="plantation">🌱 Plantation ✅</option>
              <option value="recycling">♻️ Recycling — Coming Soon</option>
              <option value="led_lighting">💡 LED Lighting — Coming Soon</option>
              <option value="cycling">🚲 Cycling — Coming Soon</option>
              <option value="solar_panels">☀️ Solar Panels — Coming Soon</option>
              <option value="ocean_cleanup">🌊 Ocean Cleanup — Coming Soon</option>
              <option value="wind_energy">💨 Wind Energy — Coming Soon</option>
              <option value="ev_charging">⚡ EV Charging — Coming Soon</option>
              <option value="public_transport">🚌 Public Transport — Coming Soon</option>
              <option value="water_conservation">💧 Water Conservation — Coming Soon</option>
              <option value="organic_farming">🌾 Organic Farming — Coming Soon</option>
            </select>
          </div>
        )}

        {/* Video mode */}
        {mode === "video" && (
          <div style={{ borderRadius: 16, overflow: "hidden", background: "#000", border: "1.5px solid #1a2e1a" }}>
            {!videoUrl ? (
              <>
                <video ref={videoRef} style={{ width: "100%", maxHeight: 280, display: "block", background: "#000" }} muted playsInline />
                <div style={{ padding: 16, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  {recording ? (
                    <>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#ef4444", fontFamily: "monospace" }}>
                        <span style={{ width: 10, height: 10, borderRadius: "50%", background: "#ef4444", animation: "pulse 1s infinite", display: "inline-block" }} />
                        REC {recordSeconds}s
                      </div>
                      <button onClick={stopRecording} style={{
                        padding: "10px 20px", borderRadius: 10, border: "none",
                        background: "#ef4444", color: "#fff", fontWeight: 700, cursor: "pointer", fontSize: 13
                      }}>
                        ⏹ Stop
                      </button>
                    </>
                  ) : (
                    <button onClick={startRecording} style={{
                      width: "100%", padding: "12px", borderRadius: 10, border: "none",
                      background: "linear-gradient(135deg,#16a34a,#22c55e)", color: "#fff", fontWeight: 700, cursor: "pointer", fontSize: 14
                    }}>
                      🎥 Start Recording (min 5 sec)
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div style={{ padding: 16 }}>
                <video src={videoUrl} controls style={{ width: "100%", borderRadius: 10, maxHeight: 280 }} />
                <button onClick={() => { setVideoBlob(null); setVideoUrl(null); reset(); }}
                  style={{
                    width: "100%", marginTop: 10, padding: "10px", borderRadius: 10, border: "1px solid #1a2e1a",
                    background: "transparent", color: "#6b7280", cursor: "pointer", fontSize: 12
                  }}>
                  ↺ Record again
                </button>
              </div>
            )}
          </div>
        )}

        {/* File info */}
        {(file || videoBlob) && (
          <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", fontSize: 11, color: "#374151", fontFamily: "monospace", padding: "0 4px" }}>
            <span style={{ color: "#22c55e66" }}>▸ {mode === "video" ? `video_${recordSeconds}s.webm` : file?.name}</span>
            <span>{mode === "video" ? `${recordSeconds}s` : `${((file?.size || 0) / 1024).toFixed(1)} KB`}</span>
          </div>
        )}

        {/* Modules */}
        {(file || videoBlob) && (
          <div style={{ marginTop: 18 }}>
            <div style={{ fontSize: 10, letterSpacing: 3, color: "#1f3a1f", textTransform: "uppercase", marginBottom: 10, fontFamily: "monospace" }}>
              ▸ Consensus Engine — All must pass
            </div>
            <ModuleRow icon="🛰️" name="Spatial Metadata (GPS + Timestamp)" status={modules.spatial} />
            <ModuleRow icon="👁️" name="Liveness 2.0 (Blur / Moiré)" status={modules.liveness} />
            <ModuleRow icon="🧠" name="AI Vision — ecox_model_edge.tflite" status={modules.ai} />
            <ModuleRow icon="📝" name="Activity Proof (Video/OCR)" status={modules.ocr} />
            <ModuleRow icon="🔐" name="ZK-Proof (Off-chain)" status={modules.zk} />
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            marginTop: 14, padding: "12px 16px", borderRadius: 10,
            background: "rgba(239,68,68,0.08)", border: "1px solid #ef444433",
            fontSize: 12, color: "#fca5a5", fontFamily: "monospace"
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Verify button */}
        <motion.button
          whileHover={{ scale: canVerify ? 1.02 : 1 }}
          whileTap={{ scale: canVerify ? 0.98 : 1 }}
          className="vbtn" disabled={!canVerify} onClick={runVerify}
          style={{
            width: "100%", marginTop: 20, padding: "17px 0", borderRadius: 14, border: "none",
            cursor: canVerify ? "pointer" : "not-allowed",
            background: canVerify ? "linear-gradient(135deg,#16a34a,#22c55e)" : "rgba(255,255,255,0.04)",
            color: canVerify ? "#fff" : "#1f2937",
            fontSize: 15, fontWeight: 800, letterSpacing: 0.8, transition: "all 0.2s"
          }}>
          {busy ? (
            <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
              <span style={{
                width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff",
                borderRadius: "50%", animation: "spin 0.8s linear infinite", display: "inline-block"
              }} />
              {phaseText}
            </span>
          ) : "⚡ ⚡ Verify & Earn GaiaVolt"}
        </motion.button>

        <AnimatePresence>
          {result && <ResultCard result={result} />}
        </AnimatePresence>

        {result && (
          <button onClick={() => { setFile(null); setPreview(null); setVideoBlob(null); setVideoUrl(null); reset(); }}
            style={{
              width: "100%", marginTop: 12, padding: "12px 0", borderRadius: 12,
              border: "1px solid #1a2e1a", background: "transparent",
              color: "#374151", fontSize: 13, cursor: "pointer"
            }}
            onMouseOver={e => e.currentTarget.style.color = "#22c55e"}
            onMouseOut={e => e.currentTarget.style.color = "#374151"}>
            ↺ Upload another proof
          </button>
        )}

        <div style={{ marginTop: 36, textAlign: "center", fontSize: 10, color: "#1a2e1a", fontFamily: "monospace", letterSpacing: 2 }}>
          GPS · VIDEO PROOF · AI · ZK-SNARKS · POLYGON
        </div>
      </div>
    </div>
  );
}