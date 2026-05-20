import os
import cv2
import psycopg2
import json
from web3 import Web3
from flask import Flask, request, jsonify
from anti_cheat import EcoXShield 

app = Flask(__name__)

# --- Configuration ---
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
ABI_PATH = "ecox-contracts/artifacts/contracts/EcoCoin.sol/EcoCoin.json"

UPLOAD_FOLDER = 'dataset/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Initialize Engines ---
shield = EcoXShield(registered_user="Sadaf")
with open(ABI_PATH, "r") as f:
    contract_abi = json.load(f)["abi"]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def get_db():
    return psycopg2.connect(dbname="postgres", user="postgres", password="mskbh2009", host="localhost")

# --- Dashboard Route ---
@app.route('/')
def index():
    try:
        # DB Data
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM processed_images")
        count = cur.fetchone()[0]
        conn.close()

        # Blockchain Data (Safe Mode: Error handling included)
        try:
            balance_raw = contract.functions.balanceOf("0x70997970C51812dc3A010C7d01b50e0d17dc79C8").call()
            balance_eco = balance_raw / (10**18)
        except:
            balance_eco = 0.0

        return f"<h1>EcoX Dashboard</h1><p>Images Processed: {count}</p><p>EcoCoin Balance: {balance_eco:.2f} ECO</p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

# --- API Route (Anti-Cheat) ---
@app.route('/upload-ecox', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"status": "Rejected", "error": "No image uploaded"}), 400
        
    file = request.files['image']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    
    # Liveness check
    img = cv2.imread(file_path)
    if img is None:
        return jsonify({"status": "Rejected", "error": "Invalid image"}), 400
        
    score = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    
    if score < 100:
        return jsonify({"status": "Rejected", "reason": f"Spoof detected (Score: {score:.2f})"}), 401
    
    result = shield.verify_full_protocol(file_path, "Nepra Utility Bill May 2026 Sadaf Certified")
    return jsonify({"status": "Success", "result": result})

if __name__ == '__main__':
    print("🌐 [DEPLOYMENT ACTIVE]: EcoX Mainnet API Engine running on Port 5000...")
    app.run(debug=True, port=5000)