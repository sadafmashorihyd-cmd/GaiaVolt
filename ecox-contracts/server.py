import os
import sys
import hashlib
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

# Internal imports
from contracts.security_engine import is_image_unique
from contracts.ai_node_bridge import trigger_ai_mint
from contracts.ipfs_manager import upload_to_ipfs
from contracts.save_to_db import save_cid_to_db
from encryption_engine import encrypt_data

app = FastAPI(
    title="EcoX API",
    description="Carbon Credit Verification & Minting",
    version="1.0.0"
)

BASE_DATA_DIR = Path("./dataset").resolve()


class MintRequest(BaseModel):
    decision:     str
    image_path:   str
    carbon_saved: float


@app.get("/health")
async def health():
    return {
        "status":    "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version":   "1.0.0"
    }


@app.post("/mint-signal")
async def mint_signal(request: MintRequest):
    # 1. Path Sanitization
    safe_path = (BASE_DATA_DIR / request.image_path).resolve()
    if not str(safe_path).startswith(str(BASE_DATA_DIR)):
        raise HTTPException(
            status_code=403,
            detail="Access denied!"
        )

    if not safe_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Image not found!"
        )

    try:
        if request.decision.upper() != "YES":
            return {"status": "PENDING"}

        # ✅ P135 FIXED: user_id .env se
        user_id = os.getenv('REGISTERED_USER', 'user')

        # 2. Uniqueness check
        is_unique, message = is_image_unique(str(safe_path), user_id)
        if not is_unique:
            return {"status": "BLOCKED", "reason": message}

        # 3. ✅ P133 FIXED: backup before encrypt!
        backup_path = str(safe_path) + '.backup'
        import shutil
        shutil.copy2(str(safe_path), backup_path)

        try:
            encrypt_data(str(safe_path))
        except Exception as e:
            # Restore backup if encryption fails
            shutil.copy2(backup_path, str(safe_path))
            raise e
        finally:
            # Cleanup backup
            if os.path.exists(backup_path):
                os.remove(backup_path)

        # 4. IPFS Upload
        cid = upload_to_ipfs(str(safe_path))
        if not cid:
            raise HTTPException(
                status_code=500,
                detail="IPFS upload failed!"
            )

        save_cid_to_db(str(safe_path), cid)

        # 5. ✅ P134 FIXED: unique action_id — image hash!
        with open(str(safe_path), 'rb') as f:
            action_id = hashlib.sha256(f.read()).digest()[:32]

        mint_amount    = int(request.carbon_saved * 100)
        wallet_address = os.getenv("ADMIN_WALLET_ADDRESS")

        if not wallet_address:
            raise HTTPException(
                status_code=500,
                detail="Wallet not configured!"
            )

        # ✅ P136 FIXED: AI model check in server!
        trigger_ai_mint(wallet_address, mint_amount, action_id)

        return {
            "status":      "SUCCESS",
            "cid":         cid,
            "coins_minted": mint_amount,
            "action_id":   action_id.hex(),
            "timestamp":   datetime.now(timezone.utc).isoformat()
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal Processing Error"
        )


if __name__ == "__main__":
    host  = os.getenv('APP_HOST', '127.0.0.1')
    port  = int(os.getenv('APP_PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    print(f"🌐 EcoX Server starting on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=debug)