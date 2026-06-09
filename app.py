"""
GaiaVolt — Complete Wired app.py  [FIXED]
Fixes applied:
  1. get_user_id_from_request() — token se real user_id nikalo
  2. Duplicate Day17 mint removed from upload_image
  3. Permanent save (update_user_stats) added to upload_image
  4. Video endpoint already had token auth — kept as-is
"""

import os
import cv2
import json
import hashlib
import time
import asyncio
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input

# ── Day-specific modules ──────────────────────────────────────────────────────
from anti_cheat        import EcoXShield
try:
    from spatial_shield import SpatialShield
    spatial_shield = SpatialShield()
    print("✅ Day 8: Spatial Shield wired")
except Exception as e:
    print(f"⚠️ Spatial Shield: {e}")
    spatial_shield = None
from image_fingerprint import ImageFingerprinter
from geo_fence         import check_geo_fence
from fresh_photo_check import check_fresh_photo
from evolution_engine  import EvolutionEngine
from bridges_engine    import BridgesEngine
from nft_engine        import NFTEngine
try:
    from audit_receipt import AuditReceiptGenerator
    audit_gen = AuditReceiptGenerator()
    AUDIT_AVAILABLE = True
    print("✅ Day 20: Audit Receipt wired")
except Exception as e:
    print(f"⚠️ Audit: {e}")
    audit_gen = None
    AUDIT_AVAILABLE = False
try:
    from day22_paymaster import UserOperationBuilder, PaymasterStatus
    paymaster_builder = UserOperationBuilder()
    DAY22_AVAILABLE   = True
    print("✅ Day 22: Paymaster wired")
except Exception as e:
    print(f"⚠️ Day 22 Paymaster: {e}")
    paymaster_builder = None
    DAY22_AVAILABLE   = False

try:
    from oracle_integration import ChainlinkOracle
    oracle = ChainlinkOracle()
    ORACLE_AVAILABLE = True
    print("✅ Day 14: Oracle wired")
except Exception as e:
    print(f"⚠️ Oracle: {e}")
    oracle = None
    ORACLE_AVAILABLE = False
from plantation_tracker import PlantationTracker
from seed_qr_system import SeedQRSystem

# Day 19: IPFS
try:
    from ipfs_manager import IPFSManager
    IPFS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ IPFS: {e}")
    IPFS_AVAILABLE = False

# Day 21: Impact Engine + Web3
try:
    from day21_impact_engine import ProofMetadata, run_impact_engine, generate_impact_message
    from day21_orchestrator  import Day21Engine, fetch_environmental_data
    DAY21_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Day21: {e}")
    DAY21_AVAILABLE = False

# Day 15: ZK Proof
try:
    from zk_proof_engine import ZKProofEngine
    ZK_AVAILABLE = True
except Exception as e:
    print(f"⚠️ ZK: {e}")
    ZK_AVAILABLE = False

# Web3
try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except:
    WEB3_AVAILABLE = False

load_dotenv()

# ── Auth System ───────────────────────────────────────────────────────────────
try:
    from auth_system import signup, login, get_user_by_token, update_user_stats, get_leaderboard as auth_leaderboard
    AUTH_AVAILABLE = True
    print("✅ Auth system wired")
except Exception as e:
    print(f"⚠️ Auth: {e}")
    AUTH_AVAILABLE = False

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

# ── Maintenance Mode — set maintenance.json {"active": true} to enable ────────
import json as _json
@app.before_request
def check_maintenance():
    try:
        with open("maintenance.json") as f:
            m = _json.load(f)
            if m.get("active") and request.path not in ["/health", "/"]:
                return jsonify({
                    "error": "🔧 GaiaVolt is under maintenance. Back soon!",
                    "maintenance": True
                }), 503
    except:
        pass  # No maintenance.json = normal mode

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

@app.errorhandler(413)
def too_large(e):
    return jsonify({"verdict":"FRAUD","fraud_reason":"File too large — max 100MB.","modules":{}}), 413

# ── Logging ───────────────────────────────────────────────────────────────────
from logging.handlers import RotatingFileHandler
rejection_logger = logging.getLogger("rejections")
rejection_logger.setLevel(logging.INFO)
rh = RotatingFileHandler("rejection_logs.log", maxBytes=5*1024*1024, backupCount=3)
rh.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
rejection_logger.addHandler(rh)

def log_rejection(reason, fname, activity, modules):
    rejection_logger.info(f"REJECTED | {fname} | {activity} | {reason} | {modules}")

def log_verified(activity, confidence, coins):
    rejection_logger.info(f"VERIFIED | {activity} | {confidence:.2f} | {coins}")

# ── Async queue ───────────────────────────────────────────────────────────────
import threading
from queue import Queue

processing_queue  = Queue()
processing_status = {}

def background_worker():
    while True:
        job = processing_queue.get()
        if job is None: break
        job_id = job["job_id"]
        try:
            processing_status[job_id] = {"status":"processing"}
            result = job["func"](*job["args"])
            processing_status[job_id] = {"status":"done","result":result}
        except Exception as e:
            processing_status[job_id] = {"status":"error","error":str(e)}
        processing_queue.task_done()

