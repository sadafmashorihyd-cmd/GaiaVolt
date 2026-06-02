import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from src.training.augmentation_strategy import get_train_augmentation
from downsampling_engine import DownsamplingEngine
from src.utils.constants import CONFIG

aug = get_train_augmentation()
ds  = DownsamplingEngine()

print('Augmentation:', type(aug).__name__, 'OK!')
print('Downsampling:', type(ds).__name__, 'OK!')
print('Config IMG_SIZE:', CONFIG['IMG_SIZE'])
print('All integrated!')