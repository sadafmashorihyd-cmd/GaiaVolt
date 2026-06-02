import sys
import os

# Ye line folder structure ko fix kar degi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from contracts.security_engine import get_file_hash

# Aapke folder mein 'ecox_cyberpunk_scan.jpg' majood hai, hum wahi use karenge
file_path = os.path.join("..", "ecox_cyberpunk_scan.jpg") 

h1 = get_file_hash(file_path)
h2 = get_file_hash(file_path)

print(f"Hash 1: {h1}")
print(f"Hash 2: {h2}")

if h1 == h2:
    print("✅ SUCCESS: Hash match kar gaya!")
else:
    print("❌ ERROR: Hash match nahi kiya!")