import sys
import os
import time
import portalocker

# Contracts folder ko path mein add karein taake files mil sakein
sys.path.append(os.path.join(os.getcwd(), 'contracts'))

# Ab imports (ab ye 'contracts' folder ke andar se files uthayenge)
from ai_node_bridge import trigger_ai_mint
from security_engine import is_image_unique
from ipfs_manager import upload_to_ipfs
from save_to_db import save_cid_to_db

# File Paths
FILE_PATH = os.path.join("contracts", "ai_decision.txt")
IMAGE_TO_MINT = os.path.join("contracts", "image_to_test.jpeg")

def watch_ai_output():
    print("🧠 AI Monitor: Active and Watching...")
    while True:
        # Is line ko yahan paste karein (while ke bilkul niche)
        print("Checking file...") 
        
        try:
            if os.path.exists(FILE_PATH):
                with open(FILE_PATH, "r+") as f:
                    # ... baqi ka code ...
        
                    portalocker.lock(f, portalocker.LOCK_EX)
                    decision = f.read().strip().upper()  # .upper() lagane se "yes", "Yes", "YES" sab chal jayenge                    
                    if decision == "YES":
                        print("✅ AI SIGNAL: YES! Security check shuru...")
                        
                        # Security Check
                        is_unique, message = is_image_unique(IMAGE_TO_MINT)
                        
                        if not is_unique:
                            print(message)
                            print("❌ Minting blocked.")
                        else:
                            print("✅ Security clearance passed.")
                            cid = upload_to_ipfs(IMAGE_TO_MINT)
                            if cid:
                                save_cid_to_db(IMAGE_TO_MINT, cid)
                                print(f"🔗 CID Linked: {cid}")
                                try:
                                    trigger_ai_mint("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", 100, b'\x01' * 32)
                                    print("🚀 Transaction Successful!")
                                except Exception as e:
                                    print(f"⚠️ Minting Error: {e}")
                        
                        f.seek(0)
                        f.write("PENDING")
                        f.truncate()
                    
                    portalocker.unlock(f)
                time.sleep(2)
        except Exception as e:
            print(f"⚠️ System Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    watch_ai_output()