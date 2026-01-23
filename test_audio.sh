#!/bin/bash
# Generate a simple test audio file using espeak (text-to-speech)

# Check if espeak is available
if ! command -v espeak &> /dev/null; then
    echo "Installing espeak for testing..."
    sudo apt install -y espeak > /dev/null 2>&1
fi

# Generate test audio
echo "Generating test audio file..."
espeak "TODO Review the voice notes integration plan. This is a test of the transcription service." -w /srv/voice_notes/test_sample.wav

echo "Test audio created: /srv/voice_notes/test_sample.wav"
echo "File size: $(du -h /srv/voice_notes/test_sample.wav | cut -f1)"
