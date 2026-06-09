"""
GaiaVolt — Day 26: Real-World Bridges
Solar companies + eco partners se discount coupons
MVP: Mock structure — real API ready hai plug-in ke liye
"""
import sqlite3
import hashlib
import random
import string
from datetime import datetime, timezone, timedelta
import os

# ── Partner companies ─────────────────────────────────────────────────────────
PARTNERS = [
    {
        "id":          "solar_one",
        "name":        "SolarOne Pakistan",
        "category":    "solar",
        "icon":        "☀️",
        "color":       "#f59e0b",
        "description": "Pakistan's #1 solar panel brand",
        "website":     "https://solarone.pk",
        "deals": [
            {
                "id":          "sol_001",
                "title":       "10% off Solar Panel Installation",
                "description": "10% discount on complete home solar system",
                "eco_coins":   50,
                "valid_days":  30,
                "category":    "installation",
            },
            {
                "id":          "sol_002",
                "title":       "Free Site Survey",
                "description": "Free home solar assessment",
                "eco_coins":   20,
                "valid_days":  15,
                "category":    "survey",
            },
        ]
    },
    {
        "id":          "green_cycle",
        "name":        "GreenCycle Karachi",
        "category":    "cycling",
        "icon":        "🚲",
        "color":       "#22c55e",
        "description": "Premium bicycles and accessories",
        "website":     "https://greencycle.pk",
        "deals": [
            {
                "id":          "cyc_001",
                "title":       "15% off Any Bicycle",
                "description": "Special GaiaVolt discount on all models",
                "eco_coins":   40,
                "valid_days":  30,
                "category":    "purchase",
            },
            {
                "id":          "cyc_002",
                "title":       "Free Helmet with Purchase",
                "description": "Free helmet with any bicycle purchase",
                "eco_coins":   30,
                "valid_days":  20,
                "category":    "gift",
            },
        ]
    },
    {
        "id":          "eco_bulb",
        "name":        "EcoBulb LED Store",
        "category":    "led",
        "icon":        "💡",
        "color":       "#fde047",
        "description": "Energy saving LED lighting solutions",
        "website":     "https://ecobulb.pk",
        "deals": [
            {
                "id":          "led_001",
                "title":       "Buy 2 Get 1 Free LED",
                "description": "Special offer on LED bulbs",
                "eco_coins":   25,
                "valid_days":  15,
                "category":    "offer",
            },
        ]
    },
    {
        "id":          "recycle_pk",
        "name":        "RecyclePK",
        "category":    "recycling",
        "icon":        "♻️",
        "color":       "#34d399",
        "description": "Pakistan's first digital recycling platform",
        "website":     "https://recycle.pk",
        "deals": [
            {
                "id":          "rec_001",
                "title":       "Double Points on Next Drop",
                "description": "2x reward on your next recycling drop",
                "eco_coins":   15,
                "valid_days":  7,
                "category":    "reward",
            },
        ]
    },
    {
        "id":          "ev_motors",
        "name":        "EV Motors Pakistan",
        "category":    "ev",
        "icon":        "⚡",
        "color":       "#a78bfa",
        "description": "Electric vehicles and charging solutions",
        "website":     "https://evmotors.pk",
        "deals": [
            {
                "id":          "ev_001",
                "title":       "5% off EV Purchase",
                "description": "GaiaVolt discount on any electric vehicle",
                "eco_coins":   200,
                "valid_days":  60,
                "category":    "purchase",
            },
            {
                "id":          "ev_002",
                "title":       "Free Home Charger Installation",
                "description": "Free home charging station with EV purchase",
                "eco_coins":   150,
                "valid_days":  45,
                "category":    "installation",
            },
        ]
    },
    {
        "id":          "green_farm",
        "name":        "GreenFarm Organics",
        "category":    "farming",
        "icon":        "🌾",
        "color":       "#86efac",
        "description": "Organic seeds, fertilizers and farming tools",
        "website":     "https://greenfarm.pk",
        "deals": [
            {
                "id":          "farm_001",
                "title":       "20% off Organic Seeds",
                "description": "Discount on all organic seed varieties",
                "eco_coins":   35,
                "valid_days":  30,
                "category":    "seeds",
            },
        ]
    },
]