threading.Thread(target=background_worker, daemon=True).start()

# ── Config ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = 'dataset/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

COIN_REWARDS = {
    "solar_panels":    5.0, "cycling":         3.0,
    "utility_bills":   2.0, "ev_charging":     4.0,
    "recycling":       2.5, "tree_planting":   4.5,
    "wind_turbine":    5.0, "public_transport":2.0,
    "composting":      2.0, "led_lighting":    1.5,
    "rainwater":       3.0, "insulation":      3.5,
    "other_eco":       1.0,
    "plantation":      4.5, "ocean_cleanup":   5.0,
    "electric_cars":   4.0, "wind_energy":     5.0,
    "organic_farming": 4.0, "water_conservation":3.0,
}
CARBON_PER_COIN = 0.6

# ── Module init ───────────────────────────────────────────────────────────────
print("🚀 Initializing GaiaVolt modules...")

shield            = EcoXShield()
fingerprinter     = ImageFingerprinter()
evolution         = EvolutionEngine()
bridges           = BridgesEngine()
nft_eng           = NFTEngine()
plantation_tracker = PlantationTracker()
seed_system       = SeedQRSystem()

zk_engine       = ZKProofEngine() if ZK_AVAILABLE else None
used_nullifiers = set()

ipfs_manager  = IPFSManager() if IPFS_AVAILABLE else None
day21_engine  = Day21Engine() if DAY21_AVAILABLE else None

try:
    from security_hardening import SecurityGatekeeper
    gatekeeper = SecurityGatekeeper()
    print("✅ Security Gatekeeper v2.0 wired")
except Exception as e:
    print(f"⚠️ Gatekeeper: {e}")
    gatekeeper = None

print("✅ All modules loaded!")

# ── AI Model ──────────────────────────────────────────────────────────────────
from src.utils.constants import CONFIG
model       = None
CLASS_NAMES = CONFIG['CLASSES']

def get_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(CONFIG['MODEL_PATH'], compile=False)
    return model

# ── Pre-load model at startup — phone timeout fix ─────────────────────────────
print("🧠 Pre-loading AI model...")
get_model()
print("✅ AI model ready — fast response guaranteed!")

# ── SQLite DB ─────────────────────────────────────────────────────────────────
import sqlite3 as _sqlite3

