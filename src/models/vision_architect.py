"""
vision_architect.py — Compatibility wrapper
Main implementation: upgrade_brain.py
"""
from src.models.upgrade_brain import build_futuristic_brain
from src.utils.constants import CONFIG


def build_futuristic_brain(num_classes=None):
    """Wrapper — upgrade_brain.py use karta hai"""
    model, _ = build_futuristic_brain(num_classes)
    return model