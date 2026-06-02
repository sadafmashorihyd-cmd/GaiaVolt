import os
import hashlib
import json
import hmac
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

WORD_LIST = [
    "apple", "bridge", "carbon", "delta", "eagle", "forest", "green",
    "honey", "island", "jungle", "karma", "lemon", "mango", "noble",
    "ocean", "planet", "queen", "river", "solar", "tiger", "ultra",
    "valley", "water", "xenon", "yield", "zenith", "amber", "brave",
    "cloud", "dance", "earth", "flame", "grace", "heart", "ivory",
    "jewel", "kings", "light", "music", "night", "olive", "pearl",
    "quiet", "royal", "storm", "truth", "unity", "viola", "wheat",
    "xerus", "young", "zonal", "azure", "bloom", "coral", "dream",
    "ember", "frost", "globe", "haven", "input", "joker", "knack",
    "lunar", "maple", "nexus", "ozone", "prose", "quest", "radar",
    "shine", "torch", "umbra", "venom", "winds", "exact", "yacht",
    "zesty", "acorn", "bayou", "cedar", "depot", "equip", "fauna",
    "glare", "haste", "index", "jazzy", "kudos", "lilac", "medal",
    "niche", "optic", "pixel", "quilt", "relic", "stone", "tepid"
]

IDENTITY_FILE = 'user_identity.json'
WALLET_FILE   = os.getenv('WALLET_FILE', 'sadaf_wallet.json')


def generate_identity_hash(name, secret_pin):
    combined = f"{name.lower().strip()}:{secret_pin}"
    return hashlib.sha256(combined.encode()).hexdigest()


def generate_recovery_phrase(identity_hash, num_words=12):
    """✅ No duplicate words — BIP-39 style"""
    hash_bytes = bytes.fromhex(identity_hash)
    used_words = set()
    words      = []
    i          = 0

    while len(words) < num_words:
        idx  = (hash_bytes[i % 32] * 256 + hash_bytes[(i+1) % 32]) % len(WORD_LIST)
        word = WORD_LIST[idx]
        if word not in used_words:
            words.append(word)
            used_words.add(word)
        i += 2

    return ' '.join(words)


def verify_recovery_phrase(phrase, identity_hash):
    expected = generate_recovery_phrase(identity_hash)
    return hmac.compare_digest(phrase.strip().lower(), expected)


def create_identity(name, secret_pin):
    print(f"\n{'='*55}")
    print(f"🔐 ECOX IDENTITY CREATION")
    print(f"{'='*55}")

    if os.path.exists(IDENTITY_FILE):
        print(f"⚠️  Identity already exists!")
        print(f"   Use restore_identity() instead")
        return None

    identity_hash   = generate_identity_hash(name, secret_pin)
    recovery_phrase = generate_recovery_phrase(identity_hash)

    identity = {
        "name":          name,
        "identity_hash": identity_hash,
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "version":       "EcoX-1.0"
    }

    with open(IDENTITY_FILE, 'w') as f:
        json.dump(identity, f, indent=4)

    print(f"\n   ✅ Identity created!")
    print(f"   Name: {name}")
    print(f"   Hash: {identity_hash[:16]}...")
    print(f"\n   {'='*45}")
    print(f"   🔑 RECOVERY PHRASE — SAVE THIS SAFELY!")
    print(f"   {'='*45}")
    print(f"\n   {recovery_phrase}\n")
    print(f"   {'='*45}")
    print(f"   ⚠️  Write this down — never share!")
    print(f"{'='*55}\n")

    return identity_hash, recovery_phrase


def restore_identity(recovery_phrase, name, secret_pin):
    print(f"\n{'='*55}")
    print(f"🔄 ECOX IDENTITY RESTORE")
    print(f"{'='*55}")

    identity_hash = generate_identity_hash(name, secret_pin)
    is_valid      = verify_recovery_phrase(recovery_phrase, identity_hash)

    if not is_valid:
        print(f"   ❌ Invalid recovery phrase!")
        return False

    print(f"   ✅ Recovery phrase verified!")
    print(f"   Hash: {identity_hash[:16]}...")

    identity = {
        "name":          name,
        "identity_hash": identity_hash,
        "restored_at":   datetime.now(timezone.utc).isoformat(),
        "version":       "EcoX-1.0"
    }

    with open(IDENTITY_FILE, 'w') as f:
        json.dump(identity, f, indent=4)

    print(f"   ✅ Identity restored!")
    print(f"{'='*55}\n")
    return True


def load_identity():
    if not os.path.exists(IDENTITY_FILE):
        return None
    with open(IDENTITY_FILE, 'r') as f:
        return json.load(f)


def verify_identity(name, secret_pin):
    identity = load_identity()
    if not identity:
        return False, "No identity found!"

    current_hash = generate_identity_hash(name, secret_pin)
    stored_hash  = identity.get('identity_hash', '')

    if not hmac.compare_digest(current_hash, stored_hash):
        return False, "Identity mismatch!"

    return True, f"✅ Identity verified: {identity['name']}"


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"🔐 DAY 11 — IDENTITY SYSTEM TEST")
    print(f"{'='*55}")

    if os.path.exists(IDENTITY_FILE):
        os.remove(IDENTITY_FILE)

    print("\nTest 1: Create identity")
    result = create_identity("Sadaf", "1234")
    if result:
        identity_hash, phrase = result
        # Verify no duplicates
        words = phrase.split()
        assert len(words) == len(set(words)), "Duplicate words found!"
        print(f"   No duplicates: ✅")

    print("\nTest 2: Verify identity")
    ok, msg = verify_identity("Sadaf", "1234")
    print(f"   Result: {msg}")

    print("\nTest 3: Wrong PIN")
    ok, msg = verify_identity("Sadaf", "9999")
    print(f"   Result: {'✅ Blocked!' if not ok else '❌ Should block!'}")

    print("\nTest 4: Restore from phrase")
    if os.path.exists(IDENTITY_FILE):
        os.remove(IDENTITY_FILE)
    restored = restore_identity(phrase, "Sadaf", "1234")
    print(f"   Restored: {'✅' if restored else '❌'}")

    print("\nTest 5: Verify after restore")
    ok, msg = verify_identity("Sadaf", "1234")
    print(f"   Result: {msg}")

    print("\nTest 6: Wrong phrase")
    ok2 = restore_identity("wrong words here test fail check now", "Sadaf", "1234")
    print(f"   Wrong phrase: {'✅ Blocked!' if not ok2 else '❌'}")

    if os.path.exists(IDENTITY_FILE):
        os.remove(IDENTITY_FILE)

    print(f"\n{'='*55}")
    print(f"✅ P26 FIXED: Device independent identity!")
    print(f"✅ P27 FIXED: No duplicate words!")
    print(f"✅ P28 FIXED: Cross-device restore!")
    print(f"{'='*55}\n")