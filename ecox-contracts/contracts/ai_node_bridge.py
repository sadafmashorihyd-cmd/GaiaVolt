import os
import json
from web3 import Web3
from dotenv import load_dotenv
from security_engine import check_reward_eligibility

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

LOCAL_RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
ABI_PATH = os.path.join(BASE_DIR, "artifacts", "contracts", "EcoCoin.sol", "EcoCoin.json")

w3 = Web3(Web3.HTTPProvider(LOCAL_RPC_URL))
with open(ABI_PATH, "r") as f: contract_abi = json.load(f)["abi"]
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def trigger_ai_mint(recipient, amount, action_id):
    oracle_key = os.getenv("ORACLE_PRIVATE_KEY")
    acct = w3.eth.account.from_key(oracle_key)
    tx = contract.functions.mintFromAI(recipient, w3.to_wei(amount, 'ether'), action_id).build_transaction({
        'from': acct.address, 'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 200000, 'gasPrice': w3.eth.gas_price, 'chainId': 31337
    })
    signed = w3.eth.account.sign_transaction(tx, oracle_key)
    return w3.eth.wait_for_transaction_receipt(w3.eth.send_raw_transaction(signed.raw_transaction))

if __name__ == "__main__":
    print("\n--- 🛡️ EcoX AI Engine Starting ---")
    is_eligible, msg = check_reward_eligibility("image_to_test.jpeg", "Sadaf_001")
    if is_eligible:
        print(f"✅ {msg}")
        trigger_ai_mint("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", 10, b'eco_action_001')
        print("🎉 EcoCoin Minted Successfully!")
    else:
        print(f"❌ {msg}")