import os
import time
import portalocker
from ai_node_bridge import trigger_ai_mint
from security_engine import is_image_unique

FILE_PATH = os.path.join("contracts", "ai_decision.txt")
IMAGE_TO_MINT = "contracts/image_to_test.jpeg" 

def watch_ai_output():
    print("🧠 AI Monitor: Active and Watching...")
    while True:
        try:
            if os.path.exists(FILE_PATH):
                with open(FILE_PATH, "r+") as f:
                    portalocker.lock(f, portalocker.LOCK_EX)
                    decision = f.read().strip()
                    
                    if decision == "YES":
                        print("✅ AI SIGNAL: YES! Security check shuru...")
                        
                        # Security Engine Integration
                        is_unique, message = is_image_unique(IMAGE_TO_MINT)
                        
                        if not is_unique:
                            print(message)
                            print("❌ Minting blocked due to security alert.")
                        else:
                            print("✅ Security clearance passed. Minting EcoCoin...")
                            # Triggering the minting logic
                            try:
                                tx_receipt = trigger_ai_mint("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", 100, b'\x01' * 32)
                                print("🚀 Transaction Successful!")
                            except Exception as mint_error:
                                print(f"⚠️ Minting Error: {mint_error}")
                        
                        # File reset
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