import sqlite3
import os
import hashlib  # Naya import

def get_file_hash(file_path):
    # Deterministic SHA-256 hash for files
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # File ko chunks mein read karna memory ke liye behtar hai
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_image_unique(image_path, user_id):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fingerprints.db")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS processed_images 
                    (hash TEXT PRIMARY KEY, user_id TEXT)''')
    
    # Naya Secure Hash call karein
    image_hash = get_file_hash(image_path) 
    
    cur.execute("SELECT * FROM processed_images WHERE hash=?", (image_hash,))
    if cur.fetchone():
        conn.close()
        return False, "⚠️Fraud Attempt: Already processed!"
    
    cur.execute("INSERT INTO processed_images VALUES (?, ?)", (image_hash, user_id))
    conn.commit()
    conn.close()
    return True, "Success"