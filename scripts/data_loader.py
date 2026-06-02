import os
import cv2
import numpy as np
from albumentations import Compose, HorizontalFlip, RandomBrightnessContrast, Rotate
from tensorflow.keras.applications.efficientnet import preprocess_input


class DataMineLoader:
    def __init__(self, image_dir, target_size=(224, 224)):
        self.image_dir   = image_dir
        self.target_size = target_size
        self.augmentor   = Compose([
            Rotate(limit=20),
            HorizontalFlip(p=0.5),
            RandomBrightnessContrast(p=0.2),
        ])

    def process_image(self, img_path):
        # Load
        image = cv2.imread(img_path)
        if image is None:
            return None

        # BGR → RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize
        image = cv2.resize(image, self.target_size)

        # Augmentation
        augmented = self.augmentor(image=image)
        processed = augmented['image']

        # ✅ P66 FIXED: preprocess_input use karo — 1/255 nahi!
        processed = np.expand_dims(processed, axis=0).astype(np.float32)
        processed = preprocess_input(processed)
        processed = processed[0]  # batch dimension hata do

        return processed