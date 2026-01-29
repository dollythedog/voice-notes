# Voice Notes Transcription Service v3

Automated voice note transcription and AI summarization service with Logseq integration.

## Features

- 🎤 **Automatic transcription** using OpenAI Whisper (local)
- ⏱️ **Timestamped transcripts** for easy navigation of long recordings
- 🤖 **AI-powered summaries** using OpenAI GPT models
- 📝 **Multi-type support** - BJJ, meeting, and personal notes with custom prompts
- 🔄 **Syncthing compatible** - detects files synced from other devices
- 📚 **Logseq integration** - auto-creates pages and journal entries
- 🔍 **Startup scanning** - processes existing files on service start

## Quick Start

### 1. Setup

```bash
# Install dependencies
cd /srv/voice_notes
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Configure Note Types

Edit configs in `/srv/voice_notes/configs/types/`:
- `bjj.json` - Brazilian Jiu-Jitsu training notes
- `meeting.json` - Meeting notes
- `personal.json` - Personal voice memos

### 3. Start Service

```bash
cd /srv/voice_notes
nohup python transcribe_service_v3.py > logs/transcription.log 2>&1 &
```

### 4. Use It

Drop audio files (`.wav`, `.mp3`, `.m4a`) into:
- `/srv/voice_notes/inboxes/personal/`
- `/srv/voice_notes/inboxes/bjj/`
- `/srv/voice_notes/inboxes/meeting/`

Files are automatically:
1. Transcribed with timestamps
2. Summarized with AI
3. Saved to Logseq pages
4. Archived

## Output Format

```markdown
# 💭 Filename

tags:: #personal #voice-note #2026-01-29
type:: personal
recorded:: [[2026-01-29]]

---

## Summary
- Main points extracted from conversation
- Action items and decisions
- Key insights

---

## 📄 Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

(0:00) Opening remarks and context.
(0:15) Main discussion points.
(0:45) Follow-up and clarifications.

</details>
```

## Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-...
```

### Type Configurations

Each note type has a config file with:
- **prompts**: System and user prompts for AI summarization
- **domains**: Domain-specific terminology for transcript correction
- **sections**: Output sections for the summary
- **output_template**: Markdown template for the final output

## Troubleshooting

### Summaries not generating
- Check `.env` file exists with valid `OPENAI_API_KEY`
- Verify service has loaded environment: `ps eww -p <pid> | grep OPENAI`
- Check logs: `tail -f /srv/voice_notes/logs/transcription.log`

### Files not processing
- Ensure file extensions are supported (`.wav`, `.mp3`, `.m4a`)
- Check file is stable (not being written) - service waits 3 seconds
- Restart service to trigger startup scan: `pkill -f transcribe_service_v3; python transcribe_service_v3.py`

### Syncthing files not detected
- Service now handles `on_modified` and `on_moved` events
- Files should process automatically when sync completes
- If not, service restart will trigger startup scan

## Architecture

```
voice_notes/
├── transcribe_service_v3.py   # Main service (file watcher)
├── summarizer_local.py         # AI summarization
├── type_manager.py             # Type config loader
├── .env                        # API keys (not in git)
├── inboxes/                    # Drop files here
│   ├── personal/
│   ├── bjj/
│   └── meeting/
├── configs/
│   └── types/                  # Type configurations
│       ├── personal.json
│       ├── bjj.json
│       └── meeting.json
├── archive/                    # Processed files
│   ├── personal/done/
│   └── personal/failed/
└── logs/
    └── transcription.log       # Service logs
```

## Recent Updates (2026-01-29)

See [CHANGELOG.md](CHANGELOG.md) for full details.

**Major Fixes:**
- ✅ AI summaries now work for all note types
- ✅ Timestamps in transcripts for readability
- ✅ Syncthing file detection fixed
- ✅ Startup file scanning added
- ✅ Environment variable loading fixed

## License

Private project
