"""
Day 21 — Three Final Fixes:
Fix 1: INVALIDATED receipts → archive/ folder
Fix 2: CONFIRMED → READY_FOR_MINT (honest status)
Fix 3: Schema validation before any receipt creation
"""

import asyncio
import json
import os
import sys
import glob
import hashlib
import shutil
import contextlib
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RECEIPTS_DIR        = "receipts"
ARCHIVE_DIR         = os.path.join(RECEIPTS_DIR, "archive")
FINGERPRINTS_INDEX  = os.path.join(RECEIPTS_DIR, "fingerprints_index.json")
POLL_INTERVAL_SEC   = 30
PENDING_TIMEOUT_MIN = 10
RPC_URL             = os.getenv("RPC_URL", "https://rpc-amoy.polygon.technology")
CONTRACT_ADDRESS    = os.getenv("CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

os.makedirs(RECEIPTS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR,  exist_ok=True)


# ─────────────────────────────────────────────
#  FIX 2: Receipt Status — Honest Labels
# ─────────────────────────────────────────────
class ReceiptStatus:
    READY_FOR_MINT = "READY_FOR_MINT"  # local engine pass, no tx yet
    CONFIRMED      = "CONFIRMED"        # tx_hash verified on-chain
    FAILED         = "FAILED"           # engine or bridge failed
    INVALIDATED    = "INVALIDATED"      # orphaned or integrity violation


# ─────────────────────────────────────────────
#  FIX 3: Schema Validation
# ─────────────────────────────────────────────

REQUIRED_RECEIPT_FIELDS = [
    "wallet_address",
    "issued_at_utc",
    "co2_nanograms",
    "proof_fingerprint",
    "lovelock_basis_points",
    "off_chain_proof_id",
    "block_number",
    "receipt_hash",
]

REQUIRED_NONZERO_FIELDS = [
    "co2_nanograms",
    "lovelock_basis_points",
    "block_number",
]


def validate_receipt_schema(data: dict) -> tuple:
    """
    Fix 3: Validate before writing any receipt file.
    Returns (is_valid: bool, error_message: str)
    """
    # Check all required fields exist and are not None/empty
    for field in REQUIRED_RECEIPT_FIELDS:
        value = data.get(field)
        if value is None or value == "" or value == "None":
            return False, f"Missing or null field: '{field}'"

    # Check numeric fields are non-zero
    for field in REQUIRED_NONZERO_FIELDS:
        value = data.get(field, 0)
        try:
            if int(value) == 0:
                return False, f"Zero value not allowed: '{field}'"
        except (TypeError, ValueError):
            return False, f"Invalid numeric value: '{field}' = {value}"

    # Wallet address basic check
    wallet = data.get("wallet_address", "")
    if not wallet.startswith("0x") or len(wallet) < 10:
        return False, f"Invalid wallet address: {wallet}"

    # Timestamp check
    try:
        datetime.fromisoformat(data["issued_at_utc"])
    except Exception:
        return False, f"Invalid timestamp: {data.get('issued_at_utc')}"

    return True, "Schema valid"


# ─────────────────────────────────────────────
#  FIX 1: Archive INVALIDATED receipts
# ─────────────────────────────────────────────

def archive_invalidated(path: str) -> str:
    """Move INVALIDATED receipt to archive/ folder"""
    filename = os.path.basename(path)
    archive_path = os.path.join(ARCHIVE_DIR, filename)

    # Add archive timestamp to receipt
    try:
        with open(path, "r") as f:
            receipt = json.load(f)
        receipt["archived_at"] = datetime.now(timezone.utc).isoformat()
        with open(path, "w") as f:
            json.dump(receipt, f, indent=2)
    except Exception:
        pass

    shutil.move(path, archive_path)
    print(f"[Archive] 📦 Moved to archive: {filename}")
    return archive_path


def archive_all_existing_invalidated():
    """On startup: move all old INVALIDATED files to archive"""
    pattern = os.path.join(RECEIPTS_DIR, "*_INVALIDATED.json")
    files   = glob.glob(pattern)
    if files:
        print(f"[Archive] Moving {len(files)} old INVALIDATED receipt(s) to archive...")
        for path in files:
            archive_invalidated(path)
    else:
        print("[Archive] No old INVALIDATED receipts to archive")


# ─────────────────────────────────────────────
#  FILE LOCKING
# ─────────────────────────────────────────────

@contextlib.contextmanager
def locked_file(path: str, mode: str = "r"):
    f = open(path, mode, encoding="utf-8")
    try:
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 256)
            except OSError:
                time.sleep(0.1)
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 256)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        yield f
    finally:
        try:
            if sys.platform == "win32":
                import msvcrt
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 256)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        f.close()


def load_receipt(path: str) -> dict:
    with locked_file(path, "r") as f:
        return json.load(f)


