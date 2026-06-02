import os
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()


def dms_to_decimal(dms, ref):
    """✅ P69 FIXED: DMS to decimal"""
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal


def extract_gps(image_path):
    """✅ P68 FIXED: getexif() not _getexif()"""
    try:
        img  = Image.open(image_path)
        exif = img.getexif()  # ✅ modern API
        if not exif:
            return None, None, None

        gps_info = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'GPSInfo':
                for gps_tag_id, gps_val in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_val

        if not gps_info:
            return None, None, None

        lat = lon = timestamp = None

        if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
            lat = dms_to_decimal(
                gps_info['GPSLatitude'],
                gps_info['GPSLatitudeRef']
            )

        if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
            lon = dms_to_decimal(
                gps_info['GPSLongitude'],
                gps_info['GPSLongitudeRef']
            )

        if 'GPSTimeStamp' in gps_info:
            ts = gps_info['GPSTimeStamp']
            timestamp = f"{int(ts[0]):02d}:{int(ts[1]):02d}:{int(ts[2]):02d} UTC"

        return lat, lon, timestamp

    except Exception as e:
        print(f"   EXIF error: {e}")
        return None, None, None


def verify_geo_location(image_path, allowed_lat_range, allowed_lon_range):
    """✅ P70 FIXED: range actually checked!"""
    print(f"\n{'='*50}")
    print(f"🛰️  GPS VERIFICATION")
    print(f"{'='*50}")
    print(f"   Image: {os.path.basename(image_path)}")

    lat, lon, timestamp = extract_gps(image_path)

    if lat is None or lon is None:
        print(f"   ⚠️  No GPS EXIF data")
        return False, "No GPS data — use device GPS"

    print(f"   GPS: {lat:.4f}, {lon:.4f}")
    if timestamp:
        print(f"   Time: {timestamp}")

    # ✅ P70 FIXED: actually check range!
    lat_min, lat_max = allowed_lat_range
    lon_min, lon_max = allowed_lon_range

    if not (lat_min <= lat <= lat_max):
        return False, f"❌ Latitude out of range: {lat:.4f}"

    if not (lon_min <= lon <= lon_max):
        return False, f"❌ Longitude out of range: {lon:.4f}"

    print(f"   ✅ GPS verified!")
    return True, f"✅ GPS verified: {lat:.4f}, {lon:.4f}"


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"🛰️  METADATA EXTRACTOR TEST")
    print(f"{'='*55}")

    test_img = 'dataset/val/solar_panels/' + \
        os.listdir('dataset/val/solar_panels/')[0]

    lat, lon, ts = extract_gps(test_img)

    if lat:
        print(f"   GPS Found: {lat:.4f}, {lon:.4f}")
    else:
        print(f"   No GPS in test image (normal!)")

    is_valid, msg = verify_geo_location(
        test_img,
        allowed_lat_range=(23.0, 37.0),
        allowed_lon_range=(60.0, 77.0)
    )
    print(f"   Result: {msg}")

    print(f"\n✅ P68 FIXED: getexif() used!")
    print(f"✅ P69 FIXED: DMS to decimal!")
    print(f"✅ P70 FIXED: Range checked!")
    print(f"✅ P21 FIXED: GPS verification!")