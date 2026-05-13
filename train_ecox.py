import tensorflow as tf
# Naya rasta (path) ImageDataGenerator ke liye
from tensorflow.keras.preprocessing import image

print("⚙️ Preparing Data for Training...")

# 1. Images ko resize aur normalize karne ka naya setup
datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255, 
    validation_split=0.2
)

# 2. Dataset ko load karna
train_generator = datagen.flow_from_directory(
    'dataset',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

print("✅ Training Data Ready!")
# Classes check karne ka sahi tareeqa
print("Found Classes:", train_generator.class_indices)
# 3. Base Model (MobileNetV2) ko load karna bina aakhri layer ke
base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False # Purana dimaag lock kar diya

# 4. Apni "EcoX" Layers lagana (Updated for 12 Global Classes)
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(12, activation='softmax') # 3 ko mita kar 12 kar diya
])

# 5. Compile karna
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("🏗️ EcoX Custom Brain Architecture Ready!")
model.summary()
print("\n🚀 Starting Training... EcoX is now learning!")

# Training shuru (Hum 5 'epochs' yani 5 baar pura dataset dikhayenge)
history = model.fit(
    train_generator,
    epochs=5
)

# Model ko save karna taake hum baad mein use kar sakein
model.save('ecox_model.h5')
print("\n✅ MISSION ACCOMPLISHED: EcoX Model is Trained & Saved!")