def save_receipt(path: str, receipt: dict):
    """Validate schema before saving — Fix 3"""
    is_valid, error = validate_receipt_schema(receipt)
    if not is_valid and receipt.get("status") not in (
        ReceiptStatus.FAILED,
        ReceiptStatus.INVALIDATED
    ):
        print(f"[SchemaValidator] ❌ ABORT save — {error}")
        raise ValueError(f"Receipt schema invalid: {error}")

    tmp = path + ".tmp"
    with locked_file(tmp, "w") as f:
        json.dump(receipt, f, indent=2, default=str)
    if os.path.exists(path):
        os.remove(path)
    os.rename(tmp, path)


# ─────────────────────────────────────────────
#  FINGERPRINT INDEX
# ─────────────────────────────────────────────

class FingerprintIndex:
    def __init__(self):
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(FINGERPRINTS_INDEX):
            with open(FINGERPRINTS_INDEX, "r") as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save(self):
        tmp = FINGERPRINTS_INDEX + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.index, f, indent=2)
        if os.path.exists(FINGERPRINTS_INDEX):
            os.remove(FINGERPRINTS_INDEX)
        os.rename(tmp, FINGERPRINTS_INDEX)

    def is_duplicate(self, fp: str) -> bool:
        return fp in self.index

    def register(self, fp: str, receipt_id: str, wallet: str):
        self.index[fp] = {
            "receipt_id": receipt_id,
            "wallet": wallet,
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        self._save()

    def revoke(self, fp: str):
        if fp in self.index:
            del self.index[fp]
            self._save()


fingerprint_index = FingerprintIndex()


# ─────────────────────────────────────────────
#  TX INTEGRITY VERIFICATION
# ─────────────────────────────────────────────

def verify_on_chain_tx(tx_hash: str, receipt: dict) -> tuple:
    if not tx_hash or tx_hash in (None, "None", "Pending Day 22"):
        return "pending", "No tx hash"
    try:
        tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
        if tx_receipt is None:
            return "pending", "Not mined yet"
        if tx_receipt["status"] != 1:
            return "failed", f"TX reverted: {tx_hash}"

        tx_data         = w3.eth.get_transaction(tx_hash)
        expected_wallet = receipt.get("wallet_address", "").lower()
        actual_to       = (tx_data.get("to") or "").lower()

        if expected_wallet and actual_to and expected_wallet != actual_to:
            return "integrity_violation", \
                f"Wallet mismatch: {expected_wallet[:16]} vs {actual_to[:16]}"

        return "success", "Verified"
    except Exception as e:
        return "not_found", str(e)


# ─────────────────────────────────────────────
#  RECEIPT HELPERS
# ─────────────────────────────────────────────

def get_active_receipts() -> list:
    """Only READY_FOR_MINT — not CONFIRMED (those are done)"""
    return glob.glob(os.path.join(RECEIPTS_DIR, "*_READY_FOR_MINT.json"))


def get_confirmed_receipts() -> list:
    return glob.glob(os.path.join(RECEIPTS_DIR, "*_CONFIRMED.json"))


def check_receipt_age(receipt: dict) -> float:
    issued = datetime.fromisoformat(receipt["issued_at_utc"])
    if issued.tzinfo is None:
        issued = issued.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - issued).total_seconds() / 60


def invalidate_and_archive(path: str, receipt: dict, reason: str):
    fp = receipt.get("proof_fingerprint", "")
    if fp:
        fingerprint_index.revoke(fp)

    receipt["status"]              = ReceiptStatus.INVALIDATED
    receipt["invalidated_at_utc"]  = datetime.now(timezone.utc).isoformat()
    receipt["invalidation_reason"] = reason

    fields = {k: v for k, v in receipt.items()
              if k not in ("receipt_hash", "oracle_signature")}
    receipt["receipt_hash"] = hashlib.sha256(
        json.dumps(fields, sort_keys=True, default=str).encode()
    ).hexdigest()

    inv_path = path.replace("_READY_FOR_MINT.json", "_INVALIDATED.json")
    if "_CONFIRMED.json" in path:
        inv_path = path.replace("_CONFIRMED.json", "_INVALIDATED.json")

    # Save then archive immediately
    with open(inv_path, "w") as f:
        json.dump(receipt, f, indent=2, default=str)
    if os.path.exists(path):
        os.remove(path)

    archive_invalidated(inv_path)
    print(f"[Monitor] Reason: {reason}")


def upgrade_to_confirmed(path: str, receipt: dict, tx_hash: str):
    """READY_FOR_MINT → CONFIRMED after real tx verified"""
    receipt["status"]            = ReceiptStatus.CONFIRMED
    receipt["on_chain_tx"]       = tx_hash
    receipt["chain_verified_at"] = datetime.now(timezone.utc).isoformat()

    fields = {k: v for k, v in receipt.items()
              if k not in ("receipt_hash", "oracle_signature")}
    receipt["receipt_hash"] = hashlib.sha256(
        json.dumps(fields, sort_keys=True, default=str).encode()
    ).hexdigest()

    new_path = path.replace("_READY_FOR_MINT.json", "_CONFIRMED.json")
    save_receipt(new_path, receipt)
    if os.path.exists(path):
        os.remove(path)
    print(f"[Monitor] ✅ CONFIRMED: {os.path.basename(new_path)}")


