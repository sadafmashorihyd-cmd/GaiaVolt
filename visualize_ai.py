import tensorflow as tf
import numpy as np
import cv2
import os

# 1. Model Load
model = tf.keras.models.load_model('ecox_model.h5')

# 2. Image Processing
img_path = 'dataset/real_test.jpg'
if not os.path.exists(img_path):
    print("⚠️ Error: Image missing!")
    exit()

img = cv2.imread(img_path)
img_res = cv2.resize(img, (224, 224))
img_array = np.expand_dims(img_res, axis=0) / 255.0

# 3. Force Build & Layer Extract
# Hum MobileNet ki internal layer ko direct target kar rahe hain
base_model = model.get_layer('mobilenetv2_1.00_224')
feature_model = tf.keras.models.Model(
    inputs=base_model.input, 
    outputs=base_model.get_layer('Conv_1').output
)

# 4. Generate Heatmap (The Smart Way)
features = feature_model.predict(img_array)
# Sum all feature maps to see where the AI is 'looking'
heatmap = np.sum(features[0], axis=-1)

# 5. Normalize & Cyberpunk Overlay
heatmap = np.maximum(heatmap, 0)
heatmap /= np.max(heatmap)
heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
heatmap = np.uint8(255 * heatmap)

# Apply JET colormap for that Cyberpunk X-Ray look
heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
superimposed_img = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

# 6. Save Result
cv2.imwrite("ecox_cyberpunk_scan.jpg", superimposed_img)

print("\n🚀 VICTORY! Day 6 Cyberpunk Scan Generated.")
print("The 'Sequential' error has been bypassed. Check 'ecox_cyberpunk_scan.jpg'!")