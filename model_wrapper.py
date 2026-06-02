import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import onnxruntime as ort
import numpy as np
import cv2
from tensorflow.keras.applications.efficientnet import preprocess_input


class DualBrainBridge:
    def __init__(self, model_path="ecox_model_final.onnx"):
        try:
            self.session = ort.InferenceSession(model_path)
            print("🚀 Dual-Engine Bridge: ONNX Runtime Active.")
        except Exception as e:
            print(f"❌ ONNX Error: {e}")
            self.session = None

    def get_tiled_patches(self, image, tile_size=224, stride=112):
        h, w, _ = image.shape
        patches  = []
        for y in range(0, h - tile_size + 1, stride):
            for x in range(0, w - tile_size + 1, stride):
                patches.append(image[y:y+tile_size, x:x+tile_size])
        return patches

    def preprocess_patch(self, patch):
        # ✅ P100 FIXED: preprocess_input use karo!
        img_rgb   = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB)
        img_array = np.expand_dims(img_rgb, axis=0).astype(np.float32)
        return preprocess_input(img_array)

    def tiled_predict(self, image):
        if self.session is None:
            return None

        patches      = self.get_tiled_patches(image)
        tile_results = []

        for patch in patches:
            p_input    = self.preprocess_patch(patch)
            # ONNX input format: (1, 3, 224, 224)
            p_input    = p_input.transpose(0, 3, 1, 2)
            input_name = self.session.get_inputs()[0].name
            res        = self.session.run(None, {input_name: p_input})
            tile_results.append(res[0])

        # ✅ P102 FIXED: mean use karo — max nahi!
        return np.mean(tile_results, axis=0)

    def predict(self, image):
        if self.session is None:
            return "ENGINE_NOT_READY"
        try:
            if image is None or image.size == 0:
                raise ValueError("Empty image!")
            return self.tiled_predict(image)
        except Exception as e:
            print(f"⚠️ Warning: {e}")
            return "RETRY_SIGNAL"


if __name__ == "__main__":
    bridge = DualBrainBridge()
    # ✅ P103 FIXED: real image test
    solar_dir = 'dataset/val/solar_panels/'
    img_name  = os.listdir(solar_dir)[0]
    real_img  = cv2.imread(os.path.join(solar_dir, img_name))
    print(f"Testing with real image: {img_name}")
    result = bridge.predict(real_img)
    print(f"✅ Result: {result}")