class BridgesEngine:

    def __init__(self):
        self.db = sqlite3.connect("bridges.db", check_same_thread=False)
        self._init_db()
        print("✅ Bridges Engine ready!")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_code  TEXT PRIMARY KEY,
                user_id      TEXT NOT NULL,
                partner_id   TEXT NOT NULL,
                deal_id      TEXT NOT NULL,
                deal_title   TEXT NOT NULL,
                eco_coins    INTEGER NOT NULL,
                expires_at   TEXT NOT NULL,
                redeemed     INTEGER DEFAULT 0,
                redeemed_at  TEXT,
                created_at   TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS partner_clicks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT,
                partner_id TEXT,
                timestamp  TEXT
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_coupons ON coupons(user_id)")
        self.db.commit()

    def _generate_coupon_code(self, partner_id, deal_id):
        """Unique coupon code generate karo"""
        chars    = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(chars, k=6))
        prefix   = partner_id[:3].upper()
        return f"GAIA-{prefix}-{random_part}"

    def get_all_partners(self):
        """Sab partners + deals return karo"""
        return PARTNERS

    def get_partner_by_category(self, category):
        """Category se partners filter karo"""
        return [p for p in PARTNERS if p["category"] == category]

    def get_user_coupons(self, user_id):
        """User ke active coupons"""
        rows = self.db.execute("""
            SELECT coupon_code, partner_id, deal_id, deal_title,
                   eco_coins, expires_at, redeemed, created_at
            FROM coupons
            WHERE user_id=? AND redeemed=0
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()

        coupons = []
        now = datetime.now(timezone.utc)
        for r in rows:
            try:
                exp = datetime.fromisoformat(r[5])
                days_left = (exp - now).days
                if days_left >= 0:
                    coupons.append({
                        "coupon_code": r[0],
                        "partner_id":  r[1],
                        "deal_id":     r[2],
                        "deal_title":  r[3],
                        "eco_coins":   r[4],
                        "expires_at":  r[5],
                        "days_left":   days_left,
                        "redeemed":    r[6],
                    })
            except:
                pass
        return coupons

    def claim_coupon(self, user_id, partner_id, deal_id, user_coins):
        """User ECO coins se coupon claim karo"""
        # Find partner + deal
        partner = next((p for p in PARTNERS if p["id"]==partner_id), None)
        if not partner:
            return {"success":False, "error":"Partner not found"}

        deal = next((d for d in partner["deals"] if d["id"]==deal_id), None)
        if not deal:
            return {"success":False, "error":"Deal not found"}

        # Check coins
        if user_coins < deal["eco_coins"]:
            return {
                "success": False,
                "error":   f"Insufficient ECO coins! Need {deal['eco_coins']}, you have {user_coins:.1f}"
            }

        # Check already claimed
        existing = self.db.execute("""
            SELECT 1 FROM coupons
            WHERE user_id=? AND deal_id=? AND redeemed=0
        """, (user_id, deal_id)).fetchone()
        if existing:
            return {"success":False, "error":"You already have this coupon!"}

        # Generate coupon
        code       = self._generate_coupon_code(partner_id, deal_id)
        now        = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=deal["valid_days"])).isoformat()

        self.db.execute("""
            INSERT INTO coupons
            (coupon_code, user_id, partner_id, deal_id, deal_title,
             eco_coins, expires_at, redeemed, created_at)
            VALUES (?,?,?,?,?,?,?,0,?)
        """, (code, user_id, partner_id, deal_id, deal["title"],
              deal["eco_coins"], expires_at, now.isoformat()))
        self.db.commit()

        return {
            "success":     True,
            "coupon_code": code,
            "deal_title":  deal["title"],
            "partner":     partner["name"],
            "expires_at":  expires_at,
            "valid_days":  deal["valid_days"],
            "coins_spent": deal["eco_coins"],
        }

    def redeem_coupon(self, coupon_code, user_id):
        """Coupon redeem karo"""
        row = self.db.execute(
            "SELECT * FROM coupons WHERE coupon_code=? AND user_id=?",
            (coupon_code, user_id)
        ).fetchone()

        if not row:
            return {"success":False, "error":"Coupon not found"}
        if row[7]:  # redeemed
            return {"success":False, "error":"Coupon already redeemed"}

        now = datetime.now(timezone.utc)
        try:
            exp = datetime.fromisoformat(row[6])
            if now > exp:
                return {"success":False, "error":"Coupon expired!"}
        except:
            pass

        self.db.execute("""
            UPDATE coupons SET redeemed=1, redeemed_at=?
            WHERE coupon_code=?
        """, (now.isoformat(), coupon_code))
        self.db.commit()

        return {"success":True, "message":"Coupon redeemed successfully!"}

    def get_stats(self):
        total    = self.db.execute("SELECT COUNT(*) FROM coupons").fetchone()[0]
        redeemed = self.db.execute("SELECT COUNT(*) FROM coupons WHERE redeemed=1").fetchone()[0]
        return {"total_coupons": total, "redeemed": redeemed, "partners": len(PARTNERS)}