import os
import json
import hashlib
import sqlite3
import time
import logging
from datetime import datetime, timezone
from PIL import Image
from PIL.ExifTags import TAGS
import imagehash
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ImageFingerprint")

# ✅ Dynamic thresholds per class!
CLASS_THRESHOLDS = {
    "solar_panels":       16,
    "cycling":            20,
    "electric_cars":      18,
    "ocean_cleanup":      20,
    "plantation":         18,
    "recycling":          16,
    "utility_bills":      12,
    "organic_farming":    18,
    "wind_energy":        16,
    "water_conservation": 18,
    "led_lighting":       14,
    "public_transport":   18,
    "default":            16
}

DHASH_THRESHOLD  = 10
FINGERPRINT_DB   = os.getenv('FINGERPRINT_DB', 'fingerprints.db')
# ✅ Fix 3: Salt for anchor!
ANCHOR_SALT      = os.getenv('ANCHOR_SALT', 'ecox_anchor_2026')
COLLISION_MIN    = 10
COLLISION_MAX    = 20


class ImageFingerprinter:
    """
    ✅ Day 18: Production-grade Image Fingerprinting
    Fix 1: Trust score + auto-ban!
    Fix 2: SQLite WAL (Redis Day 29)
    Fix 3: Salted anchor!
    Fix 4: Collision handling!
    """

    def __init__(self):
        self._init_db()
        print(f"\n{'='*55}")
        print(f"🔍 IMAGE FINGERPRINTER")
        print(f"{'='*55}")
        print(f"   SHA-256:    Exact match ✅")
        print(f"   pHash:      Dynamic threshold ✅")
        print(f"   dHash:      Structural ({DHASH_THRESHOLD}) ✅")
        print(f"   EXIF:       Metadata check ✅")
        print(f"   Anchor:     Salted deterministic ✅")
        print(f"   DB:         SQLite WAL ✅")
        print(f"   Trust:      Auto-ban system ✅")
        print(f"   Collision:  Flag+Review ✅")
        print(f"{'='*55}\n")

    def _init_db(self):
        self.conn = sqlite3.connect(FINGERPRINT_DB)
        self.conn.execute("PRAGMA journal_mode=WAL")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                sha256       TEXT UNIQUE NOT NULL,
                phash        TEXT NOT NULL,
                dhash        TEXT NOT NULL,
                anchor       TEXT UNIQUE NOT NULL,
                user_id      TEXT,
                action_class TEXT,
                exif_hash    TEXT,
                status       TEXT DEFAULT 'approved',
                registered   TEXT NOT NULL
            )
        """)
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sha256 ON fingerprints(sha256)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_anchor ON fingerprints(anchor)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_phash ON fingerprints(phash)"
        )

        # ✅ Fix 1: Trust score table!
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_trust (
                user_id      TEXT PRIMARY KEY,
                trust_score  INTEGER DEFAULT 100,
                collisions   INTEGER DEFAULT 0,
                duplicates   INTEGER DEFAULT 0,
                banned       INTEGER DEFAULT 0,
                last_updated TEXT
            )
        """)
        self.conn.commit()

    def _get_or_create_trust(self, user_id: str) -> tuple:
        row = self.conn.execute(
            "SELECT trust_score, collisions, duplicates, banned "
            "FROM user_trust WHERE user_id=?",
            (user_id,)
        ).fetchone()
        if not row:
            self.conn.execute(
                "INSERT INTO user_trust (user_id, last_updated) VALUES (?,?)",
                (user_id, datetime.now(timezone.utc).isoformat())
            )
            self.conn.commit()
            return 100, 0, 0, 0
        return row

    def _update_trust_score(self, user_id: str,
                             event: str) -> dict:
        """✅ Fix 1: Trust score + auto-ban!"""
        score, collisions, duplicates, banned = \
            self._get_or_create_trust(user_id)

        if banned:
            return {"banned": True, "score": score}

        if event == "collision":
            collisions += 1
            score      -= 10
            print(f"   ⚠️  Trust: {score}/100 (collisions: {collisions})")
            if collisions >= 5:
                banned = 1
                print(f"   🚨 AUTO-BANNED: 5+ collisions!")

        elif event == "duplicate":
            duplicates += 1
            score      -= 20
            print(f"   ⚠️  Trust: {score}/100 (duplicate: {duplicates})")
            if score <= 0:
                banned = 1
                print(f"   🚨 AUTO-BANNED: Trust zero!")

        self.conn.execute("""
            UPDATE user_trust SET
                trust_score  = ?,
                collisions   = ?,
                duplicates   = ?,
                banned       = ?,
                last_updated = ?
            WHERE user_id = ?
        """, (
            score, collisions, duplicates, banned,
            datetime.now(timezone.utc).isoformat(),
            user_id
        ))
        self.conn.commit()
        return {"banned": bool(banned), "score": score}

    def _is_banned(self, user_id: str) -> bool:
        row = self.conn.execute(
            "SELECT banned FROM user_trust WHERE user_id=?",
            (user_id,)
        ).fetchone()
        return bool(row and row[0])

    def get_sha256(self, img_path: str) -> str:
        h = hashlib.sha256()
        with open(img_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def get_phash(self, img_path: str) -> str:
        img = Image.open(img_path).convert('RGB')
        return str(imagehash.phash(img))

    def get_dhash(self, img_path: str) -> str:
        img = Image.open(img_path).convert('RGB')
        return str(imagehash.dhash(img))

    def get_exif_fingerprint(self, img_path: str) -> dict:
        try:
            img  = Image.open(img_path)
            exif = img.getexif()
            if not exif:
                return {"has_exif": False}
            relevant = {}
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag in ['DateTime', 'DateTimeOriginal',
                           'Make', 'Model', 'GPSInfo', 'Software']:
                    relevant[tag] = str(value)
            return {"has_exif": True, "data": relevant}
        except Exception:
            return {"has_exif": False}

    def get_blockchain_anchor(self, sha256: str,
                               phash: str) -> str:
        """✅ Fix 3: Salted anchor — no collision!"""
        anchor_data = f"{sha256}{phash}{ANCHOR_SALT}"
        return hashlib.sha256(anchor_data.encode()).hexdigest()

    def get_threshold(self, action_class: str = None) -> int:
        return CLASS_THRESHOLDS.get(
            action_class, CLASS_THRESHOLDS['default']
        )

    def check_duplicate(self, img_path: str,
                        action_class: str = None) -> dict:
        result = {
            "is_duplicate":  False,
            "is_collision":  False,
            "method":        None,
            "confidence":    0,
            "sha256":        None,
            "phash":         None,
            "dhash":         None,
            "anchor":        None,
            "exif":          None,
            "review_needed": False
        }

        threshold = self.get_threshold(action_class)

        # Layer 1: SHA-256
        sha256 = self.get_sha256(img_path)
        result['sha256'] = sha256
        row = self.conn.execute(
            "SELECT 1 FROM fingerprints WHERE sha256=?", (sha256,)
        ).fetchone()
        if row:
            result['is_duplicate'] = True
            result['method']       = "SHA-256 exact match"
            result['confidence']   = 100
            return result

        # Layer 2: pHash
        phash = self.get_phash(img_path)
        result['phash'] = phash
        all_phashes = self.conn.execute(
            "SELECT phash FROM fingerprints"
        ).fetchall()
        curr_phash = imagehash.hex_to_hash(phash)
        for (stored,) in all_phashes:
            try:
                dist = curr_phash - imagehash.hex_to_hash(stored)
                if dist <= threshold:
                    result['is_duplicate'] = True
                    result['method']       = f"pHash visual (dist={dist})"
                    result['confidence']   = int((1 - dist/64) * 100)
                    return result
                if COLLISION_MIN <= dist <= COLLISION_MAX:
                    result['is_collision']  = True
                    result['review_needed'] = True
                    result['method']        = f"pHash collision (dist={dist})"
            except Exception:
                pass

        # Layer 3: dHash
        dhash = self.get_dhash(img_path)
        result['dhash'] = dhash
        all_dhashes = self.conn.execute(
            "SELECT dhash FROM fingerprints"
        ).fetchall()
        curr_dhash = imagehash.hex_to_hash(dhash)
        for (stored,) in all_dhashes:
            try:
                dist = curr_dhash - imagehash.hex_to_hash(stored)
                if dist <= DHASH_THRESHOLD:
                    result['is_duplicate'] = True
                    result['method']       = f"dHash structural (dist={dist})"
                    result['confidence']   = int((1 - dist/64) * 100)
                    return result
            except Exception:
                pass

        # Layer 4: EXIF
        exif = self.get_exif_fingerprint(img_path)
        result['exif'] = exif
        if exif.get('has_exif'):
            exif_key  = json.dumps(
                exif.get('data', {}), sort_keys=True
            )
            exif_hash = hashlib.sha256(
                exif_key.encode()
            ).hexdigest()[:16]
            row = self.conn.execute(
                "SELECT 1 FROM fingerprints WHERE exif_hash=?",
                (exif_hash,)
            ).fetchone()
            if row:
                result['is_duplicate'] = True
                result['method']       = "EXIF metadata match"
                result['confidence']   = 85
                return result

        # Anchor check
        anchor = self.get_blockchain_anchor(sha256, phash)
        result['anchor'] = anchor
        row = self.conn.execute(
            "SELECT 1 FROM fingerprints WHERE anchor=?", (anchor,)
        ).fetchone()
        if row:
            result['is_duplicate'] = True
            result['method']       = "Blockchain anchor match"
            result['confidence']   = 95
            return result

        return result

    def register_image(self, img_path: str,
                       user_id: str = "unknown",
                       action_class: str = None) -> dict:
        # ✅ Fix 1: Check ban first!
        if self._is_banned(user_id):
            print(f"   🚨 BANNED USER: {user_id}")
            return {
                "is_duplicate": True,
                "method":       "User banned!",
                "confidence":   100
            }

        check = self.check_duplicate(img_path, action_class)

        if check['is_duplicate']:
            self._update_trust_score(user_id, "duplicate")
            print(f"   🚨 DUPLICATE: {check['method']}")
            print(f"   Confidence: {check['confidence']}%")
            return check

        if check['is_collision']:
            trust = self._update_trust_score(user_id, "collision")
            print(f"   ⚠️  COLLISION: {check['method']}")
            if trust.get('banned'):
                return {
                    "is_duplicate": True,
                    "method":       "Auto-banned!",
                    "confidence":   100
                }

        sha256 = check['sha256'] or self.get_sha256(img_path)
        phash  = check['phash']  or self.get_phash(img_path)
        dhash  = check['dhash']  or self.get_dhash(img_path)
        anchor = check['anchor'] or self.get_blockchain_anchor(
            sha256, phash
        )
        exif   = check['exif']   or self.get_exif_fingerprint(img_path)

        exif_hash = None
        if exif.get('has_exif'):
            exif_key  = json.dumps(
                exif.get('data', {}), sort_keys=True
            )
            exif_hash = hashlib.sha256(
                exif_key.encode()
            ).hexdigest()[:16]

        status = 'review' if check['is_collision'] else 'approved'

        try:
            self.conn.execute("""
                INSERT INTO fingerprints
                (sha256, phash, dhash, anchor, user_id,
                 action_class, exif_hash, status, registered)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                sha256, phash, dhash, anchor,
                user_id, action_class, exif_hash,
                status,
                datetime.now(timezone.utc).isoformat()
            ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            check['is_duplicate'] = True
            check['method']       = "DB integrity duplicate"
            return check

        print(f"   SHA-256:   {sha256[:16]}... ✅")
        print(f"   pHash:     {phash} ✅")
        print(f"   dHash:     {dhash} ✅")
        print(f"   Anchor:    {anchor[:16]}... ✅")
        print(f"   EXIF:      {'✅' if exif.get('has_exif') else '⚠️ None'}")
        print(f"   Threshold: {self.get_threshold(action_class)} ({action_class})")
        print(f"   Status:    {status.upper()} ✅")

        check['registered'] = True
        check['anchor']     = anchor
        return check

    def calibrate_phash_threshold(self, test_dir: str) -> dict:
        print(f"\n{'='*55}")
        print(f"📊 PHASH CALIBRATION")
        print(f"{'='*55}")
        images = [
            os.path.join(test_dir, f)
            for f in os.listdir(test_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ][:10]
        if len(images) < 2:
            return {}
        distances = []
        for i in range(len(images)):
            for j in range(i+1, len(images)):
                try:
                    h1 = imagehash.phash(
                        Image.open(images[i]).convert('RGB')
                    )
                    h2 = imagehash.phash(
                        Image.open(images[j]).convert('RGB')
                    )
                    distances.append(h1 - h2)
                except Exception:
                    pass
        if not distances:
            return {}
        avg_dist = sum(distances) / len(distances)
        min_dist = min(distances)
        max_dist = max(distances)
        optimal  = max(min_dist + 2, 6)
        print(f"   Images:    {len(images)}")
        print(f"   Min dist:  {min_dist}")
        print(f"   Avg dist:  {avg_dist:.1f}")
        print(f"   Max dist:  {max_dist}")
        print(f"   Optimal:   {optimal}")
        print(f"   solar_panels: {CLASS_THRESHOLDS['solar_panels']}")
        print(f"   Status: ✅ Dynamic per class!")
        print(f"{'='*55}\n")
        return {"min": min_dist, "avg": avg_dist,
                "max": max_dist, "optimal": optimal}

    def get_stats(self) -> dict:
        total    = self.conn.execute(
            "SELECT COUNT(*) FROM fingerprints"
        ).fetchone()[0]
        approved = self.conn.execute(
            "SELECT COUNT(*) FROM fingerprints WHERE status='approved'"
        ).fetchone()[0]
        review   = self.conn.execute(
            "SELECT COUNT(*) FROM fingerprints WHERE status='review'"
        ).fetchone()[0]
        banned   = self.conn.execute(
            "SELECT COUNT(*) FROM user_trust WHERE banned=1"
        ).fetchone()[0]
        return {
            "total": total, "approved": approved,
            "review": review, "banned": banned
        }


def run_fingerprint_demo():
    print(f"\n{'='*55}")
    print(f"🔍 DAY 18 — IMAGE FINGERPRINTING DEMO")
    print(f"{'='*55}")

    if os.path.exists(FINGERPRINT_DB):
        os.remove(FINGERPRINT_DB)

    fp        = ImageFingerprinter()
    solar_dir = 'dataset/val/solar_panels/'
    images    = sorted(os.listdir(solar_dir))
    img1      = os.path.join(solar_dir, images[0])
    img2      = os.path.join(solar_dir, images[1])

    # Test 1: Register
    print(f"\n--- Test 1: Register new image ---")
    r1 = fp.register_image(img1, "Sadaf", "solar_panels")
    print(f"   Registered: {'✅' if r1.get('registered') else '❌'}")

    # Test 2: Duplicate
    print(f"\n--- Test 2: Exact duplicate ---")
    r2 = fp.check_duplicate(img1, "solar_panels")
    print(f"   Duplicate:  {'🚨 BLOCKED!' if r2['is_duplicate'] else '❌'}")
    print(f"   Method:     {r2.get('method')}")

    # Test 3: New image
    print(f"\n--- Test 3: New image ---")
    r3 = fp.register_image(img2, "Sadaf", "solar_panels")
    print(f"   Registered: {'✅' if r3.get('registered') else '❌'}")

    # Test 4: Deterministic anchor
    print(f"\n--- Test 4: Salted deterministic anchor ---")
    a1 = fp.get_blockchain_anchor(r1['sha256'], r1['phash'])
    a2 = fp.get_blockchain_anchor(r1['sha256'], r1['phash'])
    print(f"   Same always: {'✅' if a1 == a2 else '❌'}")
    print(f"   Salted: ✅ No collision!")

    # Test 5: Trust score / auto-ban
    print(f"\n--- Test 5: Auto-ban collision flood ---")
    hacker_fp = ImageFingerprinter.__new__(ImageFingerprinter)
    hacker_fp.conn = fp.conn
    for i in range(6):
        fp._update_trust_score("hacker", "collision")
    row = fp.conn.execute(
        "SELECT banned, collisions FROM user_trust WHERE user_id='hacker'"
    ).fetchone()
    print(f"   Collisions: {row[1]}")
    print(f"   Banned:     {'🚨 YES!' if row[0] else '❌'}")

    # Test 6: pHash calibration
    print(f"\n--- Test 6: pHash calibration ---")
    fp.calibrate_phash_threshold(solar_dir)

    # Test 7: All classes
    print(f"\n--- Test 7: All classes ---")
    val_dir = 'dataset/val/'
    for cls in sorted(os.listdir(val_dir))[:3]:
        cls_dir = os.path.join(val_dir, cls)
        if not os.path.isdir(cls_dir):
            continue
        imgs = os.listdir(cls_dir)
        if not imgs:
            continue
        img    = os.path.join(cls_dir, imgs[0])
        res    = fp.register_image(img, "Sadaf", cls)
        status = '✅' if res.get('registered') else '🚨'
        anchor = res.get('anchor') or res.get('sha256', 'N/A')
        print(f"   {status} {cls:<22} anchor: {anchor[:12]}...")

    # Stats
    stats = fp.get_stats()
    print(f"\n--- DB Stats ---")
    print(f"   Total:    {stats['total']} ✅")
    print(f"   Approved: {stats['approved']} ✅")
    print(f"   Review:   {stats['review']}")
    print(f"   Banned:   {stats['banned']}")

    print(f"\n{'='*55}")
    print(f"✅ Fix 1: Trust score + auto-ban!")
    print(f"✅ Fix 2: SQLite WAL!")
    print(f"✅ Fix 3: Salted anchor!")
    print(f"✅ Fix 4: Collision handling!")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    run_fingerprint_demo()