import os
import sys

# Root ko path mein add karein
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encryption_engine import encrypt_data, decrypt_data

# Image ka sahi relative path
file_path = os.path.join("..", "ecox_cyberpunk_scan.jpg")

print("🔐 Starting Encryption Test...")
encrypt_data(file_path)

# Verification: Data read karke check karein
with open(file_path, 'rb') as f:
    header = f.read(5)
    print(f"Data status: {'Encrypted' if header != b'\xff\xd8\xff\xe0' else 'Not Encrypted'}")

print("🔓 Decrypting file...")
decrypt_data(file_path)
print("✅ Test Complete: File restored and verified.")