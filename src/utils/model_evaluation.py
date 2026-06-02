import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import load_model
from src.utils.constants import CONFIG


def evaluate_model(model_path, val_gen):
    print(f"\n{'='*55}")
    print(f"📊 MODEL EVALUATION ENGINE")
    print(f"{'='*55}")

    model = load_model(model_path, compile=False)
    print(f"   Model:  {model_path}")
    print(f"   Layers: {len(model.layers)}")

    print(f"\n   🔄 Predicting...")
    y_pred         = model.predict(val_gen, verbose=1)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true         = val_gen.classes

    # ✅ P61 FIXED: class names
    class_names = list(val_gen.class_indices.keys())

    # ✅ P60 FIXED: confusion matrix with labels
    cm = confusion_matrix(y_true, y_pred_classes)
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm, annot=True, fmt='d',
        cmap='Blues',
        xticklabels=class_names,
        yticklabels=class_names
    )
    plt.title('EcoX Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()

    os.makedirs('assets', exist_ok=True)
    plt.savefig("assets/confusion_matrix.png")
    plt.close()
    print(f"   Confusion matrix saved ✅")

    # ✅ P61 FIXED: class names in report
    report = classification_report(
        y_true,
        y_pred_classes,
        target_names=class_names
    )

    print(f"\n{'='*55}")
    print(f"📋 CLASSIFICATION REPORT")
    print(f"{'='*55}")
    print(report)

    accuracy = np.mean(y_pred_classes == y_true) * 100
    print(f"   Overall Accuracy: {accuracy:.2f}%")
    print(f"{'='*55}\n")

    return accuracy