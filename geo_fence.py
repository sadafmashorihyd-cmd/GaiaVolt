import os
import json
import math
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

# Geo-fence config
GEO_FENCE_RADIUS_KM  = 10.0   # 10km radius
MAX_SUBMISSIONS_24H  = 3       # 24 ghante mein max submissions
FENCE_DB_FILE        = 'geo_fence_log.json'


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a    = (math.sin(dlat/2)**2 +
            math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
    return 6371 * (2 * math.asin(math.sqrt(a)))


def load_fence_db():
    """Load geo-fence log"""
    if not os.path.exists(FENCE_DB_FILE):
        return {}
    try:
        with open(FENCE_DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_fence_db(data):
    """Save geo-fence log"""
    with open(FENCE_DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def clean_old_submissions(submissions):
    """24 ghante se purani submissions remove karo"""
    now     = datetime.now(timezone.utc)
    cutoff  = (now - timedelta(hours=24)).isoformat()
    return [s for s in submissions if s['timestamp'] > cutoff]


def check_geo_fence(user_id, lat, lon):
    """
    Main geo-fence check:
    1. Same location se baar baar submit = FRAUD
    2. 10km radius mein max 3 per 24h
    """
    print(f"\n{'='*55}")
    print(f"🛰️  GEO-FENCE CHECK")
    print(f"{'='*55}")
    print(f"   User:     {user_id}")
    print(f"   Location: {lat:.4f}, {lon:.4f}")

    db       = load_fence_db()
    user_key = f"user_{user_id}"

    if user_key not in db:
        db[user_key] = []

    # Clean old submissions
    db[user_key] = clean_old_submissions(db[user_key])

    # Check submissions in 10km radius
    nearby_submissions = []
    for submission in db[user_key]:
        dist = haversine_distance(
            lat, lon,
            submission['lat'],
            submission['lon']
        )
        if dist <= GEO_FENCE_RADIUS_KM:
            nearby_submissions.append({
                **submission,
                'distance': dist
            })

    print(f"   Nearby (10km, 24h): {len(nearby_submissions)}")
    print(f"   Max allowed:        {MAX_SUBMISSIONS_24H}")

    # FRAUD check
    if len(nearby_submissions) >= MAX_SUBMISSIONS_24H:
        print(f"\n   {'🚨 '*10}")
        print(f"   FRAUD ALERT: Too many submissions!")
        print(f"   {len(nearby_submissions)} submissions in 10km/24h")
        print(f"   {'🚨 '*10}")
        return False, f"FRAUD: {len(nearby_submissions)} submissions in 10km radius!"

    # Valid — log it
    db[user_key].append({
        'lat':       lat,
        'lon':       lon,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    save_fence_db(db)

    remaining = MAX_SUBMISSIONS_24H - len(nearby_submissions) - 1
    print(f"   ✅ Location approved!")
    print(f"   Remaining today: {remaining}")
    print(f"{'='*55}\n")

    return True, f"✅ Location verified! {remaining} submissions remaining"


def get_user_stats(user_id):
    """User ki submission history"""
    db       = load_fence_db()
    user_key = f"user_{user_id}"

    if user_key not in db:
        return {"total": 0, "last_24h": 0}

    submissions = clean_old_submissions(db[user_key])
    return {
        "total":   len(db[user_key]),
        "last_24h": len(submissions)
    }


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"🛰️  GEO-FENCE TEST")
    print(f"{'='*55}")

    user = os.getenv('REGISTERED_USER', 'sadaf')

    # Karachi coordinates
    karachi_lat = 24.8607
    karachi_lon = 67.0011

    # Test 1: First submission
    print("TEST 1: First submission")
    ok, msg = check_geo_fence(user, karachi_lat, karachi_lon)
    print(f"   Result: {msg}")

    # Test 2: Same location — second
    print("TEST 2: Second submission same area")
    ok, msg = check_geo_fence(user, 24.8650, 67.0050)
    print(f"   Result: {msg}")

    # Test 3: Same location — third
    print("TEST 3: Third submission same area")
    ok, msg = check_geo_fence(user, 24.8680, 67.0080)
    print(f"   Result: {msg}")

    # Test 4: Fourth — should be BLOCKED!
    print("TEST 4: Fourth submission — should BLOCK!")
    ok, msg = check_geo_fence(user, 24.8700, 67.0100)
    print(f"   Result: {'🚨 BLOCKED!' if not ok else '✅ Allowed'}")

    # Test 5: Different city — should pass!
    print("TEST 5: Different city (Lahore)")
    ok, msg = check_geo_fence(user, 31.5204, 74.3587)
    print(f"   Result: {msg}")

    # Stats
    stats = get_user_stats(user)
    print(f"\n   User stats: {stats}")

    # Cleanup
    if os.path.exists(FENCE_DB_FILE):
        os.remove(FENCE_DB_FILE)
        print(f"   Test data cleaned!")

    print(f"\n✅ Day 9 COMPLETE: 10km Geo-Fence working!")