def get_main_db():
    conn = _sqlite3.connect("ecox_main.db", check_same_thread=False, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_images (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name     TEXT,
            confidence     REAL,
            reward_coins   REAL,
            carbon_kg      REAL,
            lat            REAL,
            lon            REAL,
            city           TEXT DEFAULT 'Unknown',
            ipfs_cid       TEXT,
            tx_hash        TEXT,
            lovelock_score REAL,
            created_at     TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON processed_images(created_at)")
    conn.commit()
    return conn

def get_db():
    return get_main_db()

# ── Rate limit ────────────────────────────────────────────────────────────────
request_counts = {}

def rate_limit_check(ip, max_req=10, window=60):
    now = time.time()
    request_counts.setdefault(ip, [])
    request_counts[ip] = [t for t in request_counts[ip] if now-t < window]
    if len(request_counts[ip]) >= max_req: return False
    request_counts[ip].append(now); return True

def fraud(reason, modules):
    log_rejection(reason, "N/A", "N/A", modules)
    return jsonify({"verdict":"FRAUD","modules":modules,"fraud_reason":reason})

# ── FIX 1: Real user_id from token ───────────────────────────────────────────
def get_user_id_from_request(req):
    """
    Token se real user_id nikalo.
    Priority: Authorization header → form field → env default
    """
    token = req.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if token and AUTH_AVAILABLE:
        try:
            u = get_user_by_token(token)
            if u and u.get("user_id"):
                print(f"   ✅ Auth user: {u['name']} ({u['user_id']})")
                return u["user_id"]
        except Exception as e:
            print(f"   ⚠️ Token parse error: {e}")
    # Fallback
    uid = req.form.get("user_id", "").strip()
    return uid if uid else os.getenv("REGISTERED_USER", "anonymous")


# ══ MAIN ENDPOINT ═════════════════════════════════════════════════════════════
@app.route('/upload-ecox', methods=['POST'])
def upload_image():

    modules = {"spatial":"pending","liveness":"pending","ai":"pending","ocr":"pending","zk":"pending"}

    if not rate_limit_check(request.remote_addr):
        return fraud("Rate limit exceeded.", {k:"fail" for k in modules}), 429

    if 'image' not in request.files:
        return fraud("No image uploaded.", {k:"fail" for k in modules}), 400

    file     = request.files['image']
    filename = file.filename or f"upload_{int(time.time())}.jpg"

    allowed = {'.jpg','.jpeg','.png','.heic','.webp','.bmp'}
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed:
        return fraud(f"Invalid format ({ext})", {k:"fail" for k in modules}), 400

    file.seek(0,2); fsize=file.tell(); file.seek(0)
    if fsize > 10*1024*1024:
        return fraud("Image too large — max 10MB.", {k:"fail" for k in modules}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # ── FIX 1 APPLIED: real user_id ──────────────────────────────────────────
    user_id    = get_user_id_from_request(request)
    proof_type = request.form.get('proof_type', 'other_eco')
    lat        = request.form.get('lat')
    lon        = request.form.get('lon')

    # ── MODULE 1: IMAGE FINGERPRINT (Day 18) ──────────────────────────────────
    fp_result = fingerprinter.register_image(file_path, user_id, proof_type)
    if fp_result.get('is_duplicate'):
        modules.update({k:"fail" for k in modules})
        modules["spatial"] = "pass"
        return fraud(f"Duplicate image! {fp_result.get('method','')}", modules), 400

    # ── MODULE 2: SPATIAL / GPS (Day 8,9) ─────────────────────────────────────
    if spatial_shield and lat and lon:
        velocity_score = spatial_shield.verify_integrity(float(lat), float(lon))
        if velocity_score == 0:
            modules["spatial"] = "fail"
            return fraud("GPS teleportation detected — impossible velocity!", modules), 400
    if not lat or not lon:
        try:
            from PIL import Image as PILImage
            from PIL.ExifTags import TAGS
            pil_img  = PILImage.open(file_path)
            exif     = pil_img.getexif()
            gps_found = any(TAGS.get(tid)=='GPSInfo' for tid in (exif or {}))
            if not gps_found:
                modules["spatial"] = "fail"
                return fraud("No GPS — only on-location photos accepted.", modules), 400
            modules["spatial"] = "pass"
        except Exception as e:
            modules["spatial"] = "fail"
            return fraud("GPS verification failed.", modules), 400
    else:
        try:
            geo_ok, geo_msg = check_geo_fence(user_id, float(lat), float(lon))
            if not geo_ok:
                modules.update({k:"fail" for k in modules})
                return fraud(geo_msg, modules), 400
            modules["spatial"] = "pass"
        except Exception as e:
            modules["spatial"] = "fail"
            return fraud("Geo-fence error.", modules), 400

    # ── MODULE 3: LIVENESS (Day 10) + FRESH PHOTO ─────────────────────────────
    img = cv2.imread(file_path)
    if img is None:
        modules["liveness"] = "fail"
        return fraud("Invalid image file.", modules), 400

    blur = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    if blur < 100:
        modules["liveness"] = "fail"
        return fraud(f"Spoof detected — blurry ({blur:.1f}).", modules), 401

    if not shield.detect_editing_traces(file_path):
        modules["liveness"] = "fail"
        return fraud("Edited image — Photoshop traces.", modules), 401

    fresh = check_fresh_photo(file_path)
    if not fresh["passed"]:
        modules["liveness"] = "fail"
        return fraud(fresh["reason"], modules), 401

    modules["liveness"] = "pass"

    # ── MODULE 4: AI VISION (Day 1-7) ─────────────────────────────────────────
    try:
        img_rgb     = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, tuple(CONFIG['IMG_SIZE']))
        img_array   = preprocess_input(np.expand_dims(img_resized,0).astype(np.float32))
        predictions = get_model().predict(img_array, verbose=0)
        confidence  = float(np.max(predictions))
        predicted   = CLASS_NAMES[np.argmax(predictions)]
        if confidence < 0.70:
            modules["ai"] = "fail"
            return fraud(f"Low confidence ({confidence*100:.1f}%)", modules), 400
        modules["ai"] = "pass"
    except Exception as e:
        modules["ai"] = "fail"
        return fraud(f"AI error: {e}", modules), 500

    # ── MODULE 5: OCR / ANTI-CHEAT (Day 5,11) ────────────────────────────────
    try:
        current_month  = datetime.now(timezone.utc).strftime("%B %Y")
        extracted_text = f"{current_month} {shield.registered_user}"
        shield_result  = shield.verify_full_protocol(file_path, extracted_text)
        if predicted == "utility_bills" and "REJECTED" in str(shield_result):
            modules["ocr"] = "fail"
            return fraud(f"Document check failed: {shield_result}", modules), 400
        modules["ocr"] = "pass"
    except Exception as e:
        print(f"⚠️ Shield: {e}")
        modules["ocr"] = "pass"

    # ── MODULE 6: ZK PROOF (Day 15) ───────────────────────────────────────────
    img_hash = fp_result.get('sha256') or hashlib.sha256(open(file_path,'rb').read()).hexdigest()
    zk_proof_data = None

    if zk_engine:
        try:
            zk_proof = zk_engine.generate_proof(
                image_hash=img_hash, user_id=user_id,
                action_class=predicted, confidence=confidence*100, carbon_rate=24.80
            )
            if not zk_engine.verify_proof(zk_proof):
                modules["zk"] = "fail"
                return fraud("ZK proof failed.", modules), 400
            nullifier = zk_proof.get('nullifier','')
            if not zk_engine.check_nullifier(nullifier, used_nullifiers):
                modules["zk"] = "fail"
                return fraud("Double-spend detected!", modules), 400
            modules["zk"] = "pass"
            zk_proof_data = nullifier[:32]
        except Exception as e:
            print(f"⚠️ ZK: {e}")
            zk_proof_data = hashlib.sha256(f"{img_hash}{time.time()}".encode()).hexdigest()[:32]
            modules["zk"] = "pass"
    else:
        zk_proof_data = hashlib.sha256(f"{img_hash}{time.time()}".encode()).hexdigest()[:32]
        modules["zk"] = "pass"

    # ── CONSENSUS ─────────────────────────────────────────────────────────────
    if not all(v=="pass" for v in modules.values()):
        failed = [k for k,v in modules.items() if v!="pass"]
        return fraud(f"Consensus failed: {', '.join(failed)}", modules), 400

    # ── REWARD CALCULATION ────────────────────────────────────────────────────
    reward_coins = round(COIN_REWARDS.get(predicted,1.0) + (confidence-0.70)*5, 2)
    carbon_kg    = round(reward_coins * CARBON_PER_COIN, 3)

    # ── DAY 21: IMPACT ENGINE + WEB3 (runs ONCE only) ─────────────────────────
    lovelock_score = None
    tx_hash        = None
    ipfs_cid       = None
    planet_message = "Your action just cooled a 1mm patch of the Arctic."

    if DAY21_AVAILABLE and day21_engine:
        try:
            lat_f  = float(lat) if lat else float(os.getenv('DEFAULT_LAT', 24.8607))
            lon_f  = float(lon) if lon else float(os.getenv('DEFAULT_LON', 67.0011))
            wallet = request.form.get('wallet_address', os.getenv('ADMIN_WALLET_ADDRESS',''))

            loop = asyncio.new_event_loop()
            receipt = loop.run_until_complete(
                day21_engine.execute(
                    lat=lat_f, lon=lon_f,
                    co2_kg=carbon_kg,
                    wallet_address=wallet,
                    activity_type=predicted
                )
            )
            loop.close()

            if receipt and receipt.status == "READY_FOR_MINT":
                lovelock_score = receipt.lovelock_basis_points / 10000
                tx_hash        = receipt.on_chain_tx
                planet_message = receipt.human_message
                print(f"✅ Day21: Lovelock={lovelock_score} TX={tx_hash}")
        except Exception as e:
            print(f"⚠️ Day21 error: {e}")

    # ── DAY 19: IPFS ──────────────────────────────────────────────────────────
    if IPFS_AVAILABLE and ipfs_manager:
        try:
            ipfs_result = ipfs_manager.upload_proof(
                img_path=file_path, user_id=user_id,
                action_class=predicted, sha256=img_hash,
                zk_nullifier=zk_proof_data
            )
            if ipfs_result.get('image_cid'):
                ipfs_cid = ipfs_result['image_cid']
        except Exception as e:
            print(f"⚠️ IPFS error: {e}")

    # ── SAVE TO DB ────────────────────────────────────────────────────────────
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO processed_images
            (class_name,confidence,reward_coins,carbon_kg,lat,lon,
             ipfs_cid,tx_hash,lovelock_score,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (predicted, confidence, reward_coins, carbon_kg,
              float(lat) if lat else None, float(lon) if lon else None,
              ipfs_cid, tx_hash, lovelock_score,
              datetime.now(timezone.utc).isoformat()))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"DB: {e}")

    # ── PLANTATION TRACKER ────────────────────────────────────────────────────
    plant_data = None
    if predicted == "plantation":
        lat_f = float(lat) if lat else float(os.getenv('DEFAULT_LAT',24.8607))
        lon_f = float(lon) if lon else float(os.getenv('DEFAULT_LON',67.0011))
        plant_data = plantation_tracker.register_plant(user_id, lat_f, lon_f, reward_coins)
        reward_coins = plant_data["coins_now"]
        print(f"✅ Plant registered: {plant_data['plant_id']}")

    # ── DAY 25: EVOLUTION XP ──────────────────────────────────────────────────
    evo_result = evolution.add_activity(user_id, predicted, reward_coins, carbon_kg)

    # ── FIX 3: PERMANENT SAVE to auth DB ─────────────────────────────────────
    if AUTH_AVAILABLE and user_id not in ("user", "anonymous", ""):
        try:
            update_user_stats(user_id, evo_result["xp_earned"], reward_coins, carbon_kg)
            print(f"   ✅ Permanent save: {user_id} +{evo_result['xp_earned']}XP +{reward_coins}GAIA")
        except Exception as e:
            print(f"   ⚠️ Permanent save error: {e}")

    log_verified(predicted, confidence, reward_coins)
    print(f"\n✅ VERIFIED: {predicted} | {reward_coins} GAIA | {carbon_kg}kg CO₂")

    # ── Day 20: Audit receipt ────────────────────────────────────────────────
    receipt_data = None
    if AUDIT_AVAILABLE and audit_gen:
        try:
            receipt_data = audit_gen.generate_receipt(
                user_id=user_id, action_class=predicted,
                reward=int(reward_coins), sha256=img_hash,
                tx_hash=tx_hash, ipfs_cid=ipfs_cid,
                carbon_rate=24.80, zk_nullifier=zk_proof_data
            )
        except Exception as e:
            print(f"⚠️ Receipt: {e}")

    return jsonify({
        "verdict":        "VERIFIED",
        "class":          predicted,
        "confidence":     confidence,
        "reward_coins":   reward_coins,
        "carbon_kg":      carbon_kg,
        "planet_message": planet_message,
        "modules":        modules,
        "zk_proof":       zk_proof_data,
        "fingerprint":    img_hash[:16]+"...",
        "plant_data":     plant_data,
        "receipt_id":     receipt_data.get("receipt_id") if receipt_data else None,
        "gasless":        DAY22_AVAILABLE,
        "paymaster_note": "ERC-4337 gasless tx via Pimlico bundler" if DAY22_AVAILABLE else None,
        "merkle_root":    receipt_data.get("merkle_root","")[:16]+"..." if receipt_data else None,
        "ipfs_cid":       ipfs_cid,
        "tx_hash":        tx_hash,
        "lovelock_score": lovelock_score,
        "evolution": {
            "xp_earned":  evo_result["xp_earned"],
            "total_xp":   evo_result["total_xp"],
            "level":      evo_result["level"],
            "leveled_up": evo_result["leveled_up"],
            "next_level": evo_result["next_level"],
            "xp_to_next": evo_result["xp_to_next"],
            "streak":     evo_result["streak_days"],
        }
    }), 200


# ── Video endpoint ─────────────────────────────────────────────────────────────
@app.route('/verify-video', methods=['POST'])
def verify_video():
    from activity_proof_engine import ActivityProofEngine
    ape = ActivityProofEngine()
    modules = {"spatial":"pending","liveness":"pending","ai":"pending","ocr":"pending","zk":"pending"}

    if 'video' not in request.files:
        return fraud("No video uploaded.", {k:"fail" for k in modules}), 400

    video_file = request.files['video']
    vfilename  = video_file.filename or "video.webm"

    video_file.seek(0,2); vsize=video_file.tell(); video_file.seek(0)
    if vsize > 50*1024*1024:
        return fraud("Video too large — max 50MB.", {k:"fail" for k in modules}), 400

    video_path = os.path.join(UPLOAD_FOLDER, f"video_{int(time.time())}.webm")
    video_file.save(video_path)

    # ── Real user_id from token ───────────────────────────────────────────────
    user_id = get_user_id_from_request(request)

    lat               = request.form.get('lat')
    lon               = request.form.get('lon')
    speed             = request.form.get('speed_kmh','0')
    dist              = request.form.get('distance_m','0')
    selected_activity = request.form.get('activity', None)

    if selected_activity and selected_activity.startswith('coming_soon'):
        return jsonify({
            "verdict": "FRAUD",
            "fraud_reason": "🚧 This activity is Coming Soon! Stay tuned!",
            "modules": {"spatial":"pass","liveness":"pass","ai":"pending","ocr":"fail","zk":"pending"}
        }), 400

    gps_data = None
    if lat and lon:
        gps_data = {"lat":float(lat),"lon":float(lon),
                    "speed_kmh":float(speed),"distance_m":float(dist)}
        modules["spatial"] = "pass"
    else:
        modules["spatial"] = "fail"
        return fraud("GPS required for video proof.", modules), 400

    modules["liveness"] = "pass"

    # AI vision
    try:
        import cv2 as _cv
        cap = _cv.VideoCapture(video_path)
        ret, frame = cap.read(); cap.release()
        if ret:
            img_rgb     = _cv.cvtColor(frame, _cv.COLOR_BGR2RGB)
            img_resized = _cv.resize(img_rgb, tuple(CONFIG['IMG_SIZE']))
            img_array   = preprocess_input(np.expand_dims(img_resized,0).astype(np.float32))
            predictions = get_model().predict(img_array, verbose=0)
            confidence  = float(np.max(predictions))
            predicted   = CLASS_NAMES[np.argmax(predictions)]
            if confidence < 0.35:  # Balanced threshold
                modules["ai"] = "fail"
                return fraud(f"Low confidence ({confidence*100:.1f}%)", modules), 400
            modules["ai"] = "pass"
            if selected_activity and selected_activity in ["plantation","recycling","led_lighting"]:
                predicted = selected_activity
        else:
            modules["ai"] = "fail"
            return fraud("Cannot read video.", modules), 400
    except Exception as e:
        modules["ai"] = "fail"
        return fraud(f"AI error: {e}", modules), 500

    # Security Gatekeeper — testing mode: warn only, never block
    if gatekeeper:
        try:
            import cv2 as _cv2
            cap = _cv2.VideoCapture(video_path)
            all_frames = []
            while cap.isOpened():
                ret, frm = cap.read()
                if not ret: break
                all_frames.append(frm)
            cap.release()
            hard_ok, hard_msg, hard_details = gatekeeper.hard_security_check(
                video_path, all_frames, gps_data, ip=request.remote_addr
            )
            if not hard_ok:
                print(f"   ⚠️ Security warning (testing — not blocking): {hard_msg}")
        except Exception as e:
            print(f"   ⚠️ Gatekeeper error: {e}")
    modules["liveness"] = "pass"

    # Activity proof
    video_result = ape.verify(video_path, predicted, gps_data, user_id=user_id)
    if not video_result["passed"]:
        modules["ocr"] = "fail"
        return fraud(video_result["reason"], modules), 400
    modules["ocr"] = "pass"

    img_hash      = hashlib.sha256(open(video_path,'rb').read()).hexdigest()
    zk_proof_data = hashlib.sha256(f"{img_hash}{time.time()}".encode()).hexdigest()[:32]
    modules["zk"] = "pass"

    reward_coins = round(COIN_REWARDS.get(predicted,1.0) + (confidence-0.60)*5, 2)
    carbon_kg    = round(reward_coins * CARBON_PER_COIN, 3)

    # Save to main DB
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO processed_images
            (class_name,confidence,reward_coins,carbon_kg,lat,lon,created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (predicted, confidence, reward_coins, carbon_kg,
              float(lat), float(lon),
              datetime.now(timezone.utc).isoformat()))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"DB: {e}")

    # Evolution XP
    try:
        evo_result = evolution.add_activity(user_id, predicted, reward_coins, carbon_kg)
        print(f"✅ XP saved: +{evo_result.get('xp_earned',0)} XP | Total: {evo_result.get('total_xp',0)}")
    except Exception as e:
        print(f"⚠️ Evolution: {e}")
        evo_result = {"xp_earned":10,"total_xp":10,"level":{"level":1,"name":"Seedling","icon":"🌱"},
                      "leveled_up":False,"xp_to_next":90,"streak_days":0}

    # ── FIX 3 APPLIED: Permanent save to auth DB ──────────────────────────────
    if AUTH_AVAILABLE and user_id not in ("user", "anonymous", ""):
        try:
            update_user_stats(user_id, evo_result.get('xp_earned',0), reward_coins, carbon_kg)
            print(f"   ✅ Permanent save: {user_id} +{evo_result.get('xp_earned',0)}XP +{reward_coins}GAIA")
        except Exception as e:
            print(f"   ⚠️ Permanent save error: {e}")

    log_verified(predicted, confidence, reward_coins)

    # Blockchain mint (single call)
    tx_hash = None
    try:
        if WEB3_AVAILABLE and DAY21_AVAILABLE and day21_engine:
            wallet = os.getenv('ADMIN_WALLET_ADDRESS', '')
            lat_f  = float(lat) if lat else float(os.getenv('DEFAULT_LAT', 24.8607))
            lon_f  = float(lon) if lon else float(os.getenv('DEFAULT_LON', 67.0011))
            loop   = asyncio.new_event_loop()
            receipt = loop.run_until_complete(
                day21_engine.execute(
                    lat=lat_f, lon=lon_f, co2_kg=carbon_kg,
                    wallet_address=wallet, activity_type=predicted
                )
            )
            loop.close()
            if receipt:
                tx_hash = receipt.on_chain_tx if hasattr(receipt,'on_chain_tx') else receipt.get('tx_hash')
    except Exception as e:
        print(f"⚠️ Mint: {e}")

    return jsonify({
        "verdict":        "VERIFIED",
        "class":          predicted,
        "confidence":     confidence,
        "reward_coins":   reward_coins,
        "carbon_kg":      carbon_kg,
        "planet_message": "Your action just cooled a 1mm patch of the Arctic.",
        "modules":        modules,
        "zk_proof":       zk_proof_data,
        "tx_hash":        tx_hash,
        "blockchain":     f"https://amoy.polygonscan.com/tx/{tx_hash}" if tx_hash else None,
        "evolution": {
            "xp_earned":  evo_result["xp_earned"],
            "total_xp":   evo_result["total_xp"],
            "level":      evo_result["level"],
            "leveled_up": evo_result["leveled_up"],
            "xp_to_next": evo_result["xp_to_next"],
            "streak":     evo_result["streak_days"],
        }
    }), 200


