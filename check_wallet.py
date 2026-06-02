import json
import os
from dotenv import load_dotenv

load_dotenv()


def show_my_wealth():
    # ✅ P97 FIXED: hardcoded nahi — .env se
    wallet_file = os.getenv('WALLET_FILE', 'sadaf_wallet.json')

    if not os.path.exists(wallet_file):
        print("\n❌ Wallet not found! Pehle predict_ecox.py chala kar coins earn karein.")
        return

    try:
        with open(wallet_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Wallet file corrupted!")
        return

    # ✅ P98 FIXED: User name .env se
    user = os.getenv('REGISTERED_USER', 'User').upper()

    print("\n" + "="*50)
    print(f"🌍 ECOX GLOBAL WEALTH DASHBOARD — {user}")
    print("="*50)
    print(f"💰 TOTAL BALANCE: {data.get('balance', 0)} Eco-Coins")
    print("-"*50)

    history = data.get('history', [])

    if not history:
        print("   No transactions yet!")
    else:
        print(f"{'Action':<22} | {'Reward':<10} | {'Confidence':<12} | Time")
        print("-"*50)
        for entry in history:
            # Timestamp format
            ts = entry.get('timestamp', 0)
            if ts:
                from datetime import datetime, timezone
                time_str = datetime.fromtimestamp(
                    ts, tz=timezone.utc
                ).strftime("%m/%d %H:%M")
            else:
                time_str = "N/A"

            print(
                f"{entry.get('action','?'):<22} | "
                f"{entry.get('reward',0):<10} | "
                f"{entry.get('match','?'):<12} | "
                f"{time_str}"
            )

    print("-"*50)
    print(f"   Total transactions: {len(history)}")
    print(f"🚀 Future: Real-money conversion coming soon!")
    print("="*50 + "\n")


if __name__ == "__main__":
    show_my_wealth()