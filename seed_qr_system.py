"""
GaiaVolt — Seed QR System
Har seed ka alag unique QR code
User seeds order karta hai → QR milta hai → plant karta hai → growth reward
"""
import sqlite3
import hashlib
import json
import os
import math
import secrets
import base64
from datetime import datetime, timezone, timedelta
from io import BytesIO

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except:
    QR_AVAILABLE = False
    print("⚠️ Install: pip install qrcode[pil]")


class SeedQRSystem:

    def __init__(self):
        self.db = sqlite3.connect("seeds.db", check_same_thread=False)
        self._init_db()
        print("✅ Seed QR System ready!")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS seed_orders (
                order_id     TEXT PRIMARY KEY,
                user_id      TEXT NOT NULL,
                qty          INTEGER NOT NULL,
                created_at   TEXT NOT NULL,
                status       TEXT DEFAULT 'active'
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS seeds (
                seed_id      TEXT PRIMARY KEY,
                order_id     TEXT NOT NULL,
                user_id      TEXT NOT NULL,
                qr_code      TEXT UNIQUE NOT NULL,
                seed_number  INTEGER NOT NULL,
                status       TEXT DEFAULT 'unplanted',
                planted_at   TEXT,
                lat          REAL,
                lon          REAL,
                stage        INTEGER DEFAULT 0,
                stage1_img   TEXT,
                stage2_img   TEXT,
                stage3_img   TEXT,
                stage1_at    TEXT,
                stage2_at    TEXT,
                stage3_at    TEXT,
                stage2_due   TEXT,
                stage3_due   TEXT,
                coins_s1     REAL DEFAULT 0,
                coins_s2     REAL DEFAULT 0,
                coins_s3     REAL DEFAULT 0,
                cancelled    INTEGER DEFAULT 0
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS growth_proofs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                seed_id      TEXT NOT NULL,
                stage        INTEGER NOT NULL,
                img_hash     TEXT,
                plant_size   REAL,
                prev_size    REAL,
                growth_pct   REAL,
                lat          REAL,
                lon          REAL,
                verified_at  TEXT NOT NULL,
                coins        REAL DEFAULT 0,
                passed       INTEGER DEFAULT 0
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_seeds ON seeds(user_id)")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_qr ON seeds(qr_code)")
        self.db.commit()

    # ── QR Code generate ─────────────────────────────────────────────────────
    def _generate_unique_qr(self, seed_id, user_id, seed_number, order_id):
        """Har seed ka bilkul unique QR"""
        # Unique token — secrets se random bytes
        unique_token = secrets.token_hex(8).upper()
        qr_code = f"GSEED-{unique_token}-{seed_number:03d}"

        if not QR_AVAILABLE:
            return qr_code, None

        # QR image banana
        qr_data = json.dumps({
            "seed_id":  seed_id,
            "qr":       qr_code,
            "user":     hashlib.sha256(user_id.encode()).hexdigest()[:8],
            "num":      seed_number,
            "app":      "GaiaVolt"
        }, separators=(',',':'))

        try:
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=8, border=3
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Green themed QR
            img = qr.make_image(fill_color="#166534", back_color="white")
            img = img.convert("RGB")

            # Add seed number label
            try:
                draw = ImageDraw.Draw(img)
                w, h = img.size
                draw.rectangle([0, h-25, w, h], fill="#166534")
                draw.text((w//2-30, h-20), f"SEED #{seed_number:03d}", fill="white")
            except:
                pass

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_b64 = base64.b64encode(buffer.getvalue()).decode()

            return qr_code, qr_b64

        except Exception as e:
            print(f"QR image error: {e}")
            return qr_code, None

    # ── Order seeds ───────────────────────────────────────────────────────────
    def order_seeds(self, user_id, qty=1):
        """User seeds order karta hai — har seed ka alag QR"""
        if qty < 1 or qty > 50:
            return {"success": False, "error": "Order 1-50 seeds at a time"}

        order_id = "ORD-" + secrets.token_hex(6).upper()
        now      = datetime.now(timezone.utc).isoformat()

        self.db.execute(
            "INSERT INTO seed_orders (order_id,user_id,qty,created_at) VALUES (?,?,?,?)",
            (order_id, user_id, qty, now)
        )

        seeds = []
        for i in range(1, qty+1):
            seed_id  = f"SEED-{secrets.token_hex(6).upper()}"
            qr_code, qr_image = self._generate_unique_qr(seed_id, user_id, i, order_id)

            self.db.execute("""
                INSERT INTO seeds
                (seed_id, order_id, user_id, qr_code, seed_number, status)
                VALUES (?,?,?,?,?,?)
            """, (seed_id, order_id, user_id, qr_code, i, 'unplanted'))

            seeds.append({
                "seed_id":    seed_id,
                "seed_number":i,
                "qr_code":    qr_code,
                "qr_image":   qr_image,  # Base64 PNG
                "status":     "unplanted"
            })

        self.db.commit()

        print(f"✅ Order {order_id}: {qty} seeds generated for {user_id}")

        return {
            "success":  True,
            "order_id": order_id,
            "qty":      qty,
            "seeds":    seeds,
            "message":  f"🌱 {qty} seed QR codes generated! Print them and plant!"
        }

    # ── Plant a seed ─────────────────────────────────────────────────────────
    def plant_seed(self, qr_code, user_id, lat, lon, img_hash, base_coins=3.0):
        """QR scan karke seed plant karo — Stage 1"""
        seed = self.db.execute(
            "SELECT * FROM seeds WHERE qr_code=? AND user_id=?",
            (qr_code, user_id)
        ).fetchone()

        if not seed:
            return {"passed": False, "reason": "Invalid QR code or not your seed!"}

        cols = ["seed_id","order_id","user_id","qr_code","seed_number",
                "status","planted_at","lat","lon","stage",
                "stage1_img","stage2_img","stage3_img",
                "stage1_at","stage2_at","stage3_at",
                "stage2_due","stage3_due",
                "coins_s1","coins_s2","coins_s3","cancelled"]
        s = dict(zip(cols, seed))

        if s["status"] == "planted":
            return {"passed": False, "reason": f"Seed #{s['seed_number']} already planted!"}

        if s["cancelled"]:
            return {"passed": False, "reason": "This seed was cancelled!"}

        now        = datetime.now(timezone.utc)
        stage2_due = (now + timedelta(days=30)).isoformat()
        stage3_due = (now + timedelta(days=90)).isoformat()
        coins_s1   = round(base_coins * 0.30, 2)

        self.db.execute("""
            UPDATE seeds SET
                status='planted', planted_at=?, lat=?, lon=?,
                stage=1, stage1_img=?, stage1_at=?,
                stage2_due=?, stage3_due=?, coins_s1=?
            WHERE seed_id=?
        """, (now.isoformat(), lat, lon, img_hash,
              now.isoformat(), stage2_due, stage3_due,
              coins_s1, s["seed_id"]))

        self.db.execute("""
            INSERT INTO growth_proofs
            (seed_id, stage, img_hash, lat, lon, verified_at, coins, passed)
            VALUES (?,1,?,?,?,?,?,1)
        """, (s["seed_id"], img_hash, lat, lon, now.isoformat(), coins_s1))

        self.db.commit()

        return {
            "passed":      True,
            "seed_id":     s["seed_id"],
            "seed_number": s["seed_number"],
            "qr_code":     qr_code,
            "stage":       1,
            "coins_now":   coins_s1,
            "stage2_due":  stage2_due,
            "message":     f"🌱 Seed #{s['seed_number']} planted! +{coins_s1} ECO. Come back in 30 days with growth proof!"
        }

    # ── Submit growth proof ───────────────────────────────────────────────────
    def submit_growth(self, qr_code, user_id, lat, lon, img_hash, plant_size_cm, base_coins=3.0):
        """
        Growth proof submit karo
        plant_size_cm: AI se estimated plant height in cm
        """
        seed = self.db.execute(
            "SELECT * FROM seeds WHERE qr_code=? AND user_id=?",
            (qr_code, user_id)
        ).fetchone()

        if not seed:
            return {"passed": False, "reason": "Invalid QR code!"}

        cols = ["seed_id","order_id","user_id","qr_code","seed_number",
                "status","planted_at","lat","lon","stage",
                "stage1_img","stage2_img","stage3_img",
                "stage1_at","stage2_at","stage3_at",
                "stage2_due","stage3_due",
                "coins_s1","coins_s2","coins_s3","cancelled"]
        s = dict(zip(cols, seed))

        if s["status"] == "unplanted":
            return {"passed": False, "reason": "Plant the seed first!"}

        if s["cancelled"]:
            return {"passed": False, "reason": "This seed was cancelled!"}

        current_stage = s["stage"]
        next_stage    = current_stage + 1

        if next_stage > 3:
            return {"passed": False, "reason": "All 3 stages complete! Maximum reward earned."}

        # Time check
        now      = datetime.now(timezone.utc)
        due_field = f"stage{next_stage}_due" if next_stage <= 3 else None

        if due_field and s.get(due_field):
            try:
                due       = datetime.fromisoformat(s[due_field])
                days_left = (due - now).days
                if days_left > 5:
                    return {
                        "passed": False,
                        "reason": f"Too early! Come back in {days_left} days for Stage {next_stage} proof."
                    }
            except:
                pass

        # GPS check — within 30m of original planting
        if lat and lon and s["lat"] and s["lon"]:
            dlat = math.radians(lat - s["lat"])
            dlon = math.radians(lon - s["lon"])
            a    = (math.sin(dlat/2)**2 +
                    math.cos(math.radians(lat)) *
                    math.cos(math.radians(s["lat"])) *
                    math.sin(dlon/2)**2)
            dist = 6371000 * 2 * math.asin(math.sqrt(a))
            if dist > 30:
                return {
                    "passed": False,
                    "reason": f"Wrong location! {dist:.0f}m from planting spot. Must be within 30m."
                }

        # Growth check — plant bada hona chahiye
        prev_size  = None
        growth_pct = 0
        min_growth = {2: 5.0, 3: 15.0}  # cm minimum growth

        if plant_size_cm and plant_size_cm > 0:
            # Get previous stage size
            prev_proof = self.db.execute("""
                SELECT plant_size FROM growth_proofs
                WHERE seed_id=? AND stage=?
                ORDER BY verified_at DESC LIMIT 1
            """, (s["seed_id"], current_stage)).fetchone()

            if prev_proof and prev_proof[0]:
                prev_size  = prev_proof[0]
                growth_pct = ((plant_size_cm - prev_size) / prev_size) * 100

                if plant_size_cm <= prev_size:
                    return {
                        "passed": False,
                        "reason": f"No growth detected! Plant was {prev_size}cm, still {plant_size_cm}cm. Must show real growth."
                    }

                min_g = min_growth.get(next_stage, 5.0)
                if plant_size_cm < min_g:
                    return {
                        "passed": False,
                        "reason": f"Plant too small ({plant_size_cm}cm). Need at least {min_g}cm for Stage {next_stage}."
                    }

        # Calculate reward
        reward_pcts = {2: 0.40, 3: 0.30}
        coins = round(base_coins * reward_pcts.get(next_stage, 0.30), 2)

        # Update seed
        img_col   = f"stage{next_stage}_img"
        time_col  = f"stage{next_stage}_at"
        coins_col = f"coins_s{next_stage}"

        self.db.execute(f"""
            UPDATE seeds SET stage=?, {img_col}=?, {time_col}=?, {coins_col}=?
            WHERE seed_id=?
        """, (next_stage, img_hash, now.isoformat(), coins, s["seed_id"]))

        self.db.execute("""
            INSERT INTO growth_proofs
            (seed_id, stage, img_hash, plant_size, prev_size, growth_pct,
             lat, lon, verified_at, coins, passed)
            VALUES (?,?,?,?,?,?,?,?,?,?,1)
        """, (s["seed_id"], next_stage, img_hash, plant_size_cm,
              prev_size, growth_pct, lat, lon, now.isoformat(), coins))

        self.db.commit()

        stage_names = {2:"🌿 Seedling Growing", 3:"🌳 Plant Established"}
        return {
            "passed":      True,
            "seed_id":     s["seed_id"],
            "seed_number": s["seed_number"],
            "stage":       next_stage,
            "coins_earned":coins,
            "growth_pct":  round(growth_pct, 1),
            "plant_size":  plant_size_cm,
            "message":     f"{stage_names.get(next_stage,'✅')} verified! +{coins} ECO earned! Growth: {growth_pct:.1f}%"
        }

    # ── Cancel inactive seeds ─────────────────────────────────────────────────
    def cancel_inactive_seeds(self):
        """30 days baad growth proof nahi = cancel"""
        now     = datetime.now(timezone.utc).isoformat()
        expired = self.db.execute("""
            SELECT seed_id, user_id, coins_s1
            FROM seeds
            WHERE stage=1 AND cancelled=0
            AND status='planted' AND stage2_due < ?
        """, (now,)).fetchall()

        for seed_id, user_id, coins in expired:
            self.db.execute(
                "UPDATE seeds SET cancelled=1, status='cancelled' WHERE seed_id=?",
                (seed_id,)
            )
        self.db.commit()
        return len(expired)

    # ── Get user seeds ────────────────────────────────────────────────────────
    def get_user_seeds(self, user_id):
        """User ke sab seeds"""
        rows = self.db.execute("""
            SELECT seed_id, qr_code, seed_number, status, stage,
                   planted_at, lat, lon,
                   coins_s1, coins_s2, coins_s3,
                   stage2_due, stage3_due, cancelled
            FROM seeds WHERE user_id=?
            ORDER BY seed_number ASC
        """, (user_id,)).fetchall()

        now   = datetime.now(timezone.utc)
        seeds = []
        for r in rows:
            total = (r[8] or 0) + (r[9] or 0) + (r[10] or 0)
            days_to_next = None
            due = r[11] if r[4] == 1 else r[12] if r[4] == 2 else None
            if due:
                try:
                    days_to_next = max(0, (datetime.fromisoformat(due) - now).days)
                except:
                    pass

            seeds.append({
                "seed_id":      r[0],
                "qr_code":      r[1],
                "seed_number":  r[2],
                "status":       r[3],
                "stage":        r[4],
                "stage_label":  ["Unplanted","Planted","Growing","Established"][min(r[4],3)],
                "planted_at":   r[5],
                "lat":          r[6],
                "lon":          r[7],
                "coins_earned": round(total, 2),
                "days_to_next": days_to_next,
                "cancelled":    r[13],
            })
        return seeds

    def get_seed_by_qr(self, qr_code):
        """QR code se seed info"""
        row = self.db.execute(
            "SELECT * FROM seeds WHERE qr_code=?", (qr_code,)
        ).fetchone()
        if not row:
            return None
        cols = ["seed_id","order_id","user_id","qr_code","seed_number",
                "status","planted_at","lat","lon","stage",
                "stage1_img","stage2_img","stage3_img",
                "stage1_at","stage2_at","stage3_at",
                "stage2_due","stage3_due",
                "coins_s1","coins_s2","coins_s3","cancelled"]
        return dict(zip(cols, row))