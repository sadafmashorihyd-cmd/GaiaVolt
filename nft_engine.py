"""
GaiaVolt — Day 27: Dynamic NFTs
Monthly winner ko special NFT milta hai jo waqt ke saath grow karta hai
"""
import sqlite3
import hashlib
import json
from datetime import datetime, timezone, timedelta
import calendar

# NFT Tiers — time ke saath evolve karte hain
NFT_TIERS = [
    {"tier":1, "name":"Eco Spark",      "icon":"✨", "color":"#86efac", "months":0  },
    {"tier":2, "name":"Green Flame",    "icon":"🔥", "color":"#4ade80", "months":3  },
    {"tier":3, "name":"Earth Guardian", "icon":"🌍", "color":"#22c55e", "months":6  },
    {"tier":4, "name":"Forest Lord",    "icon":"🌲", "color":"#16a34a", "months":12 },
    {"tier":5, "name":"Planet Savior",  "icon":"⚡", "color":"#f59e0b", "months":24 },
]

# Special monthly NFTs
MONTHLY_NFTS = {
    1:  {"theme":"New Beginnings",  "icon":"🌱", "color":"#86efac"},
    2:  {"theme":"Love the Earth",  "icon":"💚", "color":"#4ade80"},
    3:  {"theme":"Spring Bloom",    "icon":"🌸", "color":"#f9a8d4"},
    4:  {"theme":"Earth Day Hero",  "icon":"🌍", "color":"#22c55e"},
    5:  {"theme":"Solar Power",     "icon":"☀️", "color":"#fde047"},
    6:  {"theme":"Ocean Guardian",  "icon":"🌊", "color":"#38bdf8"},
    7:  {"theme":"Green Summer",    "icon":"🌿", "color":"#4ade80"},
    8:  {"theme":"Harvest Hero",    "icon":"🌾", "color":"#f59e0b"},
    9:  {"theme":"Clean Air",       "icon":"💨", "color":"#67e8f9"},
    10: {"theme":"Eco October",     "icon":"🍂", "color":"#fb923c"},
    11: {"theme":"Carbon Warrior",  "icon":"⚔️", "color":"#a78bfa"},
    12: {"theme":"Year Champion",   "icon":"🏆", "color":"#f59e0b"},
}


