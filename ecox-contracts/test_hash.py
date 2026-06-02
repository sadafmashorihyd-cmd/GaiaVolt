from contracts.security_engine import get_file_hash

h1 = get_file_hash("test.png")
h2 = get_file_hash("test.png")

print(f"Hash 1: {h1}")
print(f"Hash 2: {h2}")

if h1 == h2:
    print("✅ SUCCESS: Hash match kar gaya, system stable hai!")
else:
    print("❌ ERROR: Hash match nahi kiya, code check karein.")