import tensorflow as tf
import os
import sys

print("\n" + "="*60)
print("🧠 [NEURAL CORE DIAGNOSTICS]: LOADING ECOX BRAIN ENVIRONMENT...")
print("="*60)

# Target Model Node Evaluation
TARGET_MODEL = 'ecox_model.h5'

if os.path.exists(TARGET_MODEL):
    print(f"📡 [SYNC]: Target Weight File '{TARGET_MODEL}' Detected. Verifying Tensors...")
    try:
        # Load local specialized model instead of generic ImageNet
        model = tf.keras.models.load_model(TARGET_MODEL)
        print("\n+++++++++++++++++++++++++++++++++++++++++++++")
        print(" ✅ SUCCESS: ECOX MAIN MODEL IS NOW LIVE & ACTIVE!")
        print(f" 🤖 Target Architecture Core Name: {model.name}")
        print(f" 📊 Total Input Layer Geometry: {model.input_shape}")
        print("+++++++++++++++++++++++++++++++++++++++++++++")
    except Exception as e:
        print(f"🚨 [CRITICAL METRIC EXCEPTION]: Tensor load crashed. Error: {str(e)}")
else:
    print(f"⚠️ [SANDBOX MODE]: Local '{TARGET_MODEL}' not found in runtime root.")
    print("🤖 Initializing Simulation Check via Baseline MobileNetV2 Architecture...")
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
    print("🏆 [STATUS]: Sandbox Core Active. Model Name Baseline: ", model.name)

print("="*60 + "\n")