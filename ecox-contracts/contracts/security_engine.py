import psycopg2
import imagehash
from PIL import Image
import os
import logging
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import numpy as np

# Load AI Model once
model = MobileNetV2(weights='imagenet')

logging.basicConfig(filename='fraud_attempts.log', level=logging.INFO, format='%(asctime)s - User: %(message)s')

def get_db_connection():
    return psycopg2.connect(dbname="postgres", user="postgres", password="mskbh2009", host="localhost")

def is_green_content(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    preds = model.predict(x)
    results = decode_predictions(preds, top=3)[0]
    eco_keywords = ['leaf', 'tree', 'plant', 'grass', 'pot', 'recycled', 'garden', 'broccoli']
    for _, label, score in results:
        if any(keyword in label.lower() for keyword in eco_keywords):
            return True, label
    return False, "Not an eco-friendly object"

def is_image_unique(image_path, user_id):
    if not os.path.exists(image_path): return False, "File nahi mili!"
    with Image.open(image_path) as img:
        img_hash = str(imagehash.phash(img))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT hash FROM processed_images WHERE hash=%s", (img_hash,))
    if cur.fetchone():
        conn.close()
        return False, f"⚠️ Fraud Attempt: Already processed! Hash: {img_hash[:10]}..."
    cur.execute("INSERT INTO processed_images (hash, user_id) VALUES (%s, %s)", (img_hash, user_id))
    conn.commit()
    conn.close()
    return True, img_hash

def check_reward_eligibility(image_path, user_id):
    is_unique, msg = is_image_unique(image_path, user_id)
    if not is_unique: return False, msg
    is_green, label = is_green_content(image_path)
    if is_green:
        return True, f"✅ Verified Green Content: {label}"
    else:
        return False, "❌ AI Signal: Image does not contain verified green content."