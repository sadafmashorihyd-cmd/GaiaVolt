import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from src.utils.model_evaluation import evaluate_model
from src.utils.constants import CONFIG
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input

# ✅ P35 FIXED: rescale hata diya
# ✅ P36 FIXED: correct model path from CONFIG
# ✅ P37 FIXED: CONFIG paths use kiye
val_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input
).flow_from_directory(
    CONFIG["VAL_DIR"],
    target_size=CONFIG["IMG_SIZE"],
    batch_size=CONFIG["BATCH_SIZE"],
    shuffle=False
)

print(f"✅ Val classes: {val_gen.class_indices}")
print(f"✅ Val images:  {val_gen.samples}")

evaluate_model(CONFIG["MODEL_PATH"], val_gen)