class NFTEngine:

    def __init__(self):
        self.db = sqlite3.connect("nfts.db", check_same_thread=False)
        self._init_db()
        print("✅ NFT Engine ready!")

    def _init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_nfts (
                nft_id       TEXT PRIMARY KEY,
                user_id      TEXT NOT NULL,
                user_name    TEXT,
                month        INTEGER NOT NULL,
                year         INTEGER NOT NULL,
                theme        TEXT NOT NULL,
                icon         TEXT NOT NULL,
                color        TEXT NOT NULL,
                tier         INTEGER DEFAULT 1,
                xp_at_mint   INTEGER DEFAULT 0,
                carbon_saved REAL DEFAULT 0,
                minted_at    TEXT NOT NULL,
                last_evolved TEXT,
                metadata     TEXT
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS monthly_winners (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                month      INTEGER NOT NULL,
                year       INTEGER NOT NULL,
                user_id    TEXT NOT NULL,
                user_name  TEXT,
                xp         INTEGER,
                carbon     REAL,
                nft_id     TEXT,
                announced  TEXT NOT NULL
            )
        """)
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_user_nfts ON dynamic_nfts(user_id)")
        self.db.commit()

    def generate_nft_id(self, user_id, month, year):
        h = hashlib.sha256(f"{user_id}{month}{year}GaiaVolt".encode()).hexdigest()
        return f"GNFT-{year}{month:02d}-{h[:8].upper()}"

    def get_tier_for_months(self, months_old):
        """NFT kitne months purana hai usse tier decide hota hai"""
        tier = NFT_TIERS[0]
        for t in NFT_TIERS:
            if months_old >= t["months"]:
                tier = t
        return tier

    def mint_winner_nft(self, user_id, user_name, month, year, xp, carbon):
        """Monthly winner ko NFT mint karo"""
        nft_id   = self.generate_nft_id(user_id, month, year)
        theme    = MONTHLY_NFTS.get(month, MONTHLY_NFTS[1])
        now      = datetime.now(timezone.utc)

        # Check already minted
        existing = self.db.execute(
            "SELECT nft_id FROM dynamic_nfts WHERE user_id=? AND month=? AND year=?",
            (user_id, month, year)
        ).fetchone()
        if existing:
            return {"success":False, "error":"NFT already minted for this month", "nft_id":existing[0]}

        metadata = json.dumps({
            "user":    user_name,
            "month":   month,
            "year":    year,
            "xp":      xp,
            "carbon":  carbon,
            "created": now.isoformat(),
            "chain":   "Polygon",
            "standard":"ERC-721",
        })

        self.db.execute("""
            INSERT INTO dynamic_nfts
            (nft_id, user_id, user_name, month, year, theme, icon, color,
             tier, xp_at_mint, carbon_saved, minted_at, last_evolved, metadata)
            VALUES (?,?,?,?,?,?,?,?,1,?,?,?,?,?)
        """, (
            nft_id, user_id, user_name, month, year,
            theme["theme"], theme["icon"], theme["color"],
            xp, carbon, now.isoformat(), now.isoformat(), metadata
        ))

        # Save winner record
        self.db.execute("""
            INSERT OR REPLACE INTO monthly_winners
            (month, year, user_id, user_name, xp, carbon, nft_id, announced)
            VALUES (?,?,?,?,?,?,?,?)
        """, (month, year, user_id, user_name, xp, carbon, nft_id, now.isoformat()))

        self.db.commit()

        return {
            "success":  True,
            "nft_id":   nft_id,
            "theme":    theme["theme"],
            "icon":     theme["icon"],
            "color":    theme["color"],
            "month":    month,
            "year":     year,
        }

    def evolve_nft(self, nft_id):
        """NFT ko evolve karo based on age"""
        row = self.db.execute(
            "SELECT minted_at, tier, month, year FROM dynamic_nfts WHERE nft_id=?",
            (nft_id,)
        ).fetchone()
        if not row:
            return {"success":False, "error":"NFT not found"}

        minted   = datetime.fromisoformat(row[0])
        now      = datetime.now(timezone.utc)
        months   = (now.year - minted.year)*12 + (now.month - minted.month)
        new_tier = self.get_tier_for_months(months)

        self.db.execute(
            "UPDATE dynamic_nfts SET tier=?, last_evolved=? WHERE nft_id=?",
            (new_tier["tier"], now.isoformat(), nft_id)
        )
        self.db.commit()
        return {"success":True, "tier":new_tier, "months_old":months}

    def get_user_nfts(self, user_id):
        """User ke sab NFTs"""
        rows = self.db.execute("""
            SELECT nft_id, user_name, month, year, theme, icon, color,
                   tier, xp_at_mint, carbon_saved, minted_at, metadata
            FROM dynamic_nfts WHERE user_id=?
            ORDER BY year DESC, month DESC
        """, (user_id,)).fetchall()

        nfts = []
        now  = datetime.now(timezone.utc)
        for r in rows:
            try:
                minted   = datetime.fromisoformat(r[10])
                months   = (now.year - minted.year)*12 + (now.month - minted.month)
                tier_info = self.get_tier_for_months(months)
            except:
                months, tier_info = 0, NFT_TIERS[0]

            month_name = calendar.month_name[r[2]]
            nfts.append({
                "nft_id":    r[0],
                "user_name": r[1],
                "month":     r[2],
                "month_name":month_name,
                "year":      r[3],
                "theme":     r[4],
                "icon":      r[5],
                "color":     r[6],
                "tier":      tier_info,
                "xp":        r[8],
                "carbon":    r[9],
                "minted_at": r[10],
                "months_old":months,
            })
        return nfts

    def get_monthly_winners(self, limit=6):
        """Recent monthly winners"""
        rows = self.db.execute("""
            SELECT month, year, user_id, user_name, xp, carbon, nft_id, announced
            FROM monthly_winners
            ORDER BY year DESC, month DESC LIMIT ?
        """, (limit,)).fetchall()

        winners = []
        for r in rows:
            month_name = calendar.month_name[r[0]]
            winners.append({
                "month":      r[0],
                "month_name": month_name,
                "year":       r[1],
                "user_id":    r[2],
                "user_name":  r[3],
                "xp":         r[4],
                "carbon":     r[5],
                "nft_id":     r[6],
                "theme":      MONTHLY_NFTS.get(r[0], MONTHLY_NFTS[1]),
            })
        return winners

    def calculate_monthly_winner(self, evolution_db_path="evolution.db"):
        """Evolution DB se is month ka winner nikalo"""
        try:
            evo_db = sqlite3.connect(evolution_db_path, check_same_thread=False)
            now    = datetime.now(timezone.utc)
            rows   = evo_db.execute("""
                SELECT user_id, display_name, xp, carbon_total
                FROM users ORDER BY xp DESC LIMIT 1
            """).fetchall()
            evo_db.close()

            if not rows:
                return None

            winner = rows[0]
            return {
                "user_id":   winner[0],
                "user_name": winner[1],
                "xp":        winner[2],
                "carbon":    winner[3],
                "month":     now.month,
                "year":      now.year,
            }
        except Exception as e:
            print(f"Winner calc error: {e}")
            return None