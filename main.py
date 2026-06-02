import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from src.training.trainer_engine import start_training
from src.utils.constants import CONFIG
from src.utils.data_auditor import generate_distribution_chart
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input


def main():
    print("🚀 Project EcoX: God-Eye AI Initializing...")

    if not os.path.exists(CONFIG["DATA_DIR"]):
        print("❌ CRITICAL: Dataset folder not found!")
        return

    # ✅ P51 FIXED: rescale=1./255 hata diya — preprocess_input use karo
    # ✅ P53 FIXED: train_balanced use karo — train/ nahi!
    train_gen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    ).flow_from_directory(
        CONFIG["TRAIN_DIR"],
        target_size=CONFIG["IMG_SIZE"],
        batch_size=CONFIG["BATCH_SIZE"],
        shuffle=True
    )

    val_gen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    ).flow_from_directory(
        CONFIG["VAL_DIR"],
        target_size=CONFIG["IMG_SIZE"],
        batch_size=CONFIG["BATCH_SIZE"],
        shuffle=False
    )

    print(f"✅ Train: {train_gen.samples} images, {train_gen.num_classes} classes")
    print(f"✅ Val:   {val_gen.samples} images, {val_gen.num_classes} classes")

    # Sanity check
    if train_gen.num_classes != val_gen.num_classes:
        print(f"❌ Class mismatch! Train:{train_gen.num_classes} Val:{val_gen.num_classes}")
        return

    # Audit Report
    generate_distribution_chart(
        train_gen.samples,
        val_gen.samples
    )

    print("🔥 Starting Training Cycle...")
    start_training(train_gen, val_gen)

    print("✅ Training Complete!")
    print(f"📊 Model saved: {CONFIG['MODEL_PATH']}")


if __name__ == "__main__":
    main()