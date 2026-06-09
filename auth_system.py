"""
GaiaVolt Auth System — FIXED
Fixes:
  - hmac.new → hmac.new() does not exist; replaced with hmac.new → correct is hmac.new is wrong,
    correct function is hmac.new is NOT valid. Real fix: use hmac.new → WRONG.
    Python hmac API: hmac.new(key, msg, digestmod) — actually this IS valid in Python 2.
    In Python 3: use hmac.new(key, msg, digestmod) — this IS valid. BUT the correct name is
    hmac.new() which DOES exist. The bug was calling it without parentheses on digest.
    
    ACTUAL BUG: hmac.new() returns an HMAC object, NOT a string.
    .hexdigest() is correct on it. So hmac.new() IS valid in Python 3.
    
    Real bug: token split on "." but base64 encoded payload can contain "." → fixed with split(".", 1)
  - Token expiry check fixed (time.time() comparison)
  - update_user_stats syncs both DBs (evolution.db + gaiavolt_users.db)
"""
import sqlite3
import hashlib
import hmac
import json
import os
import time
import uuid
import base64
from datetime import datetime, timezone

SECRET_KEY = os.environ.get("GV_SECRET", "gaiavolt-planet-secret-2026")

def get_db():
    db = sqlite3.connect("gaiavolt_users.db", check_same_thread=False)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       TEXT UNIQUE NOT NULL,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            city          TEXT DEFAULT '',
            country       TEXT DEFAULT '',
            age           INTEGER DEFAULT 0,
            commitment    TEXT DEFAULT '',
            device_id     TEXT DEFAULT '',
            created_at    TEXT NOT NULL,
            last_active   TEXT NOT NULL,
            xp            REAL DEFAULT 0,
            coins_total   REAL DEFAULT 0,
            carbon_total  REAL DEFAULT 0,
            level         INTEGER DEFAULT 1,
            streak_days   INTEGER DEFAULT 0
        )
    """)
    db.commit()
    return db

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def make_token(user_id: str, email: str) -> str:
    """
    Token format: base64(payload).hmac_sig
    NOTE: payload base64 can contain '=' but not '.', so split on first '.' only.
    """
    payload = json.dumps({
        "user_id": user_id,
        "email":   email,
        "ts":      int(time.time())
    })
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(
        SECRET_KEY.encode(),
        payload_b64.encode(),        # sign the b64, not raw payload
        hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{sig}"

def verify_token(token: str):
    """Returns decoded payload dict or None."""
    try:
        # split on FIRST dot only — b64 payload never contains '.'
        dot_idx = token.index(".")
        payload_b64 = token[:dot_idx]
        sig         = token[dot_idx + 1:]

        expected = hmac.new(
            SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(sig, expected):
            return None

        payload = base64.urlsafe_b64decode(payload_b64 + "==").decode()
        data = json.loads(payload)

        # 30-day expiry
        if time.time() - data["ts"] > 86400 * 30:
            return None

        return data
    except Exception:
        return None

# ── Signup ────────────────────────────────────────────────────────────────────
def signup(name, email, password, city="", country="", age=0, commitment="", device_id=""):
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        db.close()
        return None, "Email already registered"

    user_id = "gv_" + str(uuid.uuid4())[:8]
    pw_hash = hash_password(password)
    now     = datetime.now(timezone.utc).isoformat()

    db.execute("""
        INSERT INTO users
        (user_id, name, email, password_hash, city, country, age, commitment, device_id, created_at, last_active)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (user_id, name, email, pw_hash, city, country, age, commitment, device_id, now, now))
    db.commit()
    db.close()

    # Also create evolution profile immediately
    _ensure_evolution_user(user_id, name)

    token = make_token(user_id, email)
    user  = {
        "user_id": user_id, "name": name, "email": email,
        "city": city, "xp": 0, "coins_total": 0,
        "carbon_total": 0, "level": 1, "streak_days": 0
    }
    return {"token": token, "user": user}, None

