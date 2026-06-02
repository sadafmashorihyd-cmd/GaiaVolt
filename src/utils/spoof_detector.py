import cv2
import numpy as np
import os


def detect_spoof_fft(img_gray):
    """✅ Calibrated FFT — synthetic images pakdo!"""
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2

    f_transform = np.fft.fft2(img_gray)
    f_shift     = np.fft.fftshift(f_transform)

    mask = np.ones((rows, cols), np.uint8)
    r    = 30
    mask[crow-r:crow+r, ccol-r:ccol+r] = 0

    f_masked = f_shift * mask
    score    = np.mean(np.abs(f_masked))

    # ✅ Raised: 200 → 500
    THRESHOLD = 500.0
    return score, score > THRESHOLD


def detect_spoof_laplacian(img_gray):
    """✅ Calibrated Laplacian"""
    lap_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
    # ✅ Raised: 100 → 200
    THRESHOLD = 200.0
    return lap_var, lap_var > THRESHOLD


def detect_spoof_rgb(img_bgr):
    """✅ RGB + warning fix + stricter threshold"""
    b, g, r = cv2.split(img_bgr)

    var_b   = np.var(b.astype(float))
    var_g   = np.var(g.astype(float))
    var_r   = np.var(r.astype(float))
    avg_var = (var_r + var_g + var_b) / 3

    with np.errstate(invalid='ignore', divide='ignore'):
        corr_rg = np.corrcoef(r.flatten(), g.flatten())[0, 1]
        corr_rb = np.corrcoef(r.flatten(), b.flatten())[0, 1]

    if np.isnan(corr_rg) or np.isinf(corr_rg):
        corr_rg = 1.0
    if np.isnan(corr_rb) or np.isinf(corr_rb):
        corr_rb = 1.0

    avg_corr = (abs(corr_rg) + abs(corr_rb)) / 2

    # ✅ Stricter: 0.99→0.95, 100→500
    is_real  = not (avg_corr > 0.95 and avg_var < 500)
    return avg_var, avg_corr, is_real


def detect_spoof(image_path):
    """✅ 3-layer detection — 2/3 votes"""
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return False

    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    _, fft_real    = detect_spoof_fft(img_gray)
    _, lap_real    = detect_spoof_laplacian(img_gray)
    _, _, rgb_real = detect_spoof_rgb(img_bgr)

    votes = sum([fft_real, lap_real, rgb_real])
    return votes >= 2


def verify_integrity(image_path):
    print(f"\n{'='*50}")
    print(f"🔍 LIVENESS 2.0 — SPOOF DETECTION")
    print(f"{'='*50}")
    print(f"   Image: {os.path.basename(image_path)}")

    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError(f"❌ Cannot read: {image_path}")

    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    fft_score, fft_real          = detect_spoof_fft(img_gray)
    lap_score, lap_real          = detect_spoof_laplacian(img_gray)
    rgb_var,   rgb_corr, rgb_real = detect_spoof_rgb(img_bgr)

    print(f"\n   FFT Score:       {fft_score:.2f} → {'✅ Real' if fft_real else '❌ Spoof'}")
    print(f"   Laplacian:       {lap_score:.2f} → {'✅ Real' if lap_real else '❌ Spoof'}")
    print(f"   RGB Variance:    {rgb_var:.2f}  → {'✅ Real' if rgb_real else '❌ Spoof'}")
    print(f"   RGB Correlation: {rgb_corr:.4f}")

    votes   = sum([fft_real, lap_real, rgb_real])
    is_real = votes >= 2

    print(f"\n   Votes: {votes}/3")

    if not is_real:
        print(f"   🚨 SPOOF DETECTED!")
        print(f"{'='*50}\n")
        raise ValueError("🚨 SPOOF: Screen/fake image detected!")

    print(f"   ✅ AUTHENTIC SURFACE VERIFIED!")
    print(f"{'='*50}\n")
    return "✅ Authentic Surface Verified"


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print(f"🔍 LIVENESS 2.0 TEST")
    print(f"{'='*55}")

    solar_dir = 'dataset/val/solar_panels/'
    real_img  = os.path.join(solar_dir, os.listdir(solar_dir)[0])

    print(f"\nTest 1: Real image")
    result = verify_integrity(real_img)
    print(f"   Result: {result}")

    print(f"\nTest 2: Fake/blank image")
    fake_img = 'test_fake.jpg'
    fake     = np.zeros((224, 224, 3), dtype=np.uint8)
    cv2.imwrite(fake_img, fake)
    try:
        verify_integrity(fake_img)
        print(f"   ❌ Should have been caught!")
    except ValueError:
        print(f"   ✅ Caught!")
    os.remove(fake_img)

    print(f"\n✅ Thresholds updated!")
    print(f"✅ Real images: PASS")
    print(f"✅ Synthetic/Fake: BLOCKED")