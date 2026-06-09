"""
EcoX — Fresh Photo Validator
Rule 1: Photo 10 min se zyada purani = FRAUD
Rule 2: EXIF missing = FRAUD (net se download)
Rule 3: Camera make/model missing = FRAUD (screenshot/WhatsApp)
"""
import os
from datetime import datetime, timezone, timedelta
from PIL import Image
from PIL.ExifTags import TAGS


def check_fresh_photo(image_path: str) -> dict:
    """
    Returns:
        { "passed": bool, "reason": str, "timestamp": str }
    """
    print(f"\n{'='*55}")
    print(f"📷 FRESH PHOTO CHECK")
    print(f"{'='*55}")

    try:
        img  = Image.open(image_path)
        exif = img.getexif()

        # ── Rule 1: EXIF must exist ───────────────────────────────
        if not exif or len(exif) == 0:
            print(f"   ❌ No EXIF — net se download ya screenshot!")
            return {
                "passed": False,
                "reason": "No EXIF data — downloaded or screenshot image rejected. Take a fresh photo with your camera."
            }

        # Parse EXIF tags
        exif_data = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value

        print(f"   EXIF tags found: {len(exif_data)}")

        # ── Rule 2: Camera make/model must exist ──────────────────
        make  = exif_data.get('Make',  '')
        model = exif_data.get('Model', '')

        if not make and not model:
            print(f"   ❌ No camera info — WhatsApp/screenshot/download!")
            return {
                "passed": False,
                "reason": "No camera info found — WhatsApp forwards, screenshots, and downloaded images are not allowed."
            }

        print(f"   Camera: {make} {model} ✅")

        # ── Rule 3: Timestamp must be fresh (within 10 min) ───────
        # Check DateTimeOriginal first, then DateTime
        dt_str = (
            exif_data.get('DateTimeOriginal') or
            exif_data.get('DateTime') or
            exif_data.get('DateTimeDigitized')
        )

        if not dt_str:
            print(f"   ❌ No timestamp in EXIF!")
            return {
                "passed": False,
                "reason": "No timestamp in photo — old or edited image rejected."
            }

        # Parse EXIF datetime format: "2026:06:04 16:30:00"
        try:
            photo_dt = datetime.strptime(
                str(dt_str), "%Y:%m:%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        except Exception:
            print(f"   ❌ Invalid timestamp format: {dt_str}")
            return {
                "passed": False,
                "reason": "Invalid timestamp format — photo may be edited."
            }

        now      = datetime.now(timezone.utc)
        age      = now - photo_dt
        max_age  = timedelta(minutes=10)

        print(f"   Photo time: {photo_dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   Now:        {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"   Age:        {age.total_seconds()/60:.1f} minutes")

        if age > max_age:
            print(f"   ❌ Photo too old! ({age.total_seconds()/60:.1f} min > 10 min)")
            return {
                "passed": False,
                "reason": f"Photo is {age.total_seconds()/60:.0f} minutes old — only fresh photos (taken within 10 minutes) are accepted."
            }

        if age.total_seconds() < 0:
            print(f"   ❌ Future timestamp — edited/fake!")
            return {
                "passed": False,
                "reason": "Photo timestamp is in the future — edited image rejected."
            }

        print(f"   ✅ Fresh photo! Age: {age.total_seconds()/60:.1f} min")
        print(f"{'='*55}\n")

        return {
            "passed":    True,
            "reason":    "Fresh photo verified",
            "camera":    f"{make} {model}".strip(),
            "timestamp": photo_dt.isoformat(),
            "age_min":   round(age.total_seconds()/60, 1)
        }

    except Exception as e:
        print(f"   ❌ Check failed: {e}")
        return {
            "passed": False,
            "reason": f"Photo validation error: {str(e)}"
        }