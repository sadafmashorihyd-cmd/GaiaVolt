# 🌍 EcoX — Proof of Planet Protocol

> *"People built apps for social media. I built an app for the Planet."*  
> Built from **Hyderabad, Pakistan** 🇵🇰

---

## What is EcoX?

EcoX is the world's first **AI + Blockchain Carbon Rewards System** that verifies real-world environmental actions and rewards users with ECOX tokens — backed by NASA satellite data and IPCC AR6 science.

**No fake data. No middleman. No trust required.**

---

## 🚀 How It Works

```
User takes photo (solar panel / cycling / utility bill)
         ↓
🤖 AI verifies action (TFLite, 99.95% accuracy, offline)
         ↓
🛡️ Fraud detection (spoof, geo-fence, duplicate check)
         ↓
🛰️ NASA POWER API fetches real-time satellite data
         ↓
📊 IPCC AR6 calculates Lovelock Score (0-10000 BPS)
         ↓
⛓️ Blockchain mints real ECOX tokens (Polygon)
         ↓
🔒 1% goes to QuantumLock 2050 (Environmental Endowment Fund)
         ↓
🌐 Receipt stored on IPFS — immutable forever
```

---

## 🏗️ Project Structure

```
EcoX/
│
├── 🧠 PHASE 1 — AI Vision Engine (Day 1-7)
│   ├── edge_predictor.py          # TFLite offline AI model
│   ├── gradcam_engine.py          # Grad-CAM heatmap visualization
│   ├── ecox_model_edge.tflite     # 5MB edge model (offline capable)
│   ├── src/models/                # Training, pruning, quantization
│   └── src/training/              # Augmentation & trainer engine
│
├── 🛡️ PHASE 2 — Security & Anti-Cheat (Day 8-14)
│   ├── anti_cheat.py              # Main fraud detection
│   ├── geo_fence.py               # 10km geo-fence check
│   ├── spatial_shield.py          # ZK-SNARK spatial proof
│   ├── image_fingerprint.py       # SHA-256 + pHash duplicate check
│   ├── encryption_engine.py       # AES-256 encryption
│   └── exploit_simulation.py      # Attack simulation tests
│
├── ⛓️ PHASE 3 — Blockchain (Day 15-22)
│   ├── ecox-contracts/
│   │   ├── contracts/
│   │   │   ├── EcoCoin.sol        # ECOX token (ERC-20, deflationary)
│   │   │   ├── QuantumLock2050.sol # Time-locked 2050 fund
│   │   │   └── EcoXPaymaster.sol  # ERC-4337 gasless transactions
│   │   └── ignition/modules/      # Deploy scripts
│   ├── day21_impact_engine.py     # Scientific CO2 + Lovelock calculation
│   ├── day21_web3_bridge.py       # Python + Blockchain bridge
│   ├── day21_orchestrator.py      # Master dual-track engine
│   ├── day22_paymaster.py         # ERC-4337 UserOperation builder
│   └── day23_pipeline.py          # Full real pipeline (no hardcoding)
│
├── 🎮 PHASE 4 — Frontend (Day 23-28)
│   └── frontend/                  # Next.js + Three.js + Framer Motion
│       └── app/page.tsx           # 3D Hyper-Globe with green lasers
│
└── 🚀 PHASE 5 — Launch (Day 32-35)
    ├── predict_ecox.py            # Main prediction + reward flow
    ├── app.py                     # Flask API server
    └── receipt_monitor.py         # Background receipt monitor
```

---

## ⛓️ Live Contracts (Polygon Amoy Testnet)

| Contract | Address | Description |
|----------|---------|-------------|
| **EcoCoin (ECOX)** | `0xc26A215ada91C7A51001a2c11B5348D532B28c93` | Deflationary ERC-20 token |
| **QuantumLock 2050** | `0xc0d5a8E04706674b5aA2e366122Ae8d54C56c7c1` | Unlocks Jan 1, 2050 |
| **EcoXPaymaster** | `0xBC8dc092c43D6795A27Cc4DbF1Abb6C55BFE5477` | Gasless transactions |
| **EntryPoint v0.6** | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` | ERC-4337 standard |

---

## 🔬 Scientific Foundation

| Component | Source | Detail |
|-----------|--------|--------|
| Temperature data | NASA POWER API v2.9 | Real-time satellite |
| Carbon scoring | IPCC AR6 WGI Table 5.1 | Peer-reviewed science |
| Lovelock Score | James Lovelock Gaia Theory | 0-10000 BPS |
| CO2 sequestration | IPCC regional factors | Solar: 0.95, Cycling: 0.72 |

---

## 🛡️ Security Features

- ✅ **Spoof Detection** — Moire pattern screen detection
- ✅ **Geo-Fence** — 10km radius, max 3 actions/day
- ✅ **Duplicate Check** — SHA-256 + pHash visual similarity
- ✅ **ZK-SNARKs** — Zero-knowledge spatial proofs
- ✅ **Rate Limiting** — 10 mints/day per wallet on-chain
- ✅ **Confidence Threshold** — Min 90% AI confidence required
- ✅ **Multisig Governance** — 2-of-N oracle approval
- ✅ **Replay Protection** — DuplicateActionHash on-chain

---

## 🔒 QuantumLock 2050 — The Legacy

> *"The world's first Environmental Endowment Fund on blockchain"*

- Every EcoX transaction sends **1% to QuantumLock**
- Fund is **locked until January 1, 2050** (blockchain enforced)
- The user with most **Proof of Planet** score unlocks it
- **No one** — not even the owner — can break the time lock

---

## 🧠 AI Model Performance

| Metric | Value |
|--------|-------|
| Model size | 5.07 MB (TFLite) |
| Classes | 13 carbon actions |
| Accuracy | 99.95% |
| Mode | **Offline capable** |
| Latency | ~250ms on CPU |

---

## 🛠️ Tech Stack

```
AI/ML:        TensorFlow Lite, PyTorch, OpenCV, Grad-CAM
Blockchain:   Solidity, Hardhat, Polygon, ERC-20, ERC-4337
Privacy:      ZK-SNARKs (circom), EIP-712 signatures
Storage:      IPFS, Pinata, AES-256 encryption
Science:      NASA POWER API, IPCC AR6
Backend:      Python, Web3.py, Flask, asyncio
Frontend:     Next.js, Three.js, Framer Motion, Tailwind
```

---

## 🌍 Vision

> *"Your action just cooled a 2,026,218 mm² patch of the Arctic."*

EcoX proves that every individual action matters — and records it permanently on the blockchain for the world to verify.

**Built for 2026. Locked until 2050. For the Planet.**

---

*Made with love from Hyderabad, Pakistan*