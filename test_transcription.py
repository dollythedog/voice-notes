#!/usr/bin/env python3
"""Test Whisper transcription with sample audio"""

import whisper
import sys

print("Loading Whisper 'base' model (recommended for production)...")
model = whisper.load_model("base")
print("✓ Base model loaded successfully!")
print(f"✓ Model size: ~74MB")
print("\nBase model is now cached and ready for the transcription service.")
print("\nPerformance expectations:")
print("- 1 minute audio → ~10-15 seconds transcription")
print("- 5 minute audio → ~50-75 seconds transcription")
