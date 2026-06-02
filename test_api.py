import requests
import os

# ✅ Port 8000 — app.py ka sahi port
url = 'http://127.0.0.1:8000/upload-ecox'

# ✅ Real image from dataset
img_dir = 'dataset/val/solar_panels/'
img_name = os.listdir(img_dir)[0]
img_path = os.path.join(img_dir, img_name)

print(f"🧪 Testing API...")
print(f"   Image: {img_name}")
print(f"   URL:   {url}")

with open(img_path, 'rb') as f:
    response = requests.post(url, files={'image': f})

print(f"\n   Status: {response.status_code}")
print(f"   Result: {response.json()}")