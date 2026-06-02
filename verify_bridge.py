import torch

try:
    # weights_only=False set kar rahe hain taake security error hat jaye
    # Yeh file humne khud banayi hai, isliye hum is par trust karte hain
    weights = torch.load('ecox_model_dual.pt', weights_only=False)
    print("✅ Test 3: Dual-Engine Bridge verified. PyTorch successfully loaded weights.")
    print(f"   Model layers detected in PyTorch: {len(weights)}")
except Exception as e:
    print(f"❌ Test 3 FAILED: Could not load bridge. Error: {e}")