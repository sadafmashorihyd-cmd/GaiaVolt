import sys
import cv2
import numpy as np
import fastapi

def status_report():
    print("\n" + "="*40)
    print("   ECOX CORE: DAY 1 MISSION STATUS   ")
    print("="*40)
    print(f"[✔] Python Version: {sys.version[:5]}")
    print(f"[✔] OpenCV (Eyes): {cv2.__version__}")
    print(f"[✔] FastAPI (Brain): {fastapi.__version__}")
    print(f"[✔] NumPy (Math): {np.__version__}")
    print("-" * 40)
    print("STATUS: FOUNDATION IS SOLID!")
    print("Sadaf, hum dunya hilane ke liye tayyar hain.")
    print("="*40 + "\n")

if __name__ == "__main__":
    status_report()