import os

CONFIG = {
    "IMG_SIZE": (224, 224),
    "BATCH_SIZE": 32,
    "EPOCHS": 20,
    "LEARNING_RATE": 0.0001,
    "CLASSES": [
        'cycling', 'electric_cars', 'led_lighting',
        'ocean_cleanup', 'organic_farming', 'plantation',
        'public_transport', 'recycling', 'solar_panels',
        'utility_bills', 'water_conservation', 'wind_energy'
    ],
    "NUM_CLASSES": 12,
    "MODEL_PATH": "models/ecox_final_best.h5",
    "DATA_DIR": "dataset/",
    "TRAIN_DIR": "dataset/train_balanced/",
    "VAL_DIR": "dataset/val/"
}

os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("assets", exist_ok=True)