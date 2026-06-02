import json
import os
import hashlib
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()


def create_metadata_bundle(image_path, lat=None, lon=None, weather_data=None):
    """
    ✅ P71 FIXED: weather .env se ya API se
    ✅ P72 FIXED: processed/ folder nahi — val/ ya train/
    """
    # ✅ P71 FIXED: weather hardcoded nahi
    if weather_data is None:
        weather_data = os.getenv('WEATHER_DATA', 'Unknown')

    # ✅ P86 FIXED: GPS .env se
    if lat is None:
        lat = float(os.getenv('DEFAULT_LAT', '24.8607'))
    if lon is None:
        lon = float(os.getenv('DEFAULT_LON', '67.0011'))

    # SHA-256 fingerprint
    sha256 = hashlib.sha256()
    with open(image_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    img_hash = sha256.hexdigest()

    metadata = {
        "file_name":  os.path.basename(image_path),
        "file_hash":  img_hash,
        "location":   {"lat": lat, "lon": lon},
        "weather":    weather_data,
        "verified":   True,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "version":    "EcoX-1.0"
    }

    json_path = os.path.splitext(image_path)[0] + ".json"

    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=4)

    print(f"   ✅ {os.path.basename(image_path)} → metadata saved")
    return metadata


def run_metadata_pipeline(dataset_dir=None):
    """
    ✅ P72 FIXED: train_balanced use karo — processed/ nahi!
    """
    from src.utils.constants import CONFIG
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if dataset_dir is None:
        dataset_dir = CONFIG['TRAIN_DIR']  # ✅ train_balanced!

    print(f"\n{'='*55}")
    print(f"📋 METADATA GENERATOR")
    print(f"{'='*55}")
    print(f"   Dataset: {dataset_dir}")

    if not os.path.exists(dataset_dir):
        print(f"❌ Dataset not found: {dataset_dir}")
        return

    total = 0
    # Sample — sirf 2 per class (full dataset bohot time lega)
    for class_name in sorted(os.listdir(dataset_dir)):
        if class_name.startswith('_'):
            continue

        class_dir = os.path.join(dataset_dir, class_name)
        if not os.path.isdir(class_dir):
            continue

        images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:2]

        for filename in images:
            img_path = os.path.join(class_dir, filename)
            create_metadata_bundle(img_path)
            total += 1

    print(f"\n   Total metadata: {total}")
    print(f"{'='*55}\n")
    return total


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    run_metadata_pipeline()

    print(f"✅ P71 FIXED: weather from .env!")
    print(f"✅ P72 FIXED: train_balanced not processed/!")