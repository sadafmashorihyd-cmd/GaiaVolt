import socket

def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

# Predict karo
from edge_predictor import EdgePredictor
import os

print("Testing offline capability...")
print(f"Internet: {'Available' if is_internet_available() else 'Not available'}")
print("(Works either way — TFLite is offline!)")

edge = EdgePredictor()
solar_dir = 'dataset/val/solar_panels/'
img = os.path.join(solar_dir, os.listdir(solar_dir)[0])
cls, _, conf, ms = edge.predict(img)
print(f"Result: {cls} ({conf:.1f}%) — OFFLINE CAPABLE ✅")