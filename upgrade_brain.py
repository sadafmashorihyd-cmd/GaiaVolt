import tensorflow as tf
from tensorflow.keras import layers, models
# B0 is smart, reliable, and powerful
from tensorflow.keras.applications import EfficientNetB0

def build_futuristic_brain():
    # Base Model: EfficientNet-B0 (Insaan ki aankh se behtar balance)
    base_model = EfficientNetB0(
        weights='imagenet', 
        include_top=False, 
        input_shape=(224, 224, 3) 
    )
    
    base_model.trainable = False 

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3), 
        layers.Dense(256, activation='relu'),
        layers.Dense(13, activation='softmax') 
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    print("🚀 2035 Level Brain (EfficientNet-B0) is Ready!")
    model.summary()
    return model

my_new_brain = build_futuristic_brain()