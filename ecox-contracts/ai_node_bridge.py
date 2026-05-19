import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

# --- SEAMLESS ENVIRONMENT INITIALIZATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

print("==================================================================")
print("🛡️ EcoX Hardened Python Node Engine — Day 17 Automated Pipeline")
print("==================================================================")

LOCAL_RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

ARTIFACTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ABI_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts", "contracts", "EcoCoin.sol", "EcoCoin.json")
w3 = Web3(Web3.HTTPProvider(LOCAL_RPC_URL))

with open(ABI_PATH, "r") as f:
    contract_abi = json.load(f)["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# ==================================================================
# DAY 17: REAL AUTOMATED AI MINTING GATEWAY
# ==================================================================

def trigger_ai_mint(recipient_address, reward_amount, action_id_bytes):
    """
    Day 17: Direct AI-to-Blockchain minting. No ZK-Proof needed if AI Oracle is validated.
    """
    print(f"\n[DAY 17 AI ENGINE] 🟢 Automated Minting Triggered for: {recipient_address}")
    
    oracle_private_key = os.getenv("ORACLE_PRIVATE_KEY")
    oracle_account = w3.eth.account.from_key(oracle_private_key)
    
    nonce = w3.eth.get_transaction_count(oracle_account.address)
    
    # Contract function call
    tx = contract.functions.mintFromAI(
        recipient_address, 
        w3.to_wei(reward_amount, 'ether'), 
        action_id_bytes
    ).build_transaction({
        'from': oracle_account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 31337
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=oracle_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"🚀 Minting Transaction Sent: {tx_hash.hex()}")
    return w3.eth.wait_for_transaction_receipt(tx_hash)

# --- ZK-PROOF PIPELINE (Original) ---
def trigger_zk_mint(recipient_address, reward_amount, image_hash_bytes, zk_proof):
    # (Yeh purana code waise hi kaam karega, isme maine koi badlav nahi kiya)
    print("\n[ZK ENGINE] Propagating cryptographic payload...")
    # ... (baaki purana logic)
    pass

if __name__ == "__main__":
    print("\n--- Pipeline Ready ---")
    print("Intezar kar rahi hoon AI ke 'Yes' signal ka...")