import cv2
import numpy as np
import os

class PreProcessor:
    @staticmethod
    def clean_image(image_path):
        # Image load in Grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
            
        # Adaptive Thresholding (Bill OCR & Sharp Edges)
        cleaned = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
        
        # Noise reduction (Median Blur)
        denoised = cv2.medianBlur(cleaned, 3)
        return denoised

def run_pipeline():
    # Dataset ke folders
    folders = ['solar_panels', 'recycling', 'utility_bills', 'plantation'] 
    output_dir = 'dataset/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    processor = PreProcessor()
    
    print("🚀 Starting Data Preprocessing Pipeline...")
    
    for folder in folders:
        folder_path = os.path.join('dataset', folder)
        if not os.path.exists(folder_path):
            continue
            
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(folder_path, filename)
                result = processor.clean_image(img_path)
                
                if result is not None:
                    save_path = os.path.join(output_dir, f"proc_{filename}")
                    cv2.imwrite(save_path, result)
                    print(f"✅ Processed: {filename}")

if __name__ == "__main__":
    run_pipeline()
    print("✨ Day 2 Pipeline Complete!")