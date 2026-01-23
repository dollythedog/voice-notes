#!/usr/bin/env python3
"""Quick test to verify Whisper installation"""

import whisper
import sys

print("Testing Whisper installation...")
print(f"Python: {sys.version}")

try:
    print("\nLoading Whisper 'tiny' model (for quick test)...")
    model = whisper.load_model("tiny")
    print("✓ Model loaded successfully!")
    print(f"✓ Model type: {type(model)}")
    print("\nWhisper is ready to use!")
    print("\nAvailable models: tiny, base, small, medium, large")
    print("Next step: Test with an actual audio file")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    sys.exit(1)
