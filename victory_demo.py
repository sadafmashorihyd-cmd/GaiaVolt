import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np
import time
from datetime import datetime, timezone
from src.utils.spoof_detector import detect_spoof
from predict_ecox import verify_and_reward
from user_identity import create_identity, load_identity
from geo_fence import check_geo_fence


def print_banner():
    print(f"\n{'🌍'*30}")
    print(f"""
    ███████╗ ██████╗ ██████╗ ██╗  ██╗
    ██╔════╝██╔════╝██╔═══██╗╚██╗██╔╝
    █████╗  ██║     ██║   ██║ ╚███╔╝ 
    ██╔══╝  ██║     ██║   ██║ ██╔██╗ 
    ███████╗╚██████╗╚██████╔╝██╔╝ ██╗
    ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
    """)
    print(f"    🌍 VICTORY DEMO — DAY 14")
    print(f"    People built apps for social media,")
    print(f"    I built an app for the Planet.")
    print(f"{'🌍'*30}\n")


def demo_attack(name, img_path, lat=None, lon=None):
    """Run single attack and show result"""
    print(f"\n{'─'*60}")
    print(f"🔴 ATTACK: {name}")
    print(f"{'─'*60}")

    result = verify_and_reward(img_path, lat=lat, lon=lon)

    if result:
        print(f"⚠️  REWARD GIVEN — check if this was valid!")
    else:
        print(f"🚨 RED ALERT — Attack blocked!")

    time.sleep(0.5)
    return result


if __name__ == "__main__":
    print_banner()

    # Setup fresh identity
    if os.path.exists('user_identity.json'):
        os.remove('user_identity.json')
    if os.path.exists('geo_fence_log.json'):
        os.remove('geo_fence_log.json')

    import json
    wallet_reset = {
        'balance': 0, 'history': [],
        'processed_hashes': [], 'processed_phashes': [],
        'identity_hash': ''
    }
    with open('sadaf_wallet.json', 'w') as f:
        json.dump(wallet_reset, f, indent=4)

    print(f"\n{'='*60}")
    print(f"🎬 SCENE 1: Setup")
    print(f"{'='*60}")
    create_identity("Sadaf", "1234")
    print(f"✅ Identity created for demo!")

    solar_dir   = 'dataset/val/solar_panels/'
    cycling_dir = 'dataset/val/cycling/'
    bills_dir   = 'dataset/val/utility_bills/'

    solar_img   = os.path.join(solar_dir, os.listdir(solar_dir)[0])
    cycling_img = os.path.join(cycling_dir, os.listdir(cycling_dir)[0])
    bills_img   = os.path.join(bills_dir, os.listdir(bills_dir)[0])

    print(f"\n{'='*60}")
    print(f"🎬 SCENE 2: Legitimate submissions")
    print(f"{'='*60}")

    print(f"\n✅ Submitting real solar panel...")
    demo_attack("Real Solar Panel", solar_img,
                lat=24.8607, lon=67.0011)

    print(f"\n✅ Submitting real cycling...")
    demo_attack("Real Cycling", cycling_img,
                lat=24.8650, lon=67.0050)

    print(f"\n{'='*60}")
    print(f"🎬 SCENE 3: Hacker attacks!")
    print(f"{'='*60}")

    # Attack 1: Duplicate photo
    print(f"\n🔴 Hacker tries: SAME photo again!")
    demo_attack("Duplicate Solar Panel", solar_img,
                lat=24.8607, lon=67.0011)

    # Attack 2: Fake bill
    print(f"\n🔴 Hacker tries: FAKE blank bill!")
    fake_bill = 'fake_bill.jpg'
    fake      = np.zeros((300, 400, 3), dtype=np.uint8) + 240
    cv2.imwrite(fake_bill, fake)
    demo_attack("Fake Blank Bill", fake_bill,
                lat=24.8700, lon=67.0100)
    os.remove(fake_bill)

    # Attack 3: GPS flood
    print(f"\n🔴 Hacker tries: Too many submissions!")
    demo_attack("GPS Flood", solar_img,
                lat=24.8720, lon=67.0120)

    # Attack 4: Spoof screen
    print(f"\n🔴 Hacker tries: Screen/digital spoof!")
    spoof = np.ones((224, 224, 3), dtype=np.uint8) * 128
    for i in range(0, 224, 4):
        spoof[i, :] = [100, 100, 100]
    cv2.imwrite('spoof_screen.jpg', spoof)
    demo_attack("Screen Spoof", 'spoof_screen.jpg',
                lat=24.8750, lon=67.0150)
    os.remove('spoof_screen.jpg')

    # Final wallet
    print(f"\n{'='*60}")
    print(f"🎬 SCENE 4: Final Results")
    print(f"{'='*60}")

    with open('sadaf_wallet.json', 'r') as f:
        wallet = json.load(f)

    print(f"\n💰 WALLET SUMMARY:")
    print(f"   Balance:      {wallet['balance']} Eco-Coins")
    print(f"   Transactions: {len(wallet['history'])}")
    print(f"\n   Transaction History:")
    for tx in wallet['history']:
        print(f"   ✅ {tx['action']:<22} +{tx['reward']} coins")

    print(f"\n{'🌍'*30}")
    print(f"   EcoX: Fraud-proof Carbon Economy!")
    print(f"   People built apps for social media,")
    print(f"   I built an app for the Planet. 🌍")
    print(f"{'🌍'*30}\n")

    # Cleanup
    if os.path.exists('user_identity.json'):
        os.remove('user_identity.json')
    if os.path.exists('geo_fence_log.json'):
        os.remove('geo_fence_log.json')