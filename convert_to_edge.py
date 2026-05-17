import tensorflow as tf
import os

# 1. Load your existing model
model_path = 'ecox_model.h5'
if not os.path.exists(model_path):
    print(f"❌ Error: {model_path} nahi mili! Pehle model train karein.")
else:
    model = tf.keras.models.load_model(model_path)
    print("🧠 [OFFLINE NEURAL SYNC]: Optimization process starting...")

    # 2. TFLite Converter with Full Integer Quantization logic
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Ye line weight pruning aur size reduction (Integer Quant) ke liye hai
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # 2035 Standard: Metadata Stripping (Size mazeed kam karne aur privacy ke liye)
    converter.exclude_conversion_metadata = True 

    # 3. Converting to TFLite format
    tflite_model = converter.convert()

    # 4. Save the final 2035 Edge model
    output_path = 'ecox_model_edge.tflite'
    with open(output_path, 'wb') as f:
        f.write(tflite_model)

    print("\n🚀 [STATUS]: Offline Neural Sync ACTIVE.")
    print(f"✅ Success! Edge-AI model saved as: {output_path}")
    
    # Size calculation check
    final_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"📊 Final Model Size: {final_size:.2f} MB")

    if final_size < 5:
        print("🏆 Target Achieved: Model is under 5MB!")
    else:
        print("⚠️ Warning: Model is still above 5MB. Need more pruning.")