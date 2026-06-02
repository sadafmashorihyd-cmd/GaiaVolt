import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from src.utils.spoof_detector import detect_spoof

solar_dir = 'dataset/val/solar_panels/'
img = os.path.join(solar_dir, os.listdir(solar_dir)[0])

result = detect_spoof(img)
print(f'Spoof result: {result}')
print(f'detect_spoof working: {result == True}')