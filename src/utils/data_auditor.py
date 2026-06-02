import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.utils import class_weight

def generate_distribution_chart(perfect_data, adversarial_data):
    if not os.path.exists('assets'):
        os.makedirs('assets')
    df = pd.DataFrame({'Data_Type': ['Perfect Sunlight', 'Adversarial Shadows'], 'Count': [perfect_data, adversarial_data]})
    plt.figure(figsize=(8, 6))
    df.set_index('Data_Type')['Count'].plot(kind='pie', autopct='%1.1f%%', colors=['#4CAF50', '#FF9800'])
    plt.title("EcoX Robustness: Training Data Distribution")
    plt.ylabel("")
    plt.savefig("assets/distribution_report.png")
    print("✅ Distribution Report saved in 'assets/distribution_report.png'")

def get_class_weights(train_gen):
    # Har class ke labels extract karna
    labels = train_gen.classes
    # Balanced weights calculate karna (Class 6 ka weight apne aap kam ho jayega)
    weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(labels),
        y=labels
    )
    weight_dict = dict(enumerate(weights))
    print(f"DEBUG: Calculated Class Weights: {weight_dict}")
    return weight_dict