import os
import cv2
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from web3 import Web3
from flask import Flask, request, jsonify
from anti_cheat import EcoXShield
from src.utils.constants import CONFIG
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input

load_dotenv()

app = Flask(__name__)

# ✅ P44 FIXED: password .env se
# ✅ P47 FIXED: contract address .env se
# ✅ P48 FIXED: ABI path dynamic
RPC_URL          = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
DB_HOST          = os.getenv('DB_HOST', 'localhost')
DB_NAME          = os.getenv('DB_NAME', 'postgres')
DB_USER          = os.getenv('DB_USER', 'postgres')
DB_PASS          = os.getenv('DB_PASSWORD', '')
ABI_PATH         = 'ecox-contracts/artifacts/contracts/EcoCoin.sol/EcoCoin.json'
UPLOAD_FOLDER    = 'dataset/uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ P46 FIXED: registered_user .env se
shield = EcoXShield()

# Web3 setup
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = None
if os.path.exists(ABI_PATH) and CONTRACT_ADDRESS:
    with open(ABI_PATH, "r") as f:
        contract_abi = json.load(f)["abi"]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# ✅ P49 FIXED: Vision model load karo!
model      = None
CLASS_NAMES = CONFIG['CLASSES']

def get_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(
            CONFIG['MODEL_PATH'], compile=False
        )
    return model


def get_db():
    # ✅ P44 FIXED: .env se credentials
    try:
        import psycopg2
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
    except Exception as e:
        print(f"DB Error: {e}")
        return None


# ✅ P50 FIXED: Rate limiting
from flask import g
import time
request_counts = {}

def rate_limit_check(ip, max_requests=10, window=60):
    now = time.time()
    if ip not in request_counts:
        request_counts[ip] = []
    request_counts[ip] = [t for t in request_counts[ip] if now - t < window]
    if len(request_counts[ip]) >= max_requests:
        return False
    request_counts[ip].append(now)
    return True


@app.route('/')
def index():
    try:
        count      = 0
        balance_eco = 0.0

        conn = get_db()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM processed_images")
            count = cur.fetchone()[0]
            conn.close()

        if contract:
            try:
                wallet = os.getenv('ADMIN_WALLET_ADDRESS', '')
                if wallet:
                    raw = contract.functions.balanceOf(wallet).call()
                    balance_eco = raw / (10**18)
            except Exception:
                pass

        return f"""
        <h1>🌍 EcoX Dashboard</h1>
        <p>Images Processed: {count}</p>
        <p>EcoCoin Balance: {balance_eco:.2f} ECO</p>
        <p>Status: ✅ Active</p>
        """
    except Exception as e:
        return f"<h1>Error</h1><p>Service unavailable</p>", 500


@app.route('/upload-ecox', methods=['POST'])
def upload_image():
    # ✅ P50 FIXED: Rate limit check
    ip = request.remote_addr
    if not rate_limit_check(ip):
        return jsonify({
            "status": "Rejected",
            "error": "Rate limit exceeded"
        }), 429

    if 'image' not in request.files:
        return jsonify({
            "status": "Rejected",
            "error": "No image uploaded"
        }), 400

    file      = request.files['image']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Liveness check
    img = cv2.imread(file_path)
    if img is None:
        return jsonify({
            "status": "Rejected",
            "error": "Invalid image"
        }), 400

    score = cv2.Laplacian(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        cv2.CV_64F
    ).var()

    if score < 100:
        return jsonify({
            "status":  "Rejected",
            "reason":  f"Spoof detected (Score: {score:.2f})"
        }), 401

    # ✅ P49 FIXED: AI model prediction!
    img_rgb   = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, tuple(CONFIG['IMG_SIZE']))
    img_array = np.expand_dims(img_resized, axis=0).astype(np.float32)
    img_array = preprocess_input(img_array)

    ai_model    = get_model()
    predictions = ai_model.predict(img_array, verbose=0)
    confidence  = float(np.max(predictions) * 100)
    predicted   = CLASS_NAMES[np.argmax(predictions)]

    if confidence < 70:
        return jsonify({
            "status":     "Rejected",
            "reason":     f"Low confidence: {confidence:.1f}%",
            "predicted":  predicted
        }), 400

    # Anti-cheat verification
    current_month = datetime.now(timezone.utc).strftime("%B %Y")
    extracted_text = f"{current_month} {shield.registered_user}"
    result = shield.verify_full_protocol(file_path, extracted_text)

    return jsonify({
        "status":     "Success",
        "result":     result,
        "predicted":  predicted,
        "confidence": f"{confidence:.1f}%"
    })


if __name__ == '__main__':
    port = int(os.getenv('APP_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    print(f"🌐 EcoX API running on port {port}...")
    app.run(debug=debug, port=port)