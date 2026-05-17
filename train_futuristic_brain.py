import tensorflow as tf
from efficientnet.tfkeras import EfficientNetB7
from tensorflow.keras.preprocessing.image import ImageDataGenerator
# 1. Image Augmentation (AI ki aankh ko tez karne ke liye)
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# 2. Data Loading (Path apne folder ke mutabiq set karein)
train_generator = train_datagen.flow_from_directory(
    'dataset/', 
    target_size=(224, 224), # High-Res for B7
    batch_size=8, # B7 heavy hai, is liye batch size chota rakha hai
    class_mode='categorical'
)

# 3. Load our Futuristic Brain
from upgrade_brain import build_futuristic_brain
model = build_futuristic_brain()

# 4. Start Training (Epochs kam rakhein pehle test ke liye)
print("🧠 Training Started... Laptop might get warm, it's normal!")
history = model.fit(
    train_generator,
    epochs=5, 
    verbose=1
)

# 5. Save the Master Brain
model.save('ecox_model_b7_v1.h5')
print("✅ Master Brain Saved: ecox_model_b7_v1.h5")