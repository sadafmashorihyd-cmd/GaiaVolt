import tensorflow as tf
from src.models.upgrade_brain import build_futuristic_brain
from src.utils.data_auditor import get_class_weights

def start_training(train_generator, val_generator):
    model, base_model = build_futuristic_brain(
        num_classes=len(train_generator.class_indices)
    )
    
    print(f"✅ Classes found: {train_generator.class_indices}")
    
    # ═══ PHASE 1: Sirf head train karo (10 epochs) ═══
    print("\n🔥 PHASE 1: Training head layers...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    weights_dict = get_class_weights(train_generator)
    
    callbacks_p1 = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=5, 
            restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'models/ecox_phase1_best.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=10,
        class_weight=weights_dict,
        callbacks=callbacks_p1,
        verbose=1
    )
    
    # ═══ PHASE 2: Last 20 layers unfreeze karo ═══
    print("\n🚀 PHASE 2: Fine-tuning EfficientNet last 20 layers...")
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False
    
    # Lower learning rate for fine-tuning
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks_p2 = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=7,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'models/ecox_final_best.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5,
            patience=3, verbose=1
        )
    ]
    
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=30,
        class_weight=weights_dict,
        callbacks=callbacks_p2,
        verbose=1
    )
    
    model.save('models/ecox_model_final.h5')
    print("✅ Training Complete! Best model saved.")
    return model