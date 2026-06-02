import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
import cv2
import shutil
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input
from src.training.trainer_engine import start_training
from src.utils.constants import CONFIG
from downsampling_engine import DownsamplingEngine
from src.training.augmentation_strategy import get_train_augmentation

aug         = get_train_augmentation()
downsampler = DownsamplingEngine()

IMG_SIZE   = CONFIG['IMG_SIZE']
BATCH_SIZE = CONFIG['BATCH_SIZE']


def smart_preprocess(image):
    h, w = image.shape[:2]
    if w > 224 or h > 224:
        image = downsampler.smart_downsample(image)
    augmented = aug(image=image)['image']
    return preprocess_input(augmented.astype(np.float32))


def preprocess_for_val(image):
    h, w = image.shape[:2]
    if w > 224 or h > 224:
        image = downsampler.smart_downsample(image)
    return preprocess_input(image.astype(np.float32))


def merge_augmented_to_train():
    """
    ✅ Augmented images ko train_balanced mein merge karo
    """
    aug_dir   = 'dataset/augmented/'
    train_dir = CONFIG['TRAIN_DIR']

    if not os.path.exists(aug_dir):
        print("⚠️ No augmented data found!")
        return 0

    merged = 0
    for class_name in os.listdir(aug_dir):
        src_class = os.path.join(aug_dir, class_name)
        dst_class = os.path.join(train_dir, class_name)

        if not os.path.isdir(src_class):
            continue

        os.makedirs(dst_class, exist_ok=True)

        for fname in os.listdir(src_class):
            src = os.path.join(src_class, fname)
            dst = os.path.join(dst_class, fname)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                merged += 1

    print(f"✅ Merged {merged} augmented images!")
    return merged


train_datagen = ImageDataGenerator(preprocessing_function=smart_preprocess)
val_datagen   = ImageDataGenerator(preprocessing_function=preprocess_for_val)

# ✅ Augmented data merge karo
merged = merge_augmented_to_train()

train_generator = train_datagen.flow_from_directory(
    CONFIG['TRAIN_DIR'],
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    CONFIG['VAL_DIR'],
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

print(f"✅ Train:        {train_generator.samples} images")
print(f"✅ Val:          {val_generator.samples} images")
print(f"✅ Classes:      {train_generator.num_classes}")
print(f"✅ Augmentation: integrated!")
print(f"✅ Downsampling: integrated!")
print(f"✅ Augmented:    {merged} merged!")

if train_generator.num_classes != val_generator.num_classes:
    print(f"❌ Class mismatch!")
    exit()

model = start_training(train_generator, val_generator)