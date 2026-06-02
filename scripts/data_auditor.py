import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def audit_dataset(dataset_path):
    print(f"🔍 Auditing dataset at: {dataset_path}...")
    
    # Mock scores for distribution
    perfect_count = 0
    adversarial_count = 0
    
    # Logic: Har image ko check karo
    if os.path.exists(dataset_path):
        for filename in os.listdir(dataset_path):
            if filename.endswith(".jpg"):
                # Simple logic: agar file size chota hai toh adversarial
                file_size = os.path.getsize(os.path.join(dataset_path, filename))
                if file_size < 1000: # 1KB se chota
                    adversarial_count += 1
                else:
                    perfect_count += 1
    
    # Visualization
    labels = ['Perfect', 'Adversarial']
    sizes = [perfect_count, adversarial_count]
    
    # Check agar data exist karta hai
    if sum(sizes) == 0:
        print("⚠️ Warning: No images found to audit!")
        return

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#4CAF50', '#F44336'])
    plt.title("Data Distribution Report")
    plt.savefig("distribution_report.png")
    plt.close()
    
    print(f"✅ Audit Complete: {perfect_count} Perfect, {adversarial_count} Adversarial.")
    print("✨ Distribution Report saved as 'distribution_report.png'")

if __name__ == "__main__":
    audit_dataset('dataset/processed')