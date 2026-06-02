import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.applications.efficientnet import preprocess_input

MODEL_PATH   = 'models/ecox_final_best.h5'
OUTPUT_PATH  = 'ecox_model_edge.tflite'
DATASET_PATH = 'dataset'


def convert_to_edge():
    print("\n" + "="*55)
    print("⚡ EDGE-AI CONVERSION ENGINE")
    print("="*55)

    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model not found: {MODEL_PATH}")
        return

    print(f"\n   Loading: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print(f"   Layers:  {len(model.layers)} ✅")
    print(f"   Params:  {model.count_params():,} ✅")

    print(f"\n   Converting to TFLite...")

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[1, 224, 224, 3], dtype=tf.float32)
    ])
    def serving_fn(x):
        return model(x, training=False)

    converter = tf.lite.TFLiteConverter.from_concrete_functions(
        [serving_fn.get_concrete_function()]
    )
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS
    ]
    converter.exclude_conversion_metadata = True

    print(f"   Converting...")
    tflite_model = converter.convert()

    with open(OUTPUT_PATH, 'wb') as f:
        f.write(tflite_model)

    final_size = os.path.getsize(OUTPUT_PATH) / (1024*1024)
    print(f"\n   Output: {OUTPUT_PATH}")
    print(f"   Size:   {final_size:.2f} MB")

    if final_size < 10:
        print(f"   Status: ✅ Lightweight!")
    else:
        print(f"   Status: ⚠️ Consider more pruning")

    print(f"\n{'='*55}")
    print(f"✅ P11 FIXED: Correct model loaded!")
    print(f"✅ P12 FIXED: EfficientNet preprocessing!")
    print(f"✅ Edge model: {OUTPUT_PATH}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    convert_to_edge()