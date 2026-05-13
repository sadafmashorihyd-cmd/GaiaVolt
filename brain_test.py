import tensorflow as tf

print("🧠 EcoX Brain Loading... Please wait...")

# MobileNetV2 model load ho raha hai
model = tf.keras.applications.MobileNetV2(weights='imagenet')

print("✅ SUCCESS: EcoX Brain is now LIVE!")
print("Model Name Identified as:", model.name)