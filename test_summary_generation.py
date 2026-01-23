#!/usr/bin/env python3
"""Test AI summary generation on a sample audio file."""

import sys
sys.path.insert(0, '/srv/project_wizard')

from pathlib import Path
import whisper
from transcribe_with_summary import TranscriptSummarizer

# Test with first audio file
audio_path = Path("/srv/voice_notes/inbox/Voice 251006_110014.m4a")

print(f"🎤 Testing with: {audio_path.name}")
print("=" * 60)

# Load Whisper
print("\n1️⃣ Loading Whisper model...")
model = whisper.load_model("base")

# Transcribe
print(f"2️⃣ Transcribing {audio_path.name}...")
result = model.transcribe(str(audio_path), language="en")
transcript = result["text"].strip()
print(f"   ✓ Got {len(transcript)} characters")
print(f"\n   Preview: {transcript[:200]}...")

# Generate summary
print("\n3️⃣ Generating AI summary...")
summarizer = TranscriptSummarizer()
summary = summarizer.generate_summary(transcript, audio_path.name)

# Output
print("\n" + "=" * 60)
print("📄 GENERATED SUMMARY:")
print("=" * 60)
print(summary)
print("\n" + "=" * 60)
print("✅ Test complete!")
