import os
import time
import portalocker
from ai_node_bridge import trigger_ai_mint

FILE_PATH = os.path.join("contracts", "ai_decision.txt")

def watch_ai_output():
    print("🧠 AI Monitor: Active and Watching...")
    while True:
        try:
            if os.path.exists(FILE_PATH):
                with open(FILE_PATH, "r+") as f:
                    portalocker.lock(f, portalocker.LOCK_EX)
                    decision = f.read().strip()
                    
                    if decision == "YES":
                        print("✅ AI SIGNAL: YES! Minting shuru ho rahi hai...")
                        
                        # Correcting function call
                        try:
                            # 32 bytes ka action ID daalna zaroori hai
                            tx_receipt = trigger_ai_mint("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266", 100, b'\x01' * 32)
                            print("🚀 Transaction Successful!")
                        except Exception as mint_error:
                            print(f"⚠️ Minting Error (Ignore if tx sent): {mint_error}")
                        
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