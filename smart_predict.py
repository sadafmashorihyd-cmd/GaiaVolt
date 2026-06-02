import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image
from scipy.stats import entropy

# Classes
CLASS_NAMES = [
    'cycling', 'electric_cars', 'led_lighting',
    'ocean_cleanup', 'organic_farming', 'plantation',
    'public_transport', 'recycling', 'solar_panels',
    'utility_bills', 'water_conservation', 'wind_energy'
]

def load_model():
    return tf.keras.models.load_model('models/ecox_final_best.h5')

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = preprocess_input(x)
    return np.expand_dims(x, axis=0)

def smart_predict(model, img_path):
    # Image load karo
    x = preprocess_image(img_path)
    preds = model.predict(x, verbose=0)[0]
    
    max_conf = float(np.max(preds))
    pred_idx = int(np.argmax(preds))
    pred_class = CLASS_NAMES[pred_idx]
    
    # Top 2 ka farq
    sorted_preds = np.sort(preds)[::-1]
    conf_gap = float(sorted_preds[0] - sorted_preds[1])
    
    # Entropy check — OOD detection
    pred_entropy = float(entropy(preds))
    max_entropy = float(np.log(len(CLASS_NAMES)))  # 12 classes
    entropy_ratio = pred_entropy / max_entropy
    
    # Top 3 predictions
    top3_idx = np.argsort(preds)[::-1][:3]
    top3 = [
        {
            'class': CLASS_NAMES[i],
            'confidence': float(preds[i] * 100)
        }
        for i in top3_idx
    ]
    
    # ═══ Decision Logic ═══
    
    # Case 1: Unknown/OOD image
    if entropy_ratio > 0.85:
        return {
            'status': 'REJECTED',
            'code': 'UNKNOWN_IMAGE',
            'message': 'Yeh image hamari kisi category mein nahi aati',
            'action': 'Sahi category ki photo lein',
            'confidence': round(max_conf * 100, 1),
            'top3': top3
        }
    
    # Case 2: Model confused
    if conf_gap < 0.15 and max_conf < 0.75:
        return {
            'status': 'UNCERTAIN',
            'code': 'MODEL_CONFUSED',
            'message': f'Model confused hai: {CLASS_NAMES[top3_idx[0]]} vs {CLASS_NAMES[top3_idx[1]]}',
            'action': 'Alag angle se photo lein',
            'confidence': round(max_conf * 100, 1),
            'top3': top3
        }
    
    # Case 3: Low confidence
    if max_conf < 0.50:
        return {
            'status': 'LOW_CONFIDENCE',
            'code': 'POOR_IMAGE',
            'message': 'Image quality ya angle theek nahi',
            'action': 'Behtar lighting mein dobara photo lein',
            'confidence': round(max_conf * 100, 1),
            'top3': top3
        }
    
    # Case 4: Medium confidence
    if max_conf < 0.80:
        return {
            'status': 'ACCEPTED_WITH_WARNING',
            'code': 'LOW_CONF_ACCEPT',
            'message': f'{pred_class} detect hua lekin confidence kam hai',
            'action': 'Accepted — manual review flag kiya',
            'class': pred_class,
            'confidence': round(max_conf * 100, 1),
            'top3': top3
        }
    
    # Case 5: High confidence
    return {
        'status': 'CONFIRMED',
        'code': 'SUCCESS',
        'message': f'{pred_class} successfully verified!',
        'action': 'Carbon coins process ho rahe hain',
        'class': pred_class,
        'confidence': round(max_conf * 100, 1),
        'top3': top3
    }


def test_smart_predict():
    print("🧠 Smart Predict System Loading...")
    model = load_model()
    print("✅ Model loaded!\n")
    
    # Val folder se test images
    import os
    test_results = []
    
    for cls in CLASS_NAMES:
        val_path = f'dataset/val/{cls}'
        if not os.path.exists(val_path):
            continue
            
        images = os.listdir(val_path)[:3]  # 3 images per class
        
        for img_name in images:
            img_path = os.path.join(val_path, img_name)
            result = smart_predict(model, img_path)
            test_results.append({
                'true_class': cls,
                'result': result
            })
            
            status_emoji = {
                'CONFIRMED': '✅',
                'ACCEPTED_WITH_WARNING': '⚠️',
                'LOW_CONFIDENCE': '🟡',
                'UNCERTAIN': '🔶',
                'REJECTED': '❌'
            }.get(result['status'], '❓')
            
            print(f"{status_emoji} True: {cls:<20} "
                  f"Pred: {result.get('class', 'N/A'):<20} "
                  f"Conf: {result['confidence']}% "
                  f"Status: {result['status']}")
    
    # Summary
    total