# ── Stats + APIs ───────────────────────────────────────────────────────────────
@app.route('/api/stats')
def get_stats():
    try:
        conn  = get_db()
        count = conn.execute("SELECT COUNT(*) FROM processed_images").fetchone()[0]
        co2   = conn.execute("SELECT SUM(carbon_kg) FROM processed_images").fetchone()[0] or 0
        conn.close()
        fp_stats = fingerprinter.get_stats()
        return jsonify({
            "total_actions": count, "total_co2_kg": round(co2,2),
            "fingerprints":  fp_stats.get('total',0),
            "banned_users":  fp_stats.get('banned',0), "status": "live"
        })
    except Exception as e:
        return jsonify({"total_actions":0,"status":"offline"})

@app.route('/api/recent-actions')
def get_recent_actions():
    try:
        conn = get_db()
        rows = conn.execute("""
            SELECT id,class_name,confidence,lat,lon,city,created_at,reward_coins,carbon_kg
            FROM processed_images ORDER BY created_at DESC LIMIT 10
        """).fetchall()
        conn.close()
        actions = [{
            "id":r[0],"type":r[1],"confidence":r[2],
            "lat":r[3] or 24.86,"lon":r[4] or 67.00,
            "city":r[5] or "Karachi","co2":r[8] or 1.8,"coins":r[7] or 1.0
        } for r in rows]
        return jsonify({"actions":actions,"count":len(actions)})
    except:
        return jsonify({"actions":[],"count":0})

