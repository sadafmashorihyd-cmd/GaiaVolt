import albumentations as A


def get_train_augmentation():
    return A.Compose([
        A.RandomShadow(p=0.3),
        A.RandomBrightnessContrast(
            brightness_limit=0.3,
            contrast_limit=0.3,
            p=0.5
        ),
        A.Rotate(limit=20, p=0.5),
        A.HorizontalFlip(p=0.5),
        A.GaussianBlur(blur_limit=3, p=0.2),
        A.RandomFog(p=0.1),
        A.RandomRain(p=0.1),
        A.GaussNoise(p=0.2),
    ])


def get_val_augmentation():
    return A.Compose([])