"""
GaiaVolt — Plantation Tracker
Stage System + QR Code
Stage 1: Planting → 30% reward
Stage 2: 1 month growth proof → 40% reward  
Stage 3: 3 months growth → 30% reward
QR tag system for plant identity verification
"""
import sqlite3
import hashlib
import json
import qrcode
import os
import math
from datetime import datetime, timezone, timedelta
from io import BytesIO
import base64

STAGE_REWARDS = {
    1: {"pct": 0.30, "label": "Planted",      "days_next": 30,  "icon": "🌱"},
    2: {"pct": 0.40, "label": "Growing",       "days_next": 60,  "icon": "🌿"},
    3: {"pct": 0.30, "label": "Established",   "days_next": None,"icon": "🌳"},
}

class PlantationTracker:

    def __init__(self):
        self.db = sqlite3.connect("plantation.db", check_same_thread=False)
        self._init_db()
        print("✅ Plantation Tracker ready!")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS plants (
                plant_id     TEXT PRIMARY KEY,
                user_id      TEXT NOT NULL,
                qr_code      TEXT UNIQUE NOT NULL,
                lat          REAL,
                lon          REAL,
                stage        INTEGER DEFAULT 1,
                coins_stage1 REAL DEFAULT 0,
                coins_stage2 REAL DEFAULT 0,
                coins_stage3 REAL DEFAULT 0,
                planted_at   TEXT NOT NULL,
                stage2_at    TEXT,
                stage3_at    TEXT,
                stage2_due   TEXT,
                stage3_due   TEXT,
                status       TEXT DEFAULT 'active',
                cancelled    INTEGER DEFAULT 0
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS stage_proofs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id     TEXT NOT NULL,
                stage        INTEGER NOT NULL,
                video_hash   TEXT,
                gps_match    INTEGER DEFAULT 0,
                qr_scanned   INTEGER DEFAULT 0,
                verified_at  TEXT NOT NULL,
                reward_coins REAL DEFAULT 0
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_plants ON plants(user_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_qr ON plants(qr_code)")
        self.db.commit()

    def generate_qr_code(self, plant_id, user_id, lat, lon):
        """
        Unique QR generate karo har plant ke liye
        QR mein: plant_id + GPS + timestamp encrypted
        """
        qr_data = {
            "plant_id": plant_id,
            "user_id":  hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "lat":      round(lat, 4) if lat else None,
            "lon":      round(lon, 4) if lon else None,
            "issued":   datetime.now(timezone.utc).isoformat(),
            "app":      "GaiaVolt"
        }
        qr_string = json.dumps(qr_data, separators=(',',':'))
        qr_hash   = hashlib.sha256(qr_string.encode()).hexdigest()[:12].upper()
        qr_code   = f"GAIA-PLANT-{qr_hash}"

        # Generate QR image
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10, border=4
            )
            qr.add_data(qr_code)
            qr.make(fit=True)
            img    = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_b64 = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"QR image error: {e}")
            qr_b64 = None

        return qr_code, qr_b64

    def register_plant(self, user_id, lat, lon, base_coins):
        """Stage 1 — Planting registered"""
        plant_id = "PLT-" + hashlib.sha256(
            f"{user_id}{lat}{lon}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()

        qr_code, qr_image = self.generate_qr_code(plant_id, user_id, lat, lon)

        now        = datetime.now(timezone.utc)
        stage2_due = (now + timedelta(days=30)).isoformat()
        stage3_due = (now + timedelta(days=90)).isoformat()

        coins_s1 = round(base_coins * STAGE_REWARDS[1]["pct"], 2)

        self.db.execute("""
            INSERT INTO plants
            (plant_id, user_id, qr_code, lat, lon, stage,
             coins_stage1, planted_at, stage2_due, stage3_due)
            VALUES (?,?,?,?,?,1,?,?,?,?)
        """, (plant_id, user_id, qr_code, lat, lon,
              coins_s1, now.isoformat(), stage2_due, stage3_due))

        self.db.execute("""
            INSERT INTO stage_proofs
            (plant_id, stage, gps_match, qr_scanned, verified_at, reward_coins)
            VALUES (?,1,1,0,?,?)
        """, (plant_id, now.isoformat(), coins_s1))

        self.db.commit()

        return {
            "plant_id":    plant_id,
            "qr_code":     qr_code,
            "qr_image":    qr_image,
            "stage":       1,
            "coins_now":   coins_s1,
            "coins_total": base_coins,
            "stage2_due":  stage2_due,
            "stage3_due":  stage3_due,
            "message":     f"🌱 Stage 1 complete! {coins_s1} ECO earned. Come back in 30 days with growth proof!"
        }

    def verify_qr_scan(self, qr_code, user_id, lat, lon):
        """QR code scan verify karo — location match hona chahiye"""
        plant = self.db.execute(
            "SELECT * FROM plants WHERE qr_code=? AND user_id=?",
            (qr_code, user_id)
        ).fetchone()

        if not plant:
            return {"valid": False, "reason": "QR code not found or not your plant!"}

        cols = ["plant_id","user_id","qr_code","lat","lon","stage",
                "coins_stage1","coins_stage2","coins_stage3",
                "planted_at","stage2_at","stage3_at",
                "stage2_due","stage3_due","status","cancelled"]
        p = dict(zip(cols, plant))

        if p["cancelled"]:
            return {"valid": False, "reason": "This plant was cancelled due to no growth proof!"}

        # GPS match check — within 30 meters
        if p["lat"] and p["lon"] and lat and lon:
            dlat = math.radians(lat - p["lat"])
            dlon = math.radians(lon - p["lon"])
            a    = (math.sin(dlat/2)**2 +
                    math.cos(math.radians(lat)) *
                    math.cos(math.radians(p["lat"])) *
                    math.sin(dlon/2)**2)
            dist = 6371000 * 2 * math.asin(math.sqrt(a))

            if dist > 30:
                return {
                    "valid":  False,
                    "reason": f"Wrong location! You are {dist:.0f}m away from your plant. Must be within 30m."
                }

        return {
            "valid":    True,
            "plant_id": p["plant_id"],
            "stage":    p["stage"],
            "plant":    p
        }

    def submit_stage_proof(self, plant_id, user_id, stage, lat, lon, video_hash, qr_scanned, base_coins):
        """Stage 2 ya 3 ka proof submit karo"""
        plant = self.db.execute(
            "SELECT * FROM plants WHERE plant_id=? AND user_id=?",
            (plant_id, user_id)
        ).fetchone()

        if not plant:
            return {"passed": False, "reason": "Plant not found!"}

        cols = ["plant_id","user_id","qr_code","lat","lon","stage",
                "coins_stage1","coins_stage2","coins_stage3",
                "planted_at","stage2_at","stage3_at",
                "stage2_due","stage3_due","status","cancelled"]
        p = dict(zip(cols, plant))

        # Stage check
        if p["stage"] >= stage:
            return {"passed": False, "reason": f"Stage {stage} already completed!"}

        if p["stage"] + 1 != stage:
            return {"passed": False, "reason": f"Complete Stage {p['stage']+1} first!"}

        # QR scan required for stage 2+
        if not qr_scanned:
            return {"passed": False, "reason": "QR code scan required! Scan the QR tag on your plant."}

        # Time check
        now = datetime.now(timezone.utc)
        due_field = f"stage{stage}_due"
        if p.get(due_field):
            due = datetime.fromisoformat(p[due_field])
            if now < due - timedelta(days=5):  # 5 days grace
                days_left = (due - now).days
                return {"passed": False, "reason": f"Too early! Come back in {days_left} days for Stage {stage} verification."}

        # GPS match
        if lat and lon and p["lat"] and p["lon"]:
            dlat = math.radians(lat - p["lat"])
            dlon = math.radians(lon - p["lon"])
            a    = (math.sin(dlat/2)**2 +
                    math.cos(math.radians(lat)) *
                    math.cos(math.radians(p["lat"])) *
                    math.sin(dlon/2)**2)
            dist = 6371000 * 2 * math.asin(math.sqrt(a))
            if dist > 30:
                return {"passed": False, "reason": f"Wrong location! {dist:.0f}m from your plant. Must be within 30m."}

        # Calculate reward
        coins = round(base_coins * STAGE_REWARDS[stage]["pct"], 2)

        # Update plant
        stage_col = f"coins_stage{stage}"
        time_col  = f"stage{stage}_at"
        self.db.execute(f"""
            UPDATE plants SET stage=?, {stage_col}=?, {time_col}=?
            WHERE plant_id=?
        """, (stage, coins, now.isoformat(), plant_id))

        self.db.execute("""
            INSERT INTO stage_proofs
            (plant_id, stage, video_hash, gps_match, qr_scanned, verified_at, reward_coins)
            VALUES (?,?,?,1,?,?,?)
        """, (plant_id, stage, video_hash, 1 if qr_scanned else 0, now.isoformat(), coins))

        self.db.commit()

        msg = STAGE_REWARDS[stage]
        return {
            "passed":      True,
            "stage":       stage,
            "coins_earned":coins,
            "message":     f"{msg['icon']} Stage {stage} verified! +{coins} ECO earned!",
            "next_stage":  stage + 1 if stage < 3 else None,
        }

    def cancel_inactive_plants(self):
        """30 days baad growth proof nahi diya = cancel + reward wapas"""
        now      = datetime.now(timezone.utc).isoformat()
        expired  = self.db.execute("""
            SELECT plant_id, user_id, coins_stage1
            FROM plants
            WHERE stage=1 AND cancelled=0 AND stage2_due < ?
        """, (now,)).fetchall()

        cancelled = []
        for plant_id, user_id, coins in expired:
            self.db.execute(
                "UPDATE plants SET cancelled=1, status='cancelled' WHERE plant_id=?",
                (plant_id,)
            )
            cancelled.append({"plant_id": plant_id, "user_id": user_id, "coins": coins})

        self.db.commit()
        return cancelled

    def get_user_plants(self, user_id):
        """User ke sab plants"""
        rows = self.db.execute("""
            SELECT plant_id, qr_code, lat, lon, stage,
                   coins_stage1, coins_stage2, coins_stage3,
                   planted_at, stage2_due, stage3_due, status, cancelled
            FROM plants WHERE user_id=? ORDER BY planted_at DESC
        """, (user_id,)).fetchall()

        plants = []
        now    = datetime.now(timezone.utc)
        for r in rows:
            total_earned = (r[5] or 0) + (r[6] or 0) + (r[7] or 0)
            days_to_s2   = None
            if r[9]:
                try:
                    due = datetime.fromisoformat(r[9])
                    days_to_s2 = max(0, (due - now).days)
                except:
                    pass
            plants.append({
                "plant_id":     r[0],
                "qr_code":      r[1],
                "lat":          r[2],
                "lon":          r[3],
                "stage":        r[4],
                "coins_earned": round(total_earned, 2),
                "planted_at":   r[8],
                "stage2_due":   r[9],
                "days_to_s2":   days_to_s2,
                "status":       r[11],
                "cancelled":    r[12],
                "stage_label":  STAGE_REWARDS.get(r[4], {}).get("label","Unknown"),
            })
        return plants