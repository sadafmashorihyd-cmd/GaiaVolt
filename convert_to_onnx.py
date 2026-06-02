import os
import tensorflow as tf

def convert_model():
    print("Exporting model using Keras Export API...")
    model = tf.keras.models.load_model('ecox_model_stable.h5')
    
    export_path = "temp_model_dir"
    model.export(export_path) 
    
    print("Converting to ONNX with Opset 16 (Edge-Ready Optimization)...")
    output_path = "ecox_model_final.onnx"
    # Opset 16 Swish activation aur efficient convolution support ke liye
    os.system(f"python -m tf2onnx.convert --saved-model {export_path} --output {output_path} --opset 16")
    
    print(f"✅ ONNX Model successfully generated: {output_path}")

if __name__ == "__main__":
    convert_model()