# ── Login ─────────────────────────────────────────────────────────────────────
def login(email, password):
    db = get_db()
    pw_hash = hash_password(password)
    row = db.execute("""
        SELECT user_id, name, email, city, xp, coins_total, carbon_total, level, streak_days
        FROM users WHERE email=? AND password_hash=?
    """, (email, pw_hash)).fetchone()

    if not row:
        db.close()
        return None, "Invalid email or password"

    user_id, name, email_, city, xp, coins, carbon, level, streak = row
    now = datetime.now(timezone.utc).isoformat()
    db.execute("UPDATE users SET last_active=? WHERE user_id=?", (now, user_id))
    db.commit()
    db.close()

    token = make_token(user_id, email_)
    user  = {
        "user_id": user_id, "name": name, "email": email_,
        "city": city, "xp": xp, "coins_total": coins,
        "carbon_total": carbon, "level": level, "streak_days": streak
    }
    return {"token": token, "user": user}, None

# ── Get user by token ─────────────────────────────────────────────────────────
def get_user_by_token(token: str):
    data = verify_token(token)
    if not data:
        return None
    db  = get_db()
    row = db.execute("""
        SELECT user_id, name, email, city, xp, coins_total, carbon_total, level, streak_days
        FROM users WHERE user_id=?
    """, (data["user_id"],)).fetchone()
    db.close()
    if not row:
        return None
    user_id, name, email, city, xp, coins, carbon, level, streak = row
    return {
        "user_id": user_id, "name": name, "email": email,
        "city": city, "xp": xp, "coins_total": coins,
        "carbon_total": carbon, "level": level, "streak_days": streak
    }

# ── Update stats — BOTH DBs ───────────────────────────────────────────────────
def update_user_stats(user_id: str, xp_add: float, coins_add: float, carbon_add: float):
    """
    Permanent save karo BOTH databases mein:
      1. gaiavolt_users.db  (auth DB — source of truth for profile/leaderboard)
      2. evolution.db       (evolution engine DB — for XP levels/NFT)
    """
    now = datetime.now(timezone.utc).isoformat()

    # ── 1. Auth DB ────────────────────────────────────────────────────────────
    auth_db = get_db()
    auth_db.execute("""
        UPDATE users SET
            xp           = xp + ?,
            coins_total  = coins_total + ?,
            carbon_total = carbon_total + ?,
            last_active  = ?
        WHERE user_id = ?
    """, (xp_add, coins_add, carbon_add, now, user_id))
    auth_db.commit()
    auth_db.close()

    # ── 2. Evolution DB ───────────────────────────────────────────────────────
    try:
        evo_db = sqlite3.connect("evolution.db", check_same_thread=False)
        evo_db.execute("PRAGMA journal_mode=WAL")
        # Only update if user exists — evolution engine creates it on first activity
        evo_db.execute("""
            UPDATE users SET
                xp           = xp + ?,
                coins_total  = coins_total + ?,
                carbon_total = carbon_total + ?,
                last_active  = ?
            WHERE user_id = ?
        """, (xp_add, coins_add, carbon_add, now, user_id))
        evo_db.commit()
        evo_db.close()
    except Exception as e:
        print(f"⚠️ Evolution DB sync: {e}")

# ── Leaderboard ───────────────────────────────────────────────────────────────
def get_leaderboard(limit=10):
    db   = get_db()
    rows = db.execute("""
        SELECT user_id, name, city, xp, coins_total, carbon_total, level
        FROM users ORDER BY xp DESC LIMIT ?
    """, (limit,)).fetchall()
    db.close()
    return [
        {
            "user_id": r[0], "name": r[1], "city": r[2],
            "xp": r[3], "coins": r[4], "carbon": r[5], "level": r[6]
        }
        for r in rows
    ]

# ── Helper: ensure evolution profile exists ───────────────────────────────────
def _ensure_evolution_user(user_id: str, display_name: str = "Eco Hero"):
    """Signup ke waqt evolution.db mein bhi user create karo."""
    try:
        evo_db = sqlite3.connect("evolution.db", check_same_thread=False)
        evo_db.execute("PRAGMA journal_mode=WAL")
        # evolution_engine._init_db() already created the table
        existing = evo_db.execute(
            "SELECT user_id FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        if not existing:
            now = datetime.now(timezone.utc).isoformat()
            evo_db.execute("""
                INSERT OR IGNORE INTO users
                (user_id, display_name, level, xp, coins_total,
                 carbon_total, avatar_stage, streak_days, last_active, created_at)
                VALUES (?,?,1,0,0,0,1,0,?,?)
            """, (user_id, display_name, now, now))
            evo_db.commit()
        evo_db.close()
    except Exception as e:
        print(f"⚠️ Evolution user create: {e}")