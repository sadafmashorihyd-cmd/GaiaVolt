import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import json
import time
import hashlib
import cv2
import imagehash
from PIL import Image
from datetime import datetime, timezone
from dotenv import load_dotenv
from tensorflow.keras.applications.efficientnet import preprocess_input
from src.utils.constants import CONFIG
from anti_cheat import EcoXShield
from geo_fence import check_geo_fence
from src.utils.spoof_detector import detect_spoof
from user_identity import load_identity
from edge_predictor import EdgePredictor

load_dotenv()

DB_FILE         = os.getenv('WALLET_FILE', 'sadaf_wallet.json')
PHASH_THRESHOLD = 10

reward_points = {
    "ocean_cleanup":      100,
    "solar_panels":        50,
    "plantation":          40,
    "electric_cars":       60,
    "cycling":             20,
    "recycling":           30,
    "utility_bills":       25,
    "organic_farming":     45,
    "wind_energy":         80,
    "water_conservation":  35,
    "led_lighting":        15,
    "public_transport":    10
}

shield          = EcoXShield()
_edge_predictor = None


def get_edge_predictor():
    """✅ Day 12: TFLite predictor — cached"""
    global _edge_predictor
    if _edge_predictor is None:
        _edge_predictor = EdgePredictor()
    return _edge_predictor


def get_sha256(img_path):
    sha256 = hashlib.sha256()
    with open(img_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_phash(img_path):
    img = Image.open(img_path).convert('RGB')
    return str(imagehash.phash(img))


def is_duplicate(img_path, wallet):
    sha256 = get_sha256(img_path)
    phash  = get_phash(img_path)

    if sha256 in wallet.get("processed_hashes", []):
        return True, "Exact duplicate!", sha256, phash

    stored_phashes = wallet.get("processed_phashes", [])
    current_phash  = imagehash.hex_to_hash(phash)

    for stored in stored_phashes:
        stored_hash = imagehash.hex_to_hash(stored)
        distance    = current_phash - stored_hash
        if distance <= PHASH_THRESHOLD:
            return True, f"Visually similar (distance={distance})!", sha256, phash

    return False, "New image", sha256, phash


def load_wallet():
    default = {
        "balance":           0,
        "history":           [],
        "processed_hashes":  [],
        "processed_phashes": [],
        "identity_hash":     ""
    }
    if not os.path.exists(DB_FILE):
        return default
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict) or "balance" not in data:
            return default
        if "processed_hashes"  not in data:
            data["processed_hashes"]  = []
        if "processed_phashes" not in data:
            data["processed_phashes"] = []
        if "identity_hash"     not in data:
            data["identity_hash"]     = ""
        return data
    except:
        return default


def save_wallet(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def link_wallet_to_identity(wallet, identity_hash):
    if not wallet.get("identity_hash"):
        wallet["identity_hash"] = identity_hash
        print(f"   Wallet linked to identity ✅")
    elif wallet["identity_hash"] != identity_hash:
        return False, "❌ Wallet belongs to different identity!"
    return True, "✅ Identity matches wallet"


def verify_and_reward(img_path, lat=None, lon=None):
    print(f"\n{'='*60}")
    print(f"🌐 EcoX — Verifying: {os.path.basename(img_path)}")
    print(f"{'='*60}")

    if not os.path.exists(img_path):
        print(f"❌ Image not found!")
        return False

    # 1. Identity check
    identity = load_identity()
    if identity is None:
        print(f"❌ No identity found!")
        print(f"   Run: python user_identity.py first!")
        return False
    print(f"   Identity: ✅ {identity['name']}")

    # 2. 3-Layer Spoof check
    if not detect_spoof(img_path):
        print("🚨 FRAUD: Screen/spoof detected!")
        return False
    print(f"   Liveness: ✅ Authentic!")

    # 3. Geo-fence check
    user_id = os.getenv('REGISTERED_USER', 'user')
    gps_lat = lat or float(os.getenv('DEFAULT_LAT', '24.8607'))
    gps_lon = lon or float(os.getenv('DEFAULT_LON', '67.0011'))

    geo_ok, geo_msg = check_geo_fence(user_id, gps_lat, gps_lon)
    if not geo_ok:
        print(f"🚨 GEO-FENCE: {geo_msg}")
        return False

    # 4. Wallet identity link
    wallet = load_wallet()
    link_ok, link_msg = link_wallet_to_identity(
        wallet, identity['identity_hash']
    )
    if not link_ok:
        print(f"🚨 {link_msg}")
        return False
    print(f"   Wallet:   {link_msg}")

    # 5. Duplicate check
    is_dup, reason, sha256, phash = is_duplicate(img_path, wallet)
    if is_dup:
        print(f"🚨 DUPLICATE: {reason}")
        print(f"   SHA-256: {sha256[:16]}...")
        return False

    print(f"   SHA-256: {sha256[:16]}... ✅")
    print(f"   pHash:   {phash} ✅")

    # ✅ 6. Day 12: TFLite offline prediction!
    edge       = get_edge_predictor()
    result, _, score, ms = edge.predict(img_path)

    if result is None:
        print("❌ Prediction failed!")
        return False

    print(f"   Detected: {result} ({score:.1f}%) [{ms:.1f}ms] ⚡")
    print(f"   Engine:   TFLite OFFLINE ✅")

    if score < 70:
        print(f"❌ Low confidence: {score:.1f}%")
        return False

    # 7. Reward
    points = reward_points.get(result, 0)
    wallet['balance'] += points
    wallet['history'].append({
        "action":    result,
        "reward":    points,
        "match":     f"{score:.2f}%",
        "latency_ms": round(ms, 2),
        "timestamp": time.time(),
        "date":      datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    })
    wallet['processed_hashes'].append(sha256)
    wallet['processed_phashes'].append(phash)
    save_wallet(wallet)

    print(f"\n✅ +{points} Eco-Coins minted!")
    print(f"💰 Balance: {wallet['balance']} Eco-Coins")
    print(f"{'='*60}\n")
    return True


if __name__ == "__main__":
    # Clean for fresh test
    if os.path.exists('geo_fence_log.json'):
        os.remove('geo_fence_log.json')
    if os.path.exists('user_identity.json'):
        os.remove('user_identity.json')

    wallet_reset = {
        'balance': 245, 'history': [],
        'processed_hashes': [], 'processed_phashes': [],
        'identity_hash': ''
    }
    with open('sadaf_wallet.json', 'w') as f:
        json.dump(wallet_reset, f, indent=4)

    from user_identity import create_identity
    create_identity("Sadaf", "1234")

    solar_dir   = 'dataset/val/solar_panels/'
    images      = os.listdir(solar_dir)
    test_image  = os.path.join(solar_dir, images[0])
    test_image2 = os.path.join(solar_dir, images[1])

    print("TEST 1: Real image")
    verify_and_reward(test_image, lat=24.8607, lon=67.0011)

    print("TEST 2: Duplicate")
    verify_and_reward(test_image, lat=24.8607, lon=67.0011)

    print("TEST 3: Different image")
    verify_and_reward(test_image2, lat=24.8650, lon=67.0050)

    print("TEST 4: Fake/spoof")
    fake_img = 'test_fake.jpg'
    fake     = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.imwrite(fake_img, fake)
    verify_and_reward(fake_img, lat=24.8800, lon=67.0200)
    if os.path.exists(fake_img):
        os.remove(fake_img)

    if os.path.exists('user_identity.json'):
        os.remove('user_identity.json')

    print("\n✅ Day 12: TFLite Offline Engine VERIFIED!")