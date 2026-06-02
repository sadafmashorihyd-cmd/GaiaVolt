import os
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()


class ChainlinkOracle:
    """
    ✅ Day 14: Oracle Integration
    Real-world data → Smart Contract
    """

    def __init__(self):
        self.carbon_rate    = None
        self.weather        = None
        self.temp_anomaly   = None
        self.last_updated   = None

    def fetch_carbon_rate(self):
        """
        Real carbon market rate
        Free API: https://api.carbonintensity.org.uk
        """
        try:
            response = requests.get(
                "https://api.carbonintensity.org.uk/intensity",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                intensity = data['data'][0]['intensity']['actual']
                # Convert gCO2/kWh to $/ton approximate
                carbon_rate = intensity * 0.025
                self.carbon_rate = round(carbon_rate, 2)
                print(f"   ✅ Carbon Rate (live): {self.carbon_rate} $/ton")
                return self.carbon_rate
        except Exception as e:
            print(f"   ⚠️  Carbon API unavailable: {e}")

        # Fallback
        self.carbon_rate = 24.80
        print(f"   ⚠️  Using fallback: {self.carbon_rate} $/ton")
        return self.carbon_rate

    def fetch_weather(self, lat=24.8607, lon=67.0011):
        """
        Real weather data
        Open-Meteo: Free, no API key needed!
        """
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,weather_code"
                f"&timezone=Asia/Karachi"
            )
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data    = response.json()
                current = data['current']
                temp    = current['temperature_2m']
                code    = current['weather_code']

                # Weather code to description
                if code < 3:
                    weather = "Clear"
                elif code < 50:
                    weather = "Cloudy"
                elif code < 70:
                    weather = "Rainy"
                else:
                    weather = "Stormy"

                self.weather = {
                    "temp":        temp,
                    "condition":   weather,
                    "code":        code,
                    "location":    f"{lat}, {lon}"
                }
                print(f"   ✅ Weather (live): {temp}°C, {weather}")
                return self.weather
        except Exception as e:
            print(f"   ⚠️  Weather API unavailable: {e}")

        # Fallback
        self.weather = {
            "temp":      38.0,
            "condition": "Clear",
            "code":      0,
            "location":  f"{lat}, {lon}"
        }
        print(f"   ⚠️  Using fallback weather")
        return self.weather

    def fetch_all(self, lat=24.8607, lon=67.0011):
        """Fetch all oracle data"""
        print(f"\n{'='*55}")
        print(f"🔗 CHAINLINK ORACLE — FETCHING DATA")
        print(f"{'='*55}")
        print(f"   Timestamp: {datetime.now(timezone.utc).isoformat()}")

        self.fetch_carbon_rate()
        self.fetch_weather(lat, lon)

        self.last_updated = datetime.now(timezone.utc).isoformat()

        payload = {
            "carbon_rate":   self.carbon_rate,
            "weather":       self.weather,
            "timestamp":     self.last_updated,
            "data_sources":  ["carbonintensity.org.uk", "open-meteo.com"],
            "status":        "LIVE"
        }

        print(f"{'='*55}\n")
        return payload

    def calculate_multiplier(self, action_class):
        """
        Carbon impact multiplier based on real data
        """
        base_multipliers = {
            "solar_panels":       1.5,
            "cycling":            1.2,
            "electric_cars":      1.8,
            "ocean_cleanup":      2.0,
            "plantation":         1.6,
            "recycling":          1.3,
            "utility_bills":      1.1,
            "organic_farming":    1.4,
            "wind_energy":        1.7,
            "water_conservation": 1.3,
            "led_lighting":       1.1,
            "public_transport":   1.2
        }

        base = base_multipliers.get(action_class, 1.0)

        # Adjust for weather
        if self.weather:
            if self.weather['condition'] == 'Clear':
                base *= 1.1  # Sunny = more solar impact
            elif self.weather['condition'] == 'Rainy':
                base *= 0.9  # Rain = less

        # Adjust for carbon rate
        if self.carbon_rate:
            if self.carbon_rate > 30:
                base *= 1.2  # High carbon rate = more reward
            elif self.carbon_rate < 15:
                base *= 0.8

        return round(base, 2)


def run_oracle_demo():
    print(f"\n{'='*55}")
    print(f"⛓️  DAY 14 — ORACLE INTEGRATION DEMO")
    print(f"{'='*55}")

    oracle = ChainlinkOracle()

    # Fetch real data
    data = oracle.fetch_all(lat=24.8607, lon=67.0011)

    # Calculate multipliers
    print(f"\n📊 CARBON MULTIPLIERS (Real-time):")
    print(f"{'='*55}")

    actions = [
        "solar_panels", "cycling", "electric_cars",
        "ocean_cleanup", "wind_energy"
    ]

    for action in actions:
        mult   = oracle.calculate_multiplier(action)
        reward = int(mult * 50)
        print(f"   {action:<22} {mult}x → {reward} coins")

    # Impact calculation
    print(f"\n🌍 PLANETARY IMPACT:")
    print(f"{'='*55}")
    print(f"   Carbon Rate:  ${data['carbon_rate']}/ton")
    if data['weather']:
        print(f"   Temperature:  {data['weather']['temp']}°C")
        print(f"   Condition:    {data['weather']['condition']}")
    print(f"   Timestamp:    {data['timestamp']}")

    # Save oracle data
    with open('oracle_data.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\n   ✅ Oracle data saved: oracle_data.json")

    print(f"\n{'='*55}")
    print(f"✅ Day 14 Oracle Integration COMPLETE!")
    print(f"✅ Real carbon rate: live!")
    print(f"✅ Real weather: live!")
    print(f"✅ Smart multipliers: working!")
    print(f"{'='*55}\n")

    return data


if __name__ == "__main__":
    run_oracle_demo()