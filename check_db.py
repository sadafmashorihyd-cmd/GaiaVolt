import sqlite3
import hashlib
import os

DB_PATH = 'ecox-contracts/contracts/fingerprints.db'

def get_connection():
    # Database connection with foreign key constraints enabled
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def record_fingerprint(device_id, image_hash):
    """
    Transactions ko 'Atomic' banaya hai taake duplicate entries na hon.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if record exists (Prevent duplicate rewards)
        cursor.execute("SELECT id FROM file_records WHERE image_hash = ?", (image_hash,))
        if cursor.fetchone():
            return False, "❌ Fraud: Image already rewarded!"
            
        # Record transaction with Device ID
        cursor.execute("""
            INSERT INTO file_records (device_id, image_hash, timestamp)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (device_id, image_hash))
        
        conn.commit()
        return True, "✅ Reward Processed."
        
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"❌ Database Error: {e}"
    finally:
        conn.close()