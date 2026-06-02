import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from src.training.augmentation_strategy import get_train_augmentation
from src.utils.constants import CONFIG


def augment_dataset(source_dir, output_dir, num_variations=3):
    print(f"\n{'='*55}")
    print(f"🔄 AUGMENTATION ENGINE")
    print(f"{'='*55}")

    if 'train' in output_dir and 'augmented' not in output_dir:
        print(f"❌ Output folder training data mein nahi!")
        return

    os.makedirs(output_dir, exist_ok=True)
    transform       = get_train_augmentation()
    total_generated = 0

    for class_name in sorted(os.listdir(source_dir)):
        if class_name.startswith('_'):
            continue
        class_src = os.path.join(source_dir, class_name)
        class_dst = os.path.join(output_dir, class_name)
        if not os.path.isdir(class_src):
            continue
        os.makedirs(class_dst, exist_ok=True)
        images = [f for f in os.listdir(class_src)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        class_count = 0
        for filename in images:
            img_path = os.path.join(class_src, filename)
            image    = cv2.imread(img_path)
            if image is None:
                continue
            base_name = os.path.splitext(filename)[0]
            for i in range(num_variations):
                augmented = transform(image=image)['image']
                out_name  = f"{base_name}_aug_{i}.jpg"
                cv2.imwrite(os.path.join(class_dst, out_name), augmented)
                class_count += 1
        total_generated += class_count
        print(f"   ✅ {class_name:<22} {class_count} augmented")

    print(f"\n   Total: {total_generated}")
    print(f"   Saved: {output_dir}")
    print(f"{'='*55}\n")
    return total_generated


if __name__ == "__main__":
    augment_dataset(
        source_dir     = CONFIG['TRAIN_DIR'],
        output_dir     = 'dataset/augmented/',
        num_variations = 2
    )