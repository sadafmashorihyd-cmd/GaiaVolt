"""
GaiaVolt — Evolution Engine Day 25
User levels: Seedling → Sapling → Tree → Forest → Carbon Zero Hero
XP system, NFT evolution, avatar stages
"""
import sqlite3
import hashlib
import os
import json
from datetime import datetime, timezone


# ── Level definitions ─────────────────────────────────────────────────────────
LEVELS = [
    {"level": 1, "name": "Seedling",        "icon": "🌱", "xp_required": 0,    "color": "#86efac"},
    {"level": 2, "name": "Sapling",          "icon": "🌿", "xp_required": 100,  "color": "#4ade80"},
    {"level": 3, "name": "Young Tree",       "icon": "🌳", "xp_required": 300,  "color": "#22c55e"},
    {"level": 4, "name": "Forest Guardian",  "icon": "🌲", "xp_required": 700,  "color": "#16a34a"},
    {"level": 5, "name": "Eco Warrior",      "icon": "🦅", "xp_required": 1500, "color": "#15803d"},
    {"level": 6, "name": "Planet Protector", "icon": "🌍", "xp_required": 3000, "color": "#166534"},
    {"level": 7, "name": "Carbon Zero Hero", "icon": "⚡", "xp_required": 6000, "color": "#f59e0b"},
]

# ── XP rewards per activity ───────────────────────────────────────────────────
XP_REWARDS = {
    "cycling":            30,
    "plantation":         50,
    "ocean_cleanup":      60,
    "solar_panels":       80,
    "recycling":          25,
    "utility_bills":      20,
    "public_transport":   20,
    "electric_cars":      40,
    "led_lighting":       15,
    "water_conservation": 25,
    "wind_energy":        70,
    "organic_farming":    45,
}


