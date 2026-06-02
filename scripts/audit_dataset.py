import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from src.utils.constants import CONFIG


def audit_dataset(dataset_path=None):
    """
    ✅ P79 FIXED: train_balanced use karo
    ✅ P80 FIXED: image quality check
    ✅ P81 FIXED: processed_backup filter
    """
    if dataset_path is None:
        dataset_path = CONFIG['TRAIN_DIR']  # train_balanced!

    print(f"\n{'='*60}")
    print(f"🔬 DATASET AUDIT ENGINE")
    print(f"{'='*60}")
    print(f"   Path: {dataset_path}")

    if not os.path.exists(dataset_path):
        print(f"❌ Path not found!")
        return

    total_images   = 0
    total_corrupt  = 0
    total_low_qual = 0
    class_stats    = {}

    for class_name in sorted(os.listdir(dataset_path)):
        # ✅ P81 FIXED: skip backup/processed folders
        if class_name.startswith('_') or class_name == 'processed':
            print(f"   ⏭️  Skipping: {class_name}")
            continue

        class_dir = os.path.join(dataset_path, class_name)
        if not os.path.isdir(class_dir):
            continue

        images = [f for f in os.listdir(class_dir)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

        corrupt  = 0
        low_qual = 0
        valid    = 0

        for img_name in images:
            img_path = os.path.join(class_dir, img_name)

            # ✅ P80 FIXED: image quality check
            try:
                img = cv2.imread(img_path)
                if img is None:
                    corrupt += 1
                    continue

                # Size check
                h, w = img.shape[:2]
                if h < 32 or w < 32:
                    low_qual += 1
                    continue

                # Blur check
                gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blur    = cv2.Laplacian(gray, cv2.CV_64F).var()
                if blur < 10:
                    low_qual += 1
                    continue

                valid += 1

            except Exception:
                corrupt += 1

        total_images   += valid
        total_corrupt  += corrupt
        total_low_qual += low_qual

        class_stats[class_name] = {
            'total':    len(images),
            'valid':    valid,
            'corrupt':  corrupt,
            'low_qual': low_qual
        }

        status = '✅' if corrupt == 0 and low_qual == 0 else '⚠️'
        print(f"   {status} {class_name:<22} "
              f"valid={valid:>4} "
              f"corrupt={corrupt} "
              f"low_qual={low_qual}")

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"   Total valid:    {total_images}")
    print(f"   Total corrupt:  {total_corrupt}")
    print(f"   Total low qual: {total_low_qual}")
    print(f"   Classes:        {len(class_stats)}")

    if total_corrupt == 0 and total_low_qual == 0:
        print(f"   Status: ✅ Dataset is CLEAN!")
    else:
        print(f"   Status: ⚠️ Issues found — fix before training!")

    print(f"{'='*60}\n")
    return class_stats


if __name__ == "__main__":
    audit_dataset()