import os
import math
import time
import numpy as np
import cv2
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from encryption_engine import load_key

load_dotenv()


class SpatialShield:
    def __init__(self):
        self.trust_score = 100

        # ✅ P86 FIXED: .env se location load karo
        lat = float(os.getenv('DEFAULT_LAT', '24.8607'))
        lon = float(os.getenv('DEFAULT_LON', '67.0011'))
        self.last_known_location = (lat, lon)
        self.last_scan_time      = datetime.now(timezone.utc) - timedelta(minutes=2)

        # ✅ P88 FIXED: encryption_engine se key load karo
        # Har baar naya key nahi — persistent key!
        key          = load_key()
        self.cipher  = Fernet(key)
        print(f"✅ SpatialShield initialized")
        print(f"   Location: {lat}, {lon}")

    def fetch_oracle_env_data(self):
        """
        ✅ P90 FIXED: Real API structure
        Abhi simulation hai lekin proper structure
        taake real Chainlink se replace ho sake
        """
        print(f"\n{'🌐 '*5}[ORACLE NODE CONNECTING]{'🌐 '*5}")

        # TODO: Replace with real Chainlink oracle call
        # Real implementation:
        # response = requests.get(CHAINLINK_ORACLE_URL)
        # env_payload = response.json()

        env_payload = {
            "global_temp_anomaly": "+1.15°C",
            "carbon_market_rate":  24.80,
            "satellite_lock":      "NASA_TERRA_SATELLITE_01",
            "carbon_delta_multiplier": 1.45,
            "data_source":         "SIMULATION",  # ✅ honest flag
            "timestamp":           datetime.now(timezone.utc).isoformat()
        }

        print(f"🛰️  Satellite: {env_payload['satellite_lock']}")
        print(f"🌍 Temp Delta: {env_payload['global_temp_anomaly']}")
        print(f"💰 Carbon Rate: ${env_payload['carbon_market_rate']}/ton")
        print(f"⚠️  Source: {env_payload['data_source']}")
        return env_payload

    def calculate_carbon_impact(self, user_action_score, oracle_multiplier):
        print(f"\n{'='*50}")
        print(f"💎 GENESIS CONTRACT: IMPACT CALCULATION")
        print(f"{'='*50}")
        impact_score = user_action_score * oracle_multiplier
        tokens       = impact_score * 0.5
        print(f"   Action Score:    {user_action_score}")
        print(f"   Multiplier:      {oracle_multiplier}")
        print(f"   CO2 Offset:      -{impact_score:.2f} kg")
        print(f"   ECOX Tokens:     {tokens:.4f}")
        return impact_score

    def generate_cyberpunk_heatmap(self, image_path):
        """
        ✅ P87 FIXED: Calibrated threshold
        Magic number 50 → proper calibration
        """
        print(f"\n{'🛡️  '*5}")
        print(f"🔍 SENTINEL SCANNING: {os.path.basename(image_path)}")

        if not os.path.exists(image_path):
            print(f"❌ Image not found!")
            return "ERROR", None

        img = cv2.imread(image_path)
        if img is None:
            return "ERROR", None

        gray              = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap_edges         = cv2.Laplacian(gray, cv2.CV_64F)
        heatmap_intensity = np.var(lap_edges)

        # ✅ P87 FIXED: Calibrated thresholds
        # < 100  = very flat = screen/printed image
        # 100-500 = low detail
        # > 500  = real world texture
        SPOOF_THRESHOLD = 100.0

        print(f"   Texture score: {heatmap_intensity:.2f}")

        if heatmap_intensity < SPOOF_THRESHOLD:
            print(f"{'🚨 '*10}")
            print(f"!!! SPOOF DETECTED (Score: {heatmap_intensity:.2f}) !!!")
            print(f"{'🚨 '*10}")
            return "RED_ALERT", heatmap_intensity

        print(f"   ✅ Organic texture verified!")
        return "GREEN_SIGNAL", heatmap_intensity

    def verify_integrity(self, new_lat, new_lon, current_time=None):
        """
        ✅ P89 FIXED: Realistic velocity threshold
        15 km/min = 900 km/h = airplane speed!
        Real threshold = 2 km/min = 120 km/h (car)
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        print(f"\n{'='*50}")
        print(f"🛰️  SPATIO-TEMPORAL AUDIT")
        print(f"{'='*50}")

        dist      = self.calculate_haversine_distance(
            self.last_known_location[0],
            self.last_known_location[1],
            new_lat, new_lon
        )

        # Handle both aware and naive datetimes
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        if self.last_scan_time.tzinfo is None:
            self.last_scan_time = self.last_scan_time.replace(tzinfo=timezone.utc)

        time_diff = (current_time - self.last_scan_time).total_seconds() / 60
        velocity  = dist / time_diff if time_diff > 0 else 999

        # ✅ P89 FIXED: 2 km/min = 120 km/h realistic!
        MAX_VELOCITY = 2.0

        print(f"   Distance:  {dist:.2f} km")
        print(f"   Time diff: {time_diff:.1f} min")
        print(f"   Velocity:  {velocity:.2f} km/min")
        print(f"   Max allowed: {MAX_VELOCITY} km/min")

        if velocity > MAX_VELOCITY:
            print(f"   🚨 FRAUD: Impossible velocity!")
            return 0

        print(f"   ✅ Location verified!")
        # Update last known location
        self.last_known_location = (new_lat, new_lon)
        self.last_scan_time      = current_time
        return 100

    def calculate_haversine_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a    = (math.sin(dlat/2)**2 +
                math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        return 6371 * (2 * math.asin(math.sqrt(a)))


if __name__ == "__main__":
    shield = SpatialShield()

    print(f"\n{'🚀 '*10}")
    print(f"DAY 8: SPATIAL SHIELD TEST")
    print(f"{'🚀 '*10}")

    # Test 1: Oracle data
    oracle_env = shield.fetch_oracle_env_data()

    # Test 2: Spoof detection
    test_img = 'dataset/val/solar_panels/' + \
        os.listdir('dataset/val/solar_panels/')[0]
    status, score = shield.generate_cyberpunk_heatmap(test_img)
    print(f"\n   Spoof test: {status} ({score:.2f})")

    # Test 3: Location audit — same city (valid)
    print(f"\n--- Test: Same city (valid) ---")
    score1 = shield.verify_integrity(24.8700, 67.0100,
             datetime.now(timezone.utc))
    print(f"   Result: {'✅ VALID' if score1 == 100 else '🚨 FRAUD'}")

    # Test 4: Teleportation (fraud)
    print(f"\n--- Test: Teleportation (fraud) ---")
    score2 = shield.verify_integrity(33.6844, 73.0479,
             datetime.now(timezone.utc))
    print(f"   Result: {'✅ VALID' if score2 == 100 else '🚨 FRAUD CAUGHT!'}")

    # Test 5: Carbon impact
    if status == "GREEN_SIGNAL":
        impact = shield.calculate_carbon_impact(
            user_action_score  = 10,
            oracle_multiplier  = oracle_env['carbon_delta_multiplier']
        )

    print(f"\n{'='*55}")
    print(f"✅ P86 FIXED: GPS from .env!")
    print(f"✅ P87 FIXED: Calibrated threshold 100!")
    print(f"✅ P88 FIXED: Persistent encryption key!")
    print(f"✅ P89 FIXED: 2 km/min velocity!")
    print(f"✅ P90 FIXED: Oracle structure ready!")
    print(f"{'='*55}\n")