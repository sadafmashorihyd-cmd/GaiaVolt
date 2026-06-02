import sys
import os
import json
import time
import cv2
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv

load_dotenv()

# ✅ P93 FIXED: .env se
# ✅ P94 FIXED: correct model path
MODEL_PATH  = 'ecox_model_edge.tflite'
WALLET_PATH = os.getenv('WALLET_FILE', 'sadaf_wallet.json')
USER        = os.getenv('REGISTERED_USER', 'User')


def check_system_integrity():
    print("\n" + "="*70)
    print("⚡ ECOX SYSTEM INTEGRITY CHECK")
    print("="*70)

    all_ok = True

    # 1. Framework versions
    print(f"\n📡 FRAMEWORK STATUS:")
    print(f"   ├── Python:     {sys.version[:5]} ✅")
    print(f"   ├── OpenCV:     {cv2.__version__} ✅")
    print(f"   ├── NumPy:      {np.__version__} ✅")
    print(f"   └── TensorFlow: {tf.__version__} ✅")

    # ✅ P96 FIXED: FastAPI sirf version check nahi —
    # properly import aur use karo
    try:
        import fastapi
        print(f"\n🌐 API GATEWAY:")
        print(f"   └── FastAPI: {fastapi.__version__} ✅")
    except ImportError:
        print(f"\n🌐 API GATEWAY:")
        print(f"   └── FastAPI: ❌ Not installed!")
        all_ok = False

    # 2. Edge model check
    print(f"\n🧠 NEURAL CORE:")
    if os.path.exists(MODEL_PATH):
        size = os.path.getsize(MODEL_PATH) / (1024*1024)
        print(f"   ├── Model:  {MODEL_PATH} ✅")
        print(f"   ├── Size:   {size:.2f} MB")

        # ✅ Actually load and test model!
        try:
            interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
            interpreter.allocate_tensors()
            input_shape = interpreter.get_input_details()[0]['shape']
            print(f"   ├── Input:  {input_shape} ✅")
            print(f"   └── Status: Loadable ✅")
        except Exception as e:
            print(f"   └── ❌ Load failed: {e}")
            all_ok = False
    else:
        print(f"   └── ❌ Model missing: {MODEL_PATH}")
        all_ok = False

    # 3. Wallet check
    print(f"\n💰 WALLET STATUS:")
    if os.path.exists(WALLET_PATH):
        try:
            with open(WALLET_PATH, 'r') as f:
                wallet = json.load(f)
            balance = wallet.get('balance', 0)
            txns    = len(wallet.get('history', []))
            print(f"   ├── File:         {WALLET_PATH} ✅")
            print(f"   ├── Balance:      {balance} Eco-Coins")
            print(f"   └── Transactions: {txns}")
        except Exception:
            print(f"   └── ❌ Wallet corrupted!")
            all_ok = False
    else:
        print(f"   └── ⚠️ Not initialized yet")

    # 4. Environment check
    print(f"\n🔐 ENVIRONMENT:")
    required_vars = [
        'RPC_URL', 'CONTRACT_ADDRESS',
        'REGISTERED_USER', 'SECRET_KEY'
    ]
    for var in required_vars:
        val = os.getenv(var)
        status = '✅' if val else '❌ Missing!'
        print(f"   ├── {var:<25} {status}")

    # 5. Dataset check
    print(f"\n📁 DATASET:")
    train_balanced = 'dataset/train_balanced'
    val_dir        = 'dataset/val'
    print(f"   ├── train_balanced: {'✅' if os.path.exists(train_balanced) else '❌'}")
    print(f"   └── val:            {'✅' if os.path.exists(val_dir) else '❌'}")

    # Final verdict
    print(f"\n{'='*70}")
    if all_ok:
        # ✅ P95 FIXED: "UN-HACKABLE" claim hata diya — honest status
        print(f"✅ STATUS: All systems operational!")
        print(f"🚀 {USER}, EcoX is ready to launch!")
    else:
        print(f"⚠️  STATUS: Some issues found — fix before launch!")
    print(f"{'='*70}\n")

    return all_ok


if __name__ == "__main__":
    check_system_integrity()