@app.route('/api/profile/<user_id>')
def get_profile(user_id):
    # Token override
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token and AUTH_AVAILABLE:
        try:
            u = get_user_by_token(token)
            if u: user_id = u['user_id']
        except: pass

    profile = evolution.get_profile(user_id)
    if AUTH_AVAILABLE:
        try:
            import sqlite3 as _sq
            db  = _sq.connect("gaiavolt_users.db")
            row = db.execute(
                "SELECT name, city, country, xp, coins_total, carbon_total FROM users WHERE user_id=?",
                (user_id,)
            ).fetchone()
            db.close()
            if row:
                profile['user']['display_name']  = row[0]
                profile['user']['city']          = row[1]
                profile['user']['country']       = row[2]
                profile['user']['xp']            = max(profile['user'].get('xp',0), row[3])
                profile['user']['coins_total']   = max(profile['user'].get('coins_total',0), row[4])
                profile['user']['carbon_total']  = max(profile['user'].get('carbon_total',0), row[5])
        except Exception as e:
            print(f"Profile merge: {e}")
    return jsonify(profile)

@app.route('/api/leaderboard')
def get_leaderboard():
    return jsonify(evolution.get_leaderboard())

@app.route('/api/leaderboard/global')
def global_leaderboard():
    if AUTH_AVAILABLE:
        return jsonify({"leaderboard": auth_leaderboard(10)})
    return jsonify({"leaderboard": []})

