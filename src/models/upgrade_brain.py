import tensorflow as tf
import numpy as np
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from src.utils.constants import CONFIG


def build_futuristic_brain(num_classes=None):
    if num_classes is None:
        num_classes = CONFIG['NUM_CLASSES']

    input_tensor = layers.Input(shape=(224, 224, 3))

    base_model = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_tensor=input_tensor
    )
    base_model.trainable = False

    x = layers.GlobalAveragePooling2D()(base_model.output)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs=input_tensor, outputs=x)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=CONFIG['LEARNING_RATE']
        ),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            tf.keras.metrics.Precision(),
            tf.keras.metrics.Recall()
        ]
    )

    return model, base_model


def build_futuristic_brain_simple(num_classes=None):
    """Single return for compatibility"""
    model, _ = build_futuristic_brain(num_classes)
    return model