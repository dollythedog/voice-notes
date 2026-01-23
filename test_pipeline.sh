#!/bin/bash
# Test the complete pipeline

echo "🧪 Testing Voice Notes Pipeline"
echo "================================"

# Pick a small audio file
AUDIO="/srv/voice_notes/inbox/Voice 251006_110014.m4a"

if [ ! -f "$AUDIO" ]; then
    echo "❌ Test audio not found: $AUDIO"
    exit 1
fi

echo "📁 Test file: $(basename "$AUDIO")"
echo ""

# Step 1: Transcribe with Whisper
echo "1️⃣ Transcribing with Whisper..."
source /srv/voice_notes/venv/bin/activate
TRANSCRIPT=$(python3 << PYEOF
import whisper
model = whisper.load_model("base")
result = model.transcribe("$AUDIO", language="en")
print(result["text"].strip())
PYEOF
)

echo "✓ Transcript (${#TRANSCRIPT} chars):"
echo "$TRANSCRIPT" | head -c 200
echo "..."
echo ""

# Step 2: Generate AI summary
echo "2️⃣ Generating AI summary..."
SUMMARY=$(echo -e "$TRANSCRIPT\n---FILENAME---\n$(basename "$AUDIO")" | /srv/project_wizard/venv/bin/python3 /srv/voice_notes/summarizer.py 2>&1)

if [ $? -eq 0 ]; then
    echo "✓ Summary generated!"
    echo ""
    echo "================================"
    echo "📄 OUTPUT:"
    echo "================================"
    echo "$SUMMARY"
else
    echo "❌ Summary generation failed:"
    echo "$SUMMARY"
    exit 1
fi

echo ""
echo "✅ Pipeline test complete!"
