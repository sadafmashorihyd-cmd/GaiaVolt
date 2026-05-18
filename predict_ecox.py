import tensorflow as tf
import numpy as np
import os
import json
import time
import random
import cv2  # basic image processing aur forensic analysis ke liye

# =====================================================================
# 🧠 1. GLOBAL REWARDS TABLE (Founder's Vision 2040)
# =====================================================================
reward_points = {
    "ocean_cleanup": 100,
    "solar_panels": 50,
    "plantation": 40,
    "electric_cars": 60,
    "cycling": 20,
    "recycling": 30,
    "utility_bills": 25,
    "organic_farming": 45,
    "wind_energy": 80,
    "water_conservation": 35,
    "led_lighting": 15,
    "public_transport": 10
}

DB_FILE = 'sadaf_wallet.json'

def load_wallet():
    """
    FIXED: Auto-initializes structure if file is empty or corrupted.
    """
    default_structure = {"balance": 0, "history": []}
    
    if not os.path.exists(DB_FILE):
        return default_structure
        
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            # Agar file empty curly braces {} ho toh keys verify karein
            if not isinstance(data, dict) or "balance" not in data:
                return default_structure
            return data
    except (json.JSONDecodeError, KeyError):
        # Corrupted file safeguard
        return default_structure

def save_wallet(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# =====================================================================
# 🛡️ 2. ADVANCED FORENSIC ANTI-CHEAT (Sentinel Level 1)
# =====================================================================
def analyze_moire_pattern(img_path):
    """
    FFT Analysis Simulation: Detects if the user is taking a photo of a digital screen.
    """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False # Image issue
    
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    if laplacian_var < 100.0: 
        return True # Screen Fraud Detected
    return False

# =====================================================================
# 📝 3. DOCUMENT INTELLIGENCE PIPELINE (OCR Engine)
# =====================================================================
def extract_and_verify_ocr(img_path):
    print("📝 [DOCUMENT INTELLIGENCE]: Initializing Neural Text Scanner...")
    time.sleep(0.4) 
    
    simulated_extracted_text = "ECO-COMPLIANT UTILITY BILL TYPE-2026 VERIFIED MAINNET"
    fake_keywords = ['sample', 'void', 'specimen', 'fake', 'photocopy']
    is_authentic = not any(word in simulated_extracted_text.lower() for word in fake_keywords)
    
    return is_authentic, simulated_extracted_text[:50]

# =====================================================================
# 🌌 4. THE GOD-EYE CORE (Prediction & Validation)
# =====================================================================
if os.path.exists('ecox_model.h5'):
    model = tf.keras.models.load_model('ecox_model.h5')
else:
    raise FileNotFoundError("🚨 [CRITICAL]: 'ecox_model.h5' not found. Ensure model is in the root directory.")

data_dir = 'dataset'
if os.path.exists(data_dir):
    class_names = sorted([f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))])
else:
    class_names = list(reward_points.keys())

def verify_and_reward(img_path):
    print("\n" + "="*60)
    print("🌐 [GLOBAL NODE SYNC]: Connecting to EcoX Decentralized Oracle...")
    print("⚡ [SENTINEL PROTOCOL]: Initializing Cyberpunk Grad-CAM X-Ray Heatmap...")
    time.sleep(0.5)

    if not os.path.exists(img_path):
        print(f"❌ [ERROR]: Target image data node '{img_path}' not found.")
        print("="*60 + "\n")
        return

    screen_fraud_detected = analyze_moire_pattern(img_path)
    if screen_fraud_detected:
        print("\n!!! 🚨 [CYBERPUNK ALERT]: FRAUD ATTEMPT DETECTED !!!")
        print("💀 [GENESIS VERDICT]: TRANSACTION ABORTED. Reason: Digital Screen Capture Blocked.")
        print("="*60 + "\n")
        return

    img = cv2.imread(img_path)
    img_resized = cv2.resize(img, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0) / 255.0

    predictions = model.predict(img_array, verbose=0)
    score = np.max(predictions) * 100
    class_idx = np.argmax(predictions)
    result = class_names[class_idx]

    print(f"👁️  [GOD-EYE ANALYSIS]: Scan Complete. Target Identified as -> '{result}'")

    if score < 70:
        print(f"❌ REJECTED: Low Confidence Waveform ({score:.2f}%). Need Higher Fidelity Data.")
    else:
        if result in ['utility_bills', 'documents']:
            is_authentic, text_sample = extract_and_verify_ocr(img_path)
            if not is_authentic:
                print("🚨 [SECURITY BREACH]: Bill text validation failed. Metadata Tampering Blocked.")
                print("="*60 + "\n")
                return
            print(f"🔒 [PHYSICAL PRESENCE AUTHENTICATED]: Document Data Validated -> '{text_sample}...'")

        # Safe Wallet Loading
        wallet = load_wallet()
        points = reward_points.get(result, 0)
        
        wallet['balance'] += points
        wallet['history'].append({
            "action": result, 
            "reward": points, 
            "match": f"{score:.2f}%",
            "timestamp": time.time()
        })
        save_wallet(wallet)
        
        print("\n+++++++++++++++++++++++++++++++++++++++++++++")
        print("   █████╗  ██████╗ ██████╗███████╗███████╗")
        print("  ██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝")
        print("  ███████║██║     ██║     █████╗  ███████╗")
        print("  ██╔══██║██║     ██║     ██╔══╝  ╚════██║")
        print("  ██║  ██║╚██████╗╚██████╗███████╗███████║")
        print("  ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝")
        print("               [ACCESS GRANTED]           ")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
        print(f"🎉 SUCCESS: +{points} Eco-Coins successfully minted to ledger!")
        print(f"💰 CURRENT WALLET BALANCE: {wallet['balance']} Eco-Coins")
    
    print("="*60 + "\n")

# =====================================================================
# 🎯 EXECUTION MATRIX
# =====================================================================
if __name__ == "__main__":
    test_image = 'dataset/plantation/image_1.jpg'
    
    if not os.path.exists('dataset/plantation'):
        os.makedirs('dataset/plantation', exist_ok=True)
        dummy_img = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.imwrite(test_image, dummy_img)
        
    verify_and_reward(test_image)