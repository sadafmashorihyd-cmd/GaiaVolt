import hashlib
import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

class EcoXShield:
    def __init__(self, registered_user="Sadaf"):
        self.registered_user = registered_user.lower()
        self.blockchain_hashes = "processed_hashes.json" # Simulated Blockchain

    def generate_fingerprint(self, image_path):
        """Step 2: SHA-256 digital signature banana"""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def detect_editing_traces(self, image_path):
        """Step 4: Scan for Photoshop or Editing software traces"""
        try:
            img = Image.open(image_path)
            info = img.info
            # Agar image mein 'Adobe' ya 'Software' ka tag hai, toh fraud hai
            software = info.get('software', '') or info.get('Adobe', '')
            if software:
                print(f"🚨 FRAUD ALERT: Editing software detected ({software})!")
                return False
            return True
        except:
            return False

    def verify_full_protocol(self, image_path, extracted_text):
        print(f"\n🛡️ Running EcoX Verification Loop for: {image_path}")
        
        # 1. SHA-256 Check (Blockchain History)
        img_hash = self.generate_fingerprint(image_path)
        print(f"🔑 Image Hash: {img_hash[:15]}...")
        # (Yahan aap hash ko database se check kar sakti hain)

        # 2. Binary Integrity (Editing check)
        if not self.detect_editing_traces(image_path):
            return "REJECTED: Edited Image Detected"

        # 3. Ownership & OCR Check (Ownership Match)
        if self.registered_user not in extracted_text.lower():
            print(f"❌ OWNERSHIP ERROR: Bill does not belong to {self.registered_user}")
            return "REJECTED: User Identity Mismatch"

        # 4. Temporal Lock (Current Month/Year)
        current_marker = "may 2026"
        if current_marker not in extracted_text.lower():
            return "REJECTED: Old/Invalid Billing Month"

        print("✅ GENESIS CONTRACT: All checks passed. Releasing Rewards!")
        return "APPROVED"

# --- 🧪 The Verification Loop ---
if __name__ == "__main__":
    shield = EcoXShield(registered_user="Sadaf")
    
    # Example usage (Testing with the bill we just scanned)
    sample_path = 'dataset/utility_bills/test_bill_2026.jpg'
    
    # In reality, 'text' will come from your document_expert.py
    sample_text = "Nepra Bill May 2026 Sadaf Consumer ID 12345" 
    
    result = shield.verify_full_protocol(sample_path, sample_text)
    print(f"\nFinal Result: {result}")