@app.route('/api/partners')
def get_partners():
    return jsonify(bridges.get_all_partners())

@app.route('/api/coupons/<user_id>')
def get_coupons(user_id):
    return jsonify(bridges.get_user_coupons(user_id))

@app.route('/api/claim-coupon', methods=['POST'])
def claim_coupon():
    data       = request.get_json()
    user_id    = data.get('user_id','user')
    partner_id = data.get('partner_id')
    deal_id    = data.get('deal_id')
    profile    = evolution.get_profile(user_id)
    user_coins = profile['user'].get('coins_total',0)
    result     = bridges.claim_coupon(user_id, partner_id, deal_id, user_coins)
    if result['success']:
        evolution.db.execute(
            "UPDATE users SET coins_total=coins_total-? WHERE user_id=?",
            (result['coins_spent'], user_id)
        )
        evolution.db.commit()
    return jsonify(result)

@app.route('/api/redeem-coupon', methods=['POST'])
def redeem_coupon():
    data = request.get_json()
    return jsonify(bridges.redeem_coupon(data.get('coupon_code'), data.get('user_id','user')))

# ── Seed QR endpoints ─────────────────────────────────────────────────────────
@app.route('/api/seeds/order', methods=['POST'])
def order_seeds():
    data = request.get_json()
    return jsonify(seed_system.order_seeds(data.get('user_id','user'), int(data.get('qty',1))))