class EvolutionEngine:

    def __init__(self):
        self.db = sqlite3.connect("evolution.db", check_same_thread=False)
        self._init_db()
        print("✅ Evolution Engine ready!")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id      TEXT PRIMARY KEY,
                display_name TEXT DEFAULT 'Eco Hero',
                level        INTEGER DEFAULT 1,
                xp           INTEGER DEFAULT 0,
                coins_total  REAL DEFAULT 0,
                carbon_total REAL DEFAULT 0,
                avatar_stage INTEGER DEFAULT 1,
                nft_id       TEXT,
                streak_days  INTEGER DEFAULT 0,
                last_active  TEXT,
                created_at   TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      TEXT NOT NULL,
                activity     TEXT NOT NULL,
                xp_earned    INTEGER NOT NULL,
                coins_earned REAL NOT NULL,
                carbon_kg    REAL NOT NULL,
                timestamp    TEXT NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS nfts (
                nft_id       TEXT PRIMARY KEY,
                user_id      TEXT NOT NULL,
                name         TEXT NOT NULL,
                stage        INTEGER DEFAULT 1,
                xp_at_mint   INTEGER DEFAULT 0,
                created_at   TEXT NOT NULL,
                last_evolved TEXT
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_log ON activity_log(user_id)")
        self.db.commit()

    # ── User management ───────────────────────────────────────────────────────
    def get_or_create_user(self, user_id, display_name="Eco Hero"):
        row = self.db.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        if not row:
            now    = datetime.now(timezone.utc).isoformat()
            nft_id = self._mint_nft(user_id, 1)
            self.db.execute("""
                INSERT INTO users
                (user_id, display_name, level, xp, coins_total,
                 carbon_total, avatar_stage, nft_id, streak_days, last_active, created_at)
                VALUES (?,?,1,0,0,0,1,?,0,?,?)
            """, (user_id, display_name, nft_id, now, now))
            self.db.commit()
            row = self.db.execute(
                "SELECT * FROM users WHERE user_id=?", (user_id,)
            ).fetchone()
        return self._row_to_user(row)

    def _row_to_user(self, row):
        cols = ["user_id","display_name","level","xp","coins_total",
                "carbon_total","avatar_stage","nft_id","streak_days","last_active","created_at"]
        return dict(zip(cols, row))

    # ── NFT minting ───────────────────────────────────────────────────────────
    def _mint_nft(self, user_id, stage):
        nft_id = "NFT-" + hashlib.sha256(
            f"{user_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12].upper()
        now = datetime.now(timezone.utc).isoformat()
        self.db.execute("""
            INSERT INTO nfts (nft_id, user_id, name, stage, xp_at_mint, created_at, last_evolved)
            VALUES (?,?,?,?,0,?,?)
        """, (nft_id, user_id, f"EcoSoul #{nft_id[-6:]}", stage, now, now))
        self.db.commit()
        return nft_id

    def evolve_nft(self, user_id, new_stage, xp):
        """NFT evolve karo jab level up ho"""
        nft = self.db.execute(
            "SELECT nft_id FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        if nft:
            self.db.execute("""
                UPDATE nfts SET stage=?, xp_at_mint=?, last_evolved=?
                WHERE nft_id=?
            """, (new_stage, xp, datetime.now(timezone.utc).isoformat(), nft[0]))
            self.db.commit()

    # ── XP + Level system ─────────────────────────────────────────────────────
    def get_level_for_xp(self, xp):
        current = LEVELS[0]
        for lvl in LEVELS:
            if xp >= lvl["xp_required"]:
                current = lvl
        return current

    def get_next_level(self, current_level):
        for lvl in LEVELS:
            if lvl["level"] == current_level + 1:
                return lvl
        return None

    def add_activity(self, user_id, activity, coins, carbon_kg):
        """Activity ke baad XP + coins add karo"""
        user     = self.get_or_create_user(user_id)
        xp_earn  = XP_REWARDS.get(activity, 10)
        old_xp   = user["xp"]
        new_xp   = old_xp + xp_earn
        new_coins = user["coins_total"] + coins
        new_carbon = user["carbon_total"] + carbon_kg

        old_level = self.get_level_for_xp(old_xp)
        new_level = self.get_level_for_xp(new_xp)
        leveled_up = new_level["level"] > old_level["level"]

        # Update streak
        now = datetime.now(timezone.utc)
        streak = user["streak_days"]
        if user["last_active"]:
            try:
                last = datetime.fromisoformat(user["last_active"])
                diff = (now - last).days
                if diff == 1:
                    streak += 1
                elif diff > 1:
                    streak = 1
            except:
                streak = 1

        # Update user
        self.db.execute("""
            UPDATE users SET
                xp=?, coins_total=?, carbon_total=?,
                level=?, avatar_stage=?,
                streak_days=?, last_active=?
            WHERE user_id=?
        """, (
            new_xp, new_coins, new_carbon,
            new_level["level"], new_level["level"],
            streak, now.isoformat(),
            user_id
        ))

        # Log activity
        self.db.execute("""
            INSERT INTO activity_log
            (user_id, activity, xp_earned, coins_earned, carbon_kg, timestamp)
            VALUES (?,?,?,?,?,?)
        """, (user_id, activity, xp_earn, coins, carbon_kg, now.isoformat()))
        self.db.commit()

        # NFT evolve on level up
        if leveled_up:
            self.evolve_nft(user_id, new_level["level"], new_xp)

        next_lvl = self.get_next_level(new_level["level"])
        xp_to_next = (next_lvl["xp_required"] - new_xp) if next_lvl else 0

        return {
            "user_id":      user_id,
            "xp_earned":    xp_earn,
            "total_xp":     new_xp,
            "level":        new_level,
            "leveled_up":   leveled_up,
            "old_level":    old_level,
            "next_level":   next_lvl,
            "xp_to_next":   max(0, xp_to_next),
            "coins_total":  round(new_coins, 2),
            "carbon_total": round(new_carbon, 3),
            "streak_days":  streak,
        }

    def get_profile(self, user_id):
        """Full user profile"""
        user = self.get_or_create_user(user_id)
        level_info = self.get_level_for_xp(user["xp"])
        next_lvl   = self.get_next_level(level_info["level"])

        # Recent activities
        activities = self.db.execute("""
            SELECT activity, xp_earned, coins_earned, carbon_kg, timestamp
            FROM activity_log WHERE user_id=?
            ORDER BY timestamp DESC LIMIT 10
        """, (user_id,)).fetchall()

        # NFT info
        nft = None
        if user["nft_id"]:
            row = self.db.execute(
                "SELECT * FROM nfts WHERE nft_id=?", (user["nft_id"],)
            ).fetchone()
            if row:
                nft = dict(zip(
                    ["nft_id","user_id","name","stage","xp_at_mint","created_at","last_evolved"],
                    row
                ))

        # XP progress %
        xp_progress = 0
        if next_lvl:
            xp_in_level  = user["xp"] - level_info["xp_required"]
            xp_needed    = next_lvl["xp_required"] - level_info["xp_required"]
            xp_progress  = min(100, int((xp_in_level / xp_needed) * 100))

        return {
            "user":       user,
            "level":      level_info,
            "next_level": next_lvl,
            "xp_progress": xp_progress,
            "nft":        nft,
            "recent_activities": [
                {
                    "activity": a[0], "xp": a[1],
                    "coins": a[2], "carbon": a[3], "time": a[4]
                } for a in activities
            ],
            "all_levels": LEVELS,
        }

    def get_leaderboard(self, limit=10):
        rows = self.db.execute("""
            SELECT user_id, display_name, level, xp, coins_total, carbon_total
            FROM users ORDER BY xp DESC LIMIT ?
        """, (limit,)).fetchall()
        return [
            {
                "rank": i+1,
                "user_id": r[0], "name": r[1],
                "level": r[2], "xp": r[3],
                "coins": r[4], "carbon": r[5]
            }
            for i, r in enumerate(rows)
        ]