import hmac
import hashlib
import json
import os
from dotenv import load_dotenv

load_dotenv()


def get_secret_key():
    # ✅ P57 FIXED: .env se load
    key = os.getenv('SECRET_KEY', 'ecox_default_secret')
    return key.encode('utf-8')


def sign_metadata(metadata_dict):
    data = metadata_dict.copy()
    data.pop('signature', None)
    msg       = json.dumps(data, sort_keys=True).encode()
    secret    = get_secret_key()
    signature = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    metadata_dict['signature'] = signature
    return metadata_dict


def verify_metadata(metadata_dict):
    data      = metadata_dict.copy()
    signature = data.pop('signature', None)
    if not signature:
        return False
    msg      = json.dumps(data, sort_keys=True).encode()
    secret   = get_secret_key()
    expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔐 SECURITY UTILS TEST")
    print("="*50)

    test_data = {"user": "sadaf", "action": "solar_panels", "coins": 50}

    signed = sign_metadata(test_data.copy())
    print(f"   Signed:    ✅ {signed['signature'][:16]}...")

    valid = verify_metadata(signed.copy())
    print(f"   Valid sig: {'✅' if valid else '❌'}")

    tampered         = signed.copy()
    tampered['coins'] = 999
    invalid          = verify_metadata(tampered)
    print(f"   Tampered:  {'✅ Caught!' if not invalid else '❌ Not caught!'}")

    print("="*50 + "\n")