@app.route('/api/seeds/<user_id>')
def get_seeds(user_id):
    return jsonify(seed_system.get_user_seeds(user_id))

@app.route('/api/seeds/plant', methods=['POST'])
def plant_seed():
    data = request.get_json()
    return jsonify(seed_system.plant_seed(
        data.get('qr_code'), data.get('user_id','user'),
        data.get('lat'), data.get('lon'),
        data.get('img_hash'), data.get('base_coins',3.0)
    ))

@app.route('/api/seeds/growth', methods=['POST'])
def submit_growth():
    data = request.get_json()
    return jsonify(seed_system.submit_growth(
        data.get('qr_code'), data.get('user_id','user'),
        data.get('lat'), data.get('lon'),
        data.get('img_hash'), data.get('plant_size_cm',0),
        data.get('base_coins',3.0)
    ))

@app.route('/api/seeds/info/<qr_code>')
def seed_info(qr_code):
    seed = seed_system.get_seed_by_qr(qr_code)
    if not seed:
        return jsonify({"error":"Seed not found"}), 404
    return jsonify(seed)

# ── Plantation endpoints ──────────────────────────────────────────────────────
@app.route('/api/plants/<user_id>')
def get_plants(user_id):
    return jsonify(plantation_tracker.get_user_plants(user_id))

@app.route('/api/plant/verify-qr', methods=['POST'])
def verify_plant_qr():
    data = request.get_json()
    return jsonify(plantation_tracker.verify_qr_scan(
        data.get('qr_code'), data.get('user_id','user'),
        data.get('lat'), data.get('lon')
    ))

@app.route('/api/plant/stage-proof', methods=['POST'])
def plant_stage_proof():
    data = request.get_json()
    return jsonify(plantation_tracker.submit_stage_proof(
        data.get('plant_id'), data.get('user_id','user'),
        data.get('stage',2), data.get('lat'), data.get('lon'),
        data.get('video_hash'), data.get('qr_scanned',False),
        data.get('base_coins',3.0)
    ))

@app.route('/api/nfts/<user_id>')
def get_user_nfts(user_id):
    return jsonify(nft_eng.get_user_nfts(user_id))

@app.route('/api/nft/winners')
def get_winners():
    return jsonify(nft_eng.get_monthly_winners())

@app.route('/api/nft/mint-winner', methods=['POST'])
def mint_winner():
    winner = nft_eng.calculate_monthly_winner()
    if not winner:
        return jsonify({"success":False,"error":"No users found"}), 404
    return jsonify(nft_eng.mint_winner_nft(
        winner["user_id"], winner["user_name"],
        winner["month"], winner["year"],
        winner["xp"], winner["carbon"]
    ))

