import os
from flask import Flask, request, jsonify
import cv2
import numpy as np
from anti_cheat import final_verification # Jo hum ne pehle banaya tha

app = Flask(__name__)
UPLOAD_FOLDER = 'dataset/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Liveness Detection Function ---
def check_liveness(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score

@app.route('/upload-ecox', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 1. Liveness Check
    liveness_score = check_liveness(file_path)
    if liveness_score < 100: # Standard threshold
        return jsonify({"status": "Rejected", "reason": "Liveness Failed (Screen Photo detected)"})

    # 2. Anti-Cheat (Time & GPS)
    # Note: Hum farzi lat/lon bhej rahe hain test ke liye
    security_result = final_verification(file_path, 25.3960, 68.3578)
    
    if "REJECTED" in security_result:
        return jsonify({"status": "Rejected", "reason": security_result})

    return jsonify({
        "status": "Success",
        "liveness_score": round(liveness_score, 2),
        "message": "Image Verified! Scientist Sadaf, points are being added."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)