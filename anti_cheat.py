import hashlib
import os
from datetime import datetime, timezone
from PIL import Image
from PIL.ExifTags import TAGS
from dotenv import load_dotenv

load_dotenv()


class EcoXShield:
    def __init__(self, registered_user=None):
        self.registered_user = (
            registered_user or
            os.getenv('REGISTERED_USER', 'user')
        ).lower()
        self.processed_hashes = set()
        self.log_file = os.getenv('FRAUD_LOG', 'fraud_attempts.log')

    def log_fraud_attempt(self, reason):
        try:
            with open(self.log_file, "a") as f:
                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
                f.write(f"[{timestamp}] ALERT: {reason}\n")
            print(f"🚨 FRAUD: {reason}")
        except Exception as e:
            print(f"CRITICAL: Log failed: {e}")

    def generate_fingerprint(self, image_path):
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def check_duplicate(self, image_path):
        img_hash = self.generate_fingerprint(image_path)
        if img_hash in self.processed_hashes:
            self.log_fraud_attempt(f"Duplicate: {img_hash[:16]}...")
            return True, img_hash
        return False, img_hash

    def detect_editing_traces(self, image_path):
        try:
            img  = Image.open(image_path)
            info = img.info

            # Software metadata check
            software = (
                info.get('software', '') or
                info.get('Software', '') or
                info.get('Adobe',    '') or
                info.get('gimp',     '') or
                info.get('GIMP',     '')
            )
            if software:
                self.log_fraud_attempt(f"Editing software: {software}")
                return False

            # EXIF Software check
            try:
                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag == 'Software' and value:
                            self.log_fraud_attempt(f"EXIF Software: {value}")
                            return False
            except Exception:
                pass

            # ✅ Histogram check removed —
            # spoof_detector.py handles this!

            # Metadata strip check
            if len(info) == 0 and not image_path.lower().endswith('.png'):
                self.log_fraud_attempt("Metadata stripping detected!")
                return False

            return True

        except Exception as e:
            self.log_fraud_attempt(f"Forensic scan failed: {str(e)}")
            return False

    def verify_full_protocol(self, image_path, extracted_text):
        print(f"\n{'='*50}")
        print(f"🛡️  ECOX SHIELD — VERIFICATION")
        print(f"{'='*50}")

        if not os.path.exists(image_path):
            self.log_fraud_attempt(f"File missing: {image_path}")
            return "REJECTED: File Missing"

        # 1. Duplicate check
        is_duplicate, img_hash = self.check_duplicate(image_path)
        if is_duplicate:
            return "REJECTED: Duplicate Image"
        print(f"   Hash:      {img_hash[:16]}... ✅")

        # 2. Editing traces
        if not self.detect_editing_traces(image_path):
            return "REJECTED: Edited Image Detected"
        print(f"   Integrity: ✅ No editing traces")

        # 3. Identity match
        if self.registered_user not in extracted_text.lower():
            self.log_fraud_attempt(
                f"Identity mismatch: {self.registered_user}"
            )
            return "REJECTED: Identity Mismatch"
        print(f"   Identity:  ✅ {self.registered_user}")

        # 4. Temporal lock
        current_marker = datetime.now(timezone.utc).strftime(
            "%B %Y"
        ).lower()
        if current_marker not in extracted_text.lower():
            self.log_fraud_attempt("Temporal mismatch!")
            return "REJECTED: Invalid Billing Month"
        print(f"   Temporal:  ✅ {current_marker}")

        self.processed_hashes.add(img_hash)

        print(f"   Status:    ✅ APPROVED!")
        print(f"{'='*50}\n")
        return "APPROVED"


if __name__ == "__main__":
    shield = EcoXShield()
    print(f"User: {shield.registered_user}")

    test_bill = 'scripts/address_mismatch_test_bill_2026.jpeg'
    if os.path.exists(test_bill):
        result = shield.verify_full_protocol(
            test_bill,
            f"Nepra Bill May 2026 {shield.registered_user}"
        )
        print(f"Result: {result}")
    else:
        print(f"⚠️ Test bill not found: {test_bill}")