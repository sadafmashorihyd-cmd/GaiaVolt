import os
import sys
import cv2
import numpy as np
from flask import Flask, request, jsonify
# FIXED: Importing correct class from anti_cheat layer
from anti_cheat import EcoXShield 

app = Flask(__name__)
UPLOAD_FOLDER = 'dataset/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the 2040 Security Shield
shield = EcoXShield(registered_user="Sadaf")

def check_liveness(image_path):
    """
    Forensic Laplacian Texture Analysis for Screen Spoofer Prevention
    """
    img = cv2.imread(image_path)
    if img is None:
        return 0.0
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score

@app.route('/upload-ecox', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"status": "Rejected", "error": "No image resource node uploaded"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "Rejected", "error": "Empty data payload node"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 1. Real-time Liveness Scan Gateway
    liveness_score = check_liveness(file_path)
    print(f"⚡ [API GATEWAY]: Received Scan Input. Liveness Variance Score -> {liveness_score:.2f}")
    
    if liveness_score < 100: 
        return jsonify({
            "status": "Rejected", 
            "reason": f"Liveness Failed. Detected Screen/Spoof Pattern (Score: {liveness_score:.2f})"
        }), 401

    # 2. Dynamic Identity & Anti-Cheat Sync Matrix
    # Simulated OCR extraction text data matching our dynamic marker logic
    simulated_ocr_text = "Nepra Utility Bill May 2026 Sadaf Certified System"
    
    # FIXED: Bound properly to the correct Object Method
    security_result = shield.verify_full_protocol(file_path, simulated_ocr_text)
    
    if "REJECTED" in security_result:
        return jsonify({"status": "Rejected", "reason": security_result}), 403

    return jsonify({
        "status": "Success",
        "liveness_score": round(liveness_score, 2),
        "oracle_validation": security_result,
        "message": "Image Verified! Scientist Sadaf, eco-rewards successfully pushed to ledger nodes."
    }), 200

if __name__ == '__main__':
    print("🌐 [DEPLOYMENT ACTIVE]: EcoX Mainnet API Engine running on Port 5000...")
    app.run(debug=True, port=5000, use_reloader=False)