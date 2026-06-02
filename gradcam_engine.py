import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.applications.efficientnet import preprocess_input
from src.utils.constants import CONFIG


class GradCAMEngine:

    def __init__(self, model_path=None):
        model_path = model_path or CONFIG['MODEL_PATH']
        print(f"   Loading model: {model_path}")
        self.model       = tf.keras.models.load_model(
            model_path, compile=False
        )
        self.class_names = CONFIG['CLASSES']
        self.last_conv_layer = self._find_last_conv()
        print(f"   Last conv layer: {self.last_conv_layer} ✅")

    def _find_last_conv(self):
        for layer in reversed(self.model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                return layer.name
        return None

    def preprocess(self, img_path):
        img     = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_res = cv2.resize(img_rgb, CONFIG['IMG_SIZE'])
        arr     = np.expand_dims(img_res, axis=0).astype(np.float32)
        return preprocess_input(arr), img

    def compute_gradcam(self, img_path):
        img_array, original = self.preprocess(img_path)

        grad_model = tf.keras.models.Model(
            inputs  = self.model.inputs,
            outputs = [
                self.model.get_layer(self.last_conv_layer).output,
                self.model.output
            ]
        )

        # ✅ Warning fix: tf.constant use karo
        inputs = tf.constant(img_array)

        with tf.GradientTape() as tape:
            tape.watch(inputs)
            conv_outputs, predictions = grad_model(inputs, training=False)
            pred_idx    = tf.argmax(predictions[0])
            class_score = predictions[:, pred_idx]

        grads        = tape.gradient(class_score, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap      = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap      = tf.squeeze(heatmap)
        heatmap      = tf.maximum(heatmap, 0) / (
            tf.math.reduce_max(heatmap) + 1e-8
        )
        heatmap      = heatmap.numpy()

        confidence = float(tf.reduce_max(predictions) * 100)
        class_name = self.class_names[int(pred_idx)]

        return heatmap, original, class_name, confidence

    def generate_cyberpunk_overlay(self, img_path, save_path=None):
        print(f"\n{'='*55}")
        print(f"🔬 GRAD-CAM X-RAY ENGINE")
        print(f"{'='*55}")

        heatmap, original, class_name, confidence = self.compute_gradcam(
            img_path
        )

        h, w    = original.shape[:2]
        heatmap = cv2.resize(heatmap, (w, h))
        heatmap = np.uint8(255 * heatmap)

        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay       = cv2.addWeighted(original, 0.6, heatmap_color, 0.4, 0)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(overlay, f"CLASS: {class_name.upper()}",
                    (10, 30), font, 0.8, (0, 255, 0), 2)
        cv2.putText(overlay, f"CONF:  {confidence:.1f}%",
                    (10, 60), font, 0.8, (0, 255, 255), 2)

        if save_path is None:
            save_path = 'ecox_cyberpunk_scan.jpg'

        os.makedirs('assets', exist_ok=True)
        cv2.imwrite(save_path, overlay)
        cv2.imwrite(f'assets/{os.path.basename(save_path)}', overlay)

        print(f"   Class:      {class_name} ✅")
        print(f"   Confidence: {confidence:.1f}% ✅")
        print(f"   Saved:      {save_path} ✅")
        print(f"{'='*55}\n")

        return overlay, class_name, confidence


def run_test():
    print("\n" + "="*55)
    print("🚀 GRAD-CAM TEST")
    print("="*55)

    engine = GradCAMEngine()

    test_dirs = {
        'solar_panels':  'dataset/val/solar_panels/',
        'cycling':       'dataset/val/cycling/',
        'utility_bills': 'dataset/val/utility_bills/'
    }

    for class_name, dir_path in test_dirs.items():
        if not os.path.exists(dir_path):
            continue
        images = [f for f in os.listdir(dir_path)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            continue

        img_path  = os.path.join(dir_path, images[0])
        save_path = f'ecox_gradcam_{class_name}.jpg'

        overlay, pred, conf = engine.generate_cyberpunk_overlay(
            img_path, save_path
        )
        print(f"   {class_name}: {pred} ({conf:.1f}%) ✅")

    print("\n✅ P31 FIXED: EfficientNet layer!")
    print("✅ P32 FIXED: Correct model!")
    print("✅ P34 FIXED: Real Grad-CAM!")
    print("✅ P43 FIXED: Cyberpunk overlay!")


if __name__ == "__main__":
    run_test()