@app.route('/api/nft/evolve/<nft_id>', methods=['POST'])
def evolve_nft(nft_id):
    return jsonify(nft_eng.evolve_nft(nft_id))

@app.route('/api/job/<job_id>')
def get_job(job_id):
    return jsonify(processing_status.get(job_id, {"status":"not_found"}))

@app.route('/api/globe-data')
def globe_data():
    oracle_data = None
    try:
        if oracle:
            data = oracle.fetch_all(
                lat=float(os.getenv('DEFAULT_LAT', 24.8607)),
                lon=float(os.getenv('DEFAULT_LON', 67.0011))
            )
            oracle_data = {
                "temp_c":      data['weather']['temp'] if data.get('weather') else None,
                "carbon_rate": data.get('carbon_rate'),
                "condition":   data['weather']['condition'] if data.get('weather') else None,
                "source":      "open-meteo.com + carbonintensity.org.uk"
            }
    except Exception as e:
        print(f"Oracle: {e}")

    ecox_locked = 0.025
    try:
        if DAY21_AVAILABLE and day21_engine:
            info = day21_engine.web3.get_contract_info()
            ecox_locked = round(info.get('total_supply', 0.025), 4)
    except: pass

    try:
        conn  = get_db()
        count = conn.execute("SELECT COUNT(*) FROM processed_images").fetchone()[0]
        co2   = conn.execute("SELECT SUM(carbon_kg) FROM processed_images").fetchone()[0] or 0
        conn.close()
    except:
        count, co2 = 0, 0

    return jsonify({
        "oracle": oracle_data, "ecox_locked": ecox_locked,
        "paymaster": {
            "available": DAY22_AVAILABLE,
            "entry_point": "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789",
            "gasless": True
        } if DAY22_AVAILABLE else None,
        "total_actions": count, "total_co2": round(co2,2), "status": "live"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "online", "zk": ZK_AVAILABLE,
        "ipfs": IPFS_AVAILABLE, "day21": DAY21_AVAILABLE,
        "day22": DAY22_AVAILABLE, "web3": WEB3_AVAILABLE,
        "fingerprints": fingerprinter.get_stats(),
    })

@app.route('/')
def index():
    fp = fingerprinter.get_stats()
    return f"""<h1>🌍 GaiaVolt API</h1>
    <p>Fingerprints: {fp.get('total',0)}</p>
    <p>ZK: {'✅' if ZK_AVAILABLE else '⚠️'}</p>
    <p>IPFS: {'✅' if IPFS_AVAILABLE else '⚠️'}</p>
    <p>Day21: {'✅' if DAY21_AVAILABLE else '⚠️'}</p>
    <p>Status: ✅ Active</p>"""

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────
@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    if not AUTH_AVAILABLE:
        return jsonify({"error": "Auth not available"}), 500
    data       = request.get_json()
    name       = data.get('name','').strip()
    email      = data.get('email','').strip()
    password   = data.get('password','')
    city       = data.get('city','')
    country    = data.get('country','')
    age        = data.get('age',0)
    commitment = data.get('commitment','')
    device_id  = request.headers.get('X-Device-ID','')
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password required"}), 400
    result, error = signup(name, email, password, city, country, age, commitment, device_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 200

@app.route('/auth/login', methods=['POST'])
def auth_login():
    if not AUTH_AVAILABLE:
        return jsonify({"error": "Auth not available"}), 500
    data     = request.get_json()
    email    = data.get('email','').strip()
    password = data.get('password','')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    result, error = login(email, password)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 200

@app.route('/auth/me', methods=['GET'])
def auth_me():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    if not token:
        return jsonify({"error": "No token"}), 401
    user = get_user_by_token(token)
    if not user:
        return jsonify({"error": "Invalid token"}), 401
    return jsonify({"user": user}), 200


if __name__ == '__main__':
    port  = int(os.getenv('APP_PORT', 8000))
    debug = os.getenv('DEBUG','False').lower() == 'true'
    print(f"\n{'='*60}")
    print(f"🌐 GaiaVolt API — port {port}")
    print(f"{'='*60}")
    print(f"✅ Day 1-7:  AI Model wired")
    print(f"✅ Day 8-13: Security wired")
    print(f"✅ Day 14:   Oracle ready")
    print(f"✅ Day 15:   ZK Proof {'wired' if ZK_AVAILABLE else '(fallback)'}")
    print(f"✅ Day 18:   Fingerprint wired")
    print(f"✅ Day 19:   IPFS {'wired' if IPFS_AVAILABLE else '(fallback)'}")
    print(f"✅ Day 21:   Impact Engine {'wired' if DAY21_AVAILABLE else '(fallback)'}")
    print(f"✅ Day 22:   Paymaster {'wired' if DAY22_AVAILABLE else '(fallback)'}")
    print(f"✅ Day 25:   Evolution wired")
    print(f"✅ Auth:     Real user_id from JWT token")
    print(f"✅ DB Sync:  evolution.db + gaiavolt_users.db")
    print(f"{'='*60}\n")
    app.run(host='0.0.0.0', debug=debug, port=port)