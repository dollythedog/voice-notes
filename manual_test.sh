#!/bin/bash
# Manual test of the transcription service

echo "======================================"
echo "Voice Notes Transcription - Manual Test"
echo "======================================"
echo ""
echo "This will start the transcription service."
echo "To test it:"
echo "1. Open another terminal"
echo "2. Copy an audio file to: /srv/voice_notes/inbox/"
echo "3. Watch the logs here"
echo "4. Press Ctrl+C to stop when done"
echo ""
echo "Starting service in 3 seconds..."
sleep 3

cd /srv/voice_notes
source venv/bin/activate
python transcribe_service.py
