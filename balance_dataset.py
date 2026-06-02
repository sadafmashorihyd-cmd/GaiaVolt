import os, shutil, random

SOURCE = r"dataset\train"
TARGET = r"dataset\train_balanced"
MAX_PER_CLASS = 150  # ab zyada images hain toh 150 karo
SKIP = ["_processed_backup", "processed"]

# Pehle purana balanced folder saaf karo
if os.path.exists(TARGET):
    shutil.rmtree(TARGET)
    print("🗑️ Purana balanced folder delete kiya")

for cls in os.listdir(SOURCE):
    if cls in SKIP:
        continue
    
    src = os.path.join(SOURCE, cls)
    dst = os.path.join(TARGET, cls)
    os.makedirs(dst, exist_ok=True)
    
    images = [f for f in os.listdir(src) 
              if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))]
    
    selected = random.sample(images, min(MAX_PER_CLASS, len(images)))
    
    for img in selected:
        shutil.copy(os.path.join(src, img), 
                    os.path.join(dst, img))
    
    print(f"{cls:<25} {len(selected)} images")

print("\n✅ Balanced dataset ready!")