# ─────────────────────────────────────────────
#  RECOVERY SCAN
# ─────────────────────────────────────────────

async def recovery_scan():
    """Check archived INVALIDATED receipts — maybe tx settled"""
    pattern    = os.path.join(ARCHIVE_DIR, "*_INVALIDATED.json")
    invalidated = glob.glob(pattern)

    if not invalidated:
        print("[Recovery] Archive empty — nothing to recover")
        return

    print(f"[Recovery] Scanning {len(invalidated)} archived receipt(s)...")
    for path in invalidated:
        try:
            receipt = load_receipt(path)
            reason  = receipt.get("invalidation_reason", "")
            tx      = receipt.get("on_chain_tx")

            if "integrity_violation" in reason:
                print(f"[Recovery] ⛔ Skip integrity violation: {os.path.basename(path)}")
                continue

            if tx and tx not in (None, "None", "Pending Day 22"):
                status, msg = verify_on_chain_tx(tx, receipt)
                if status == "success":
                    receipt["status"]          = ReceiptStatus.CONFIRMED
                    receipt["recovered_at"]    = datetime.now(timezone.utc).isoformat()
                    receipt.pop("invalidation_reason", None)
                    receipt.pop("invalidated_at_utc", None)

                    new_path = os.path.join(
                        RECEIPTS_DIR,
                        os.path.basename(path).replace("_INVALIDATED.json", "_CONFIRMED.json")
                    )
                    save_receipt(new_path, receipt)
                    os.remove(path)
                    print(f"[Recovery] ✅ Restored: {os.path.basename(new_path)}")
                else:
                    print(f"[Recovery] Still invalid: {msg}")
            else:
                print(f"[Recovery] No tx_hash — Day 22 pending")
        except Exception as e:
            print(f"[Recovery] Error: {e}")


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

async def monitor_loop():
    print("[Monitor] 🔍 BULLETPROOF Monitor — Final Version")
    print(f"[Monitor] Status flow: READY_FOR_MINT → CONFIRMED")
    print(f"[Monitor] Invalid flow: → INVALIDATED → archive/\n")

    # Startup: archive old INVALIDATED, run recovery
    archive_all_existing_invalidated()
    print()
    await recovery_scan()
    print()

    while True:
        active    = get_active_receipts()
        confirmed = get_confirmed_receipts()

        print(f"[Monitor] Active(READY): {len(active)} | Confirmed: {len(confirmed)}")

        for path in active:
            try:
                receipt = load_receipt(path)
                age_min = check_receipt_age(receipt)
                tx      = receipt.get("on_chain_tx")

                print(f"\n[Monitor] → {os.path.basename(path)} ({age_min:.1f} min)")

                if tx and tx not in (None, "None", "Pending Day 22"):
                    status, reason = verify_on_chain_tx(tx, receipt)
                    if status == "success":
                        upgrade_to_confirmed(path, receipt, tx)
                    elif status in ("failed", "integrity_violation"):
                        invalidate_and_archive(path, receipt, reason)
                    elif status == "pending" and age_min > PENDING_TIMEOUT_MIN:
                        invalidate_and_archive(path, receipt,
                            f"TX timeout: {age_min:.1f} min")
                else:
                    remaining = max(0, PENDING_TIMEOUT_MIN - age_min)
                    if age_min > PENDING_TIMEOUT_MIN:
                        invalidate_and_archive(path, receipt,
                            f"Orphaned: no TX after {age_min:.1f} min")
                    else:
                        print(f"  Waiting for Day 22 mint — {remaining:.1f} min left")

            except Exception as e:
                print(f"[Monitor] Error: {e}")

        print(f"\n[Monitor] Next check in {POLL_INTERVAL_SEC}s...\n")
        await asyncio.sleep(POLL_INTERVAL_SEC)


# ─────────────────────────────────────────────
#  SINGLE CHECK
# ─────────────────────────────────────────────

def run_single_check():
    active    = get_active_receipts()
    confirmed = get_confirmed_receipts()
    print(f"[Check] READY_FOR_MINT: {len(active)} | CONFIRMED: {len(confirmed)}\n")

    for path in active + confirmed:
        receipt = load_receipt(path)
        age_min = check_receipt_age(receipt)
        tx      = receipt.get("on_chain_tx")
        fp      = receipt.get("proof_fingerprint", "")

        print(f"  File   : {os.path.basename(path)}")
        print(f"  Status : {receipt.get('status')}")
        print(f"  Age    : {age_min:.1f} min")
        print(f"  TX     : {tx}")
        print(f"  Dup    : {fingerprint_index.is_duplicate(fp)}")
        if age_min > PENDING_TIMEOUT_MIN and not tx:
            print(f"  ⚠️  Would be invalidated + archived")
        print()


if __name__ == "__main__":
    if "--check" in sys.argv:
        run_single_check()
    elif "--recover" in sys.argv:
        asyncio.run(recovery_scan())
    else:
        asyncio.run(monitor_loop())