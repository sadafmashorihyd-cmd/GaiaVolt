import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import shutil
import numpy as np
import tensorflow as tf
import cv2
from datetime import datetime, timezone
from tensorflow.keras.applications.efficientnet import preprocess_input
from src.utils.constants import CONFIG


class ActiveLearningLoop:

    def __init__(self, model_path=None):
        self.model_path    = model_path or CONFIG['MODEL_PATH']
        self.model         = tf.keras.models.load_model(
            self.model_path, compile=False
        )
        self.class_names   = CONFIG['CLASSES']
        self.loop_dir      = 'scripts/active_learning_loop'
        self.uncertain_dir = os.path.join(self.loop_dir, 'uncertain')
        self.reviewed_dir  = os.path.join(self.loop_dir, 'reviewed')
        os.makedirs(self.uncertain_dir, exist_ok=True)
        os.makedirs(self.reviewed_dir,  exist_ok=True)

    def predict_confidence(self, img_path):
        img = cv2.imread(img_path)
        if img is None:
            return None, None, 0.0
        img   = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img   = cv2.resize(img, CONFIG['IMG_SIZE'])
        arr   = np.expand_dims(img, axis=0).astype(np.float32)
        arr   = preprocess_input(arr)
        preds = self.model.predict(arr, verbose=0)
        conf  = float(np.max(preds) * 100)
        idx   = int(np.argmax(preds))
        cls   = self.class_names[idx]
        return cls, idx, conf

    def scan_and_queue(self, scan_dir, confidence_threshold=85.0):
        print(f"\n{'='*55}")
        print(f"🔄 ACTIVE LEARNING SCAN")
        print(f"{'='*55}")
        print(f"   Threshold: {confidence_threshold}%")
        print(f"   Scanning:  {scan_dir}")

        if not os.path.exists(scan_dir):
            print(f"❌ Directory not found!")
            return 0

        # ✅ Gap 2 FIXED: existing files track karo
        existing_files = set(os.listdir(self.uncertain_dir))

        queued = 0
        total  = 0

        for root, dirs, files in os.walk(scan_dir):
            for fname in sorted(files):
                if not fname.lower().endswith(('.jpg','.jpeg','.png')):
                    continue

                img_path = os.path.join(root, fname)
                cls, _, conf = self.predict_confidence(img_path)

                if cls is None:
                    continue

                total += 1

                if conf < confidence_threshold:
                    # ✅ Duplicate check — same original filename already queued?
                    already_queued = any(fname in f for f in existing_files)
                    if already_queued:
                        continue

                    timestamp = datetime.now(timezone.utc).strftime(
                        "%Y%m%d_%H%M%S"
                    )
                    dest_name = f"uncertain_{conf:.0f}pct_{timestamp}_{fname}"
                    dest_path = os.path.join(self.uncertain_dir, dest_name)
                    shutil.copy2(img_path, dest_path)
                    existing_files.add(dest_name)
                    queued += 1
                    print(f"   ⚠️  Queued: {fname} ({cls} {conf:.1f}%)")

        print(f"\n   Total scanned: {total}")
        print(f"   Queued:        {queued}")
        print(f"   High conf:     {total - queued}")
        print(f"{'='*55}\n")
        return queued

    def get_queue_status(self):
        uncertain = os.listdir(self.uncertain_dir)
        reviewed  = os.listdir(self.reviewed_dir)
        print(f"\n{'='*55}")
        print(f"📊 ACTIVE LEARNING QUEUE STATUS")
        print(f"{'='*55}")
        print(f"   Uncertain (needs review): {len(uncertain)}")
        print(f"   Reviewed (ready):         {len(reviewed)}")
        print(f"{'='*55}\n")
        return len(uncertain), len(reviewed)


if __name__ == "__main__":
    loop = ActiveLearningLoop()
    
    # Status check
    loop.get_queue_status()
    
    # Scan — duplicates automatically skip honge
    loop.scan_and_queue(
        scan_dir             = 'dataset/val/',
        confidence_threshold = 85.0
    )
    
    # Final status
    loop.get_queue_status()
    print("✅ P84 FIXED: Active Learning Loop — No duplicates!")