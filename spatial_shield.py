import os
import hashlib
import json
import time
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime, timedelta
import math
import numpy as np 
import cv2 
from cryptography.fernet import Fernet 

class SpatialShield:
    def __init__(self):
        self.trust_score = 100
        # Mocking last scan for Velocity Audit (Karachi 2 mins ago)
        self.last_known_location = (24.8607, 67.0011) 
        self.last_scan_time = datetime.now() - timedelta(minutes=2)
        
        # Military Encryption Setup
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    # --- 1. THE ADVANCED ORACLE BRIDGE (NASA & Global Data) ---
    def fetch_oracle_env_data(self):
        """Bridges Blockchain to NASA/Satellite Global Climate Data"""
        print("\n" + "🌐 " * 5 + "[CONNECTING TO CHAINLINK ORACLE NODES]" + " 🌐" * 5)
        # Simulation: Real-world data stream for the video
        env_payload = {
            "global_temp_anomaly": "+1.15°C",
            "carbon_market_rate": 24.80, # Live Price
            "satellite_lock": "NASA_TERRA_SATELLITE_01",
            "carbon_delta_multiplier": 1.45 # Impact Factor
        }
        time.sleep(1) # Visual effect for video
        print(f"🛰️  Satellite Lock: {env_payload['satellite_lock']}")
        print(f"🌍 Global Temp Delta: {env_payload['global_temp_anomaly']}")
        print(f"💰 Live Carbon Rate: ${env_payload['carbon_market_rate']}/ton")
        return env_payload

    # --- 2. CARBON IMPACT LOGIC (Real-Time Delta) ---
    def calculate_carbon_impact(self, user_action_score, oracle_multiplier):
        """Calculates real-time impact delta for the Genesis Contract"""
        print("\n--- 💎 [GENESIS CONTRACT]: REAL-TIME IMPACT CALC ---")
        impact_score = user_action_score * oracle_multiplier
        print(f"📉 Action Impact: -{impact_score:.2f} kg CO2 Offset.")
        print(f"🏆 Reward Calculation: {impact_score * 0.5:.4f} ECOX Tokens.")
        return impact_score

    # --- 3. CYBERPUNK VISUAL AUDIT (Fraud Detection) ---
    def generate_cyberpunk_heatmap(self, image_path):
        img = cv2.imread(image_path)
        if img is None: return "ERROR", None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap_edges = cv2.Laplacian(gray, cv2.CV_64F)
        heatmap_intensity = np.var(lap_edges)
        
        print("\n" + "🛡️  " * 10)
        print("🔍 [SENTINEL SCANNING PIXEL DEPTH]...")
        
        if heatmap_intensity < 50: # Spoof Detected
            print("\n" + "🚨 " * 15)
            print("!!! [CYBERPUNK RED ALERT]: SPOOF ATTEMPT DETECTED !!!")
            print(f"!!! Forensic Score: {heatmap_intensity:.2f} (FLAT TEXTURE) !!!")
            print("🚨 " * 15)
            return "RED_ALERT", heatmap_intensity
        
        print(f"✅ [STATUS]: Organic Texture Verified (Score: {heatmap_intensity:.2f})")
        return "GREEN_SIGNAL", heatmap_intensity

    # --- 4. SPATIO-TEMPORAL AUDIT ---
    def verify_integrity(self, new_lat, new_lon, current_time):
        print("\n--- 🛰️ [GOD-EYE]: SPATIO-TEMPORAL AUDIT ---")
        dist = self.calculate_haversine_distance(self.last_known_location[0], self.last_known_location[1], new_lat, new_lon)
        time_diff = (current_time - self.last_scan_time).total_seconds() / 60
        
        velocity = dist / time_diff if time_diff > 0 else 999
        if velocity > 15:
            print(f"🚨 [FRAUD]: Impossible Velocity ({velocity:.2f} km/min)!")
            print("❌ Error: Spatial Metadata Mismatch. (Karachi-Hyd distance breach)")
            return 0
        return 100

    def calculate_haversine_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return 6371 * (2 * math.asin(math.sqrt(a)))

# --- THE VICTORY DEMO EXECUTION ---
if __name__ == "__main__":
    shield = SpatialShield()
    test_img = 'dataset/utility_bills/my_live_test.jpg' 
    
    print("\n" + "🚀 " * 15)
    print("DAY 14: THE VICTORY DEMO (ORACLE & IMPACT)")
    print("🚀 " * 15)

    # STEP 1: Fetch Oracle Data (Live Environmental Context)
    oracle_env = shield.fetch_oracle_env_data()

    # STEP 2: AI Scanning (Sadaf vs Sentinel)
    status, score = shield.generate_cyberpunk_heatmap(test_img)

    # STEP 3: Location Audit (Simulating Hyderabad Scan after Karachi)
    hyd_lat, hyd_lon = 25.3960, 68.3578
    st_score = shield.verify_integrity(hyd_lat, hyd_lon, datetime.now())

    # FINAL VERDICT
    print("\n" + "="*55)
    if status == "RED_ALERT" or st_score == 0:
        print("🚫 [BLOCKCHAIN]: Genesis Contract ABORTED.")
        print("⚠️ [VERDICT]: Fraudulent Action Purged. No Impact Generated.")
    else:
        impact = shield.calculate_carbon_impact(user_action_score=10, 
                                              oracle_multiplier=oracle_env['carbon_delta_multiplier'])
        print("💎 [BLOCKCHAIN]: Genesis Contract EXECUTED.")
        print(f"🌍 Planet Protected. Final Impact Delta: {impact:.2f}")
    print("="*55)

    print("\n[ STATUS : ECOX GLOBAL ORACLE ACTIVE & UNBEATABLE ]")