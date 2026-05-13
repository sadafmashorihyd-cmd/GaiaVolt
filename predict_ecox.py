import tensorflow as tf
import numpy as np
import os
import json
from tensorflow.keras.preprocessing import image

# 1. Global Rewards Table (Founder's Decision)
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

# 2. Wallet Database (Sadaf ke Coins save karne ke liye)
DB_FILE = 'sadaf_wallet.json'

def load_wallet():
    if not os.path.exists(DB_FILE):
        return {"balance": 0, "history": []}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_wallet(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 3. Model Load karna
model = tf.keras.models.load_model('ecox_model.h5')
data_dir = 'dataset'
class_names = sorted([f for f in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, f))])

def verify_and_reward(img_path):
    # Image preprocessing
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Prediction
    predictions = model.predict(img_array)
    score = np.max(predictions) * 100
    class_idx = np.argmax(predictions)
    result = class_names[class_idx]

    wallet = load_wallet()

    print(f"\n--- 🌍 EcoX Global Verification System ---")
    
    # 4. Threshold Logic (70% Minimum Match)
    if score < 70:
        print(f"❌ REJECTED: Match is too low ({score:.2f}%). Please take a clearer photo.")
    else:
        points = reward_points.get(result, 0)
        wallet['balance'] += points
        wallet['history'].append({"action": result, "reward": points, "match": f"{score:.2f}%"})
        save_wallet(wallet)
        
        print(f"✅ VERIFIED: This is {result} ({score:.2f}% match)")
        print(f"🎉 SUCCESS: +{points} Eco-Coins added to your wallet!")
        print(f"💰 CURRENT BALANCE: {wallet['balance']} Eco-Coins")

# --- TEST KAREIN ---
# Kisi bhi image ka sahi path dein
test_image = 'dataset/plantation/image_1.jpg'
verify_and_reward(test_image)