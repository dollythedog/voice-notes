# Voice Notes + AI Summary Integration

## What's New

Your voice notes now get AI-powered structured summaries using the project_wizard agent pipeline:

- **Overview**: 2-3 sentence summary
- **Key Points**: Main ideas in bullets
- **Detailed Notes**: Organized breakdown with sub-bullets
- **Next Steps**: Extracted action items and follow-ups
- **Raw Transcript**: Collapsible section with original text

## Files Created

```
/srv/voice_notes/
├── summarizer.py              # AI summarization using project_wizard agents
├── transcribe_service_v2.py   # New service (Whisper + AI)
└── transcribe_service.py      # Original (Whisper only)

/srv/project_wizard/patterns/transcript_summary/
├── blueprint.json             # Summary structure config
├── prompts.json              # AI agent instructions
└── template.j2               # Output format template
```

## Quick Test

Test the summarizer with a sample transcript:

```bash
# Create test transcript
echo "I need to review the project plan by Friday. The main tasks are updating the database schema and fixing the authentication bug. Also should probably schedule a team meeting next week to discuss the new feature requirements." > /tmp/test.txt

# Generate summary
echo -e "$(cat /tmp/test.txt)\n---FILENAME---\ntest_note.m4a" | \
  /srv/project_wizard/venv/bin/python3 /srv/voice_notes/summarizer.py
```

## Running the New Service

### Option 1: Test Mode (one file)
```bash
# Activate voice_notes venv
source /srv/voice_notes/venv/bin/activate

# Process one audio file manually
python3 -c "
import whisper
from pathlib import Path
import subprocess

audio = Path('/srv/voice_notes/inbox/Voice 251006_110014.m4a')
model = whisper.load_model('base')
result = model.transcribe(str(audio), language='en')
transcript = result['text'].strip()

# Generate summary
proc = subprocess.run(
    ['/srv/project_wizard/venv/bin/python3', '/srv/voice_notes/summarizer.py'],
    input=f'{transcript}\n---FILENAME---\n{audio.name}',
    capture_output=True,
    text=True
)

print(proc.stdout)
"
```

### Option 2: Replace Service
```bash
# Stop old service
./service_control.sh stop

# Update service to use v2
mv transcribe_service.py transcribe_service_old.py
mv transcribe_service_v2.py transcribe_service.py

# Start service
./service_control.sh start
```

## How It Works

1. **Whisper** transcribes audio in voice_notes venv
2. **Subprocess call** to project_wizard venv runs summarizer.py
3. **AI agents** generate sections sequentially (prevents hallucination)
4. **Template** renders formatted markdown with collapsible transcript
5. **Logseq** gets appended with rich summary

## Customization

Edit `/srv/project_wizard/patterns/transcript_summary/prompts.json` to adjust:
- Section lengths
- Summary style
- What counts as an action item
- Tone and formatting
