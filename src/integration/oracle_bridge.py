import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from anti_cheat import EcoXShield

load_dotenv()

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/oracle_bridge.log',
    level=logging.INFO,
    format='%(asctime)s UTC — %(levelname)s — %(message)s'
)


class OracleBridge:
    def __init__(self):
        self.shield = EcoXShield()
        self.logger = logging.getLogger("OracleBridge")

        # ✅ Day 14: Real oracle data!
        try:
            from oracle_integration import ChainlinkOracle
            self.oracle = ChainlinkOracle()
            print(f"🔗 Oracle Bridge initialized")
            print(f"   User:   {self.shield.registered_user}")
            print(f"   Oracle: ChainlinkOracle ready ✅")
        except Exception as e:
            self.oracle = None
            print(f"⚠️  Oracle unavailable: {e}")

    def transmit_to_blockchain(
        self,
        image_path,
        prediction_label,
        confidence,
        extracted_text,
        recipient=None
    ):
        print(f"\n{'='*55}")
        print(f"🔗 ORACLE BRIDGE — {prediction_label}")
        print(f"{'='*55}")

        # 1. Security check
        audit_result = self.shield.verify_full_protocol(
            image_path, extracted_text
        )

        if audit_result != "APPROVED":
            self.logger.error(
                f"BLOCKED: {audit_result} | "
                f"Label: {prediction_label}"
            )
            return {"status": "BLOCKED", "reason": audit_result}

        # ✅ Day 14: Real oracle data!
        carbon_rate = 24.80
        multiplier  = 1.0
        weather     = None

        if self.oracle:
            try:
                oracle_data = self.oracle.fetch_all()
                carbon_rate = oracle_data['carbon_rate']
                multiplier  = self.oracle.calculate_multiplier(
                    prediction_label
                )
                weather     = oracle_data.get('weather')
            except Exception as e:
                print(f"   ⚠️  Oracle fetch failed: {e}")

        transaction_payload = {
            "label":       prediction_label,
            "confidence":  float(confidence),
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "validator":   "God-Eye-AI-v1",
            "recipient":   recipient or os.getenv('ADMIN_WALLET_ADDRESS',''),
            "carbon_rate": carbon_rate,
            "multiplier":  multiplier,
            "weather":     weather,
        }

        self.logger.info(f"SUCCESS: {json.dumps(transaction_payload)}")

        print(f"   Label:       {prediction_label} ✅")
        print(f"   Confidence:  {confidence:.1f}% ✅")
        print(f"   Timestamp:   {transaction_payload['timestamp']} ✅")
        print(f"   Carbon Rate: ${carbon_rate}/ton ✅")
        print(f"   Multiplier:  {multiplier}x ✅")
        if weather:
            print(f"   Weather:     {weather.get('temp')}°C, {weather.get('condition')} ✅")
        print(f"   Status:      APPROVED ✅")
        print(f"{'='*55}\n")

        return {"status": "SUCCESS", "payload": transaction_payload}


if __name__ == "__main__":
    bridge = OracleBridge()

    test_img = 'scripts/address_mismatch_test_bill_2026.jpeg'
    user     = bridge.shield.registered_user

    result = bridge.transmit_to_blockchain(
        image_path       = test_img,
        prediction_label = "solar_panels",
        confidence       = 99.9,
        extracted_text   = f"May 2026 {user}"
    )
    print(f"Result: {result['status']}")