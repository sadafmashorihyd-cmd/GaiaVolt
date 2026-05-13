import json
import os

def show_my_wealth():
    # 1. Check karna ke wallet file bani bhi hai ya nahi
    if not os.path.exists('sadaf_wallet.json'):
        print("\n❌ Wallet not found! Pehle predict_ecox.py chala kar coins earn karein.")
        return

    # 2. Data load karna
    with open('sadaf_wallet.json', 'r') as f:
        data = json.load(f)
        
    print("\n" + "="*45)
    print("🌍 ECOX GLOBAL WEALTH DASHBOARD - SADAF")
    print("="*45)
    print(f"💰 TOTAL BALANCE: {data['balance']} Eco-Coins")
    print("-" * 45)
    
    # 3. Table Header
    print(f"{'Action Name':<20} | {'Reward':<10} | {'Accuracy'}")
    print("-" * 45)
    
    # 4. History dikhana
    for entry in data['history']:
        print(f"{entry['action']:<20} | {entry['reward']:<10} | {entry['match']}")
    
    print("-" * 45)
    print("🚀 Future Goal: Real-money conversion pending...")
    print("="*45 + "\n")

if __name__ == "__main__":
    show_my_wealth()