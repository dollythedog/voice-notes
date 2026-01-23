# Voice Notes System v3 - Multi-Type Transcription & Summarization

## Overview

A **production-ready voice-to-knowledge-base system** that automatically:
1. Monitors type-specific inboxes (BJJ, meetings, personal notes, etc.)
2. Transcribes audio using Whisper (small model)
3. Generates AI-powered, domain-specific summaries using OpenAI
4. Saves structured summaries to Logseq
5. Archives processed files with full error handling

**Key improvements over v2:**
- Multi-type support with config-driven extensibility
- Independent from project_wizard (OpenAI API only)
- Domain-specific terminology dictionaries for accuracy
- Robust file pipeline: inbox → done/failed archive
- Syncthing-based desktop sync for easy file upload

---

## Architecture

```
Desktop (Syncthing) → Server Inboxes → Transcription → Summarization → Logseq
                                              ↓              ↓
                                         Whisper        OpenAI API
                                          (small)       (gpt-4o-mini)
                                              ↓
                                         Archive (done/failed)
```

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| `transcribe_service_v3.py` | Main service, monitors inboxes | Watchdog file events |
| `summarizer_local.py` | Standalone summarizer | OpenAI Chat API |
| `type_manager.py` | Config loader & type detector | JSON config system |
| `configs/types/*.json` | Type definitions & prompts | Configuration |
| Systemd service | Process management | `voice-transcription.service` |

---

## Quick Start

### 1. Verify Service is Running
```bash
cd /srv/voice_notes
./service_control.sh status
```

### 2. Ensure OPENAI_API_KEY is Set
```bash
echo $OPENAI_API_KEY
# Should output your API key. If not:
export OPENAI_API_KEY="sk-..."
# Then restart service: ./service_control.sh restart
```

### 3. Test with Local File
```bash
# Place test audio in inbox
cp ~/Downloads/test_bjj.wav /srv/voice_notes/inboxes/bjj/
# Watch progress
./service_control.sh logs
# File should move to archive/bjj/done/ after ~2-3 minutes
```

### 4. Configure Syncthing (Desktop)
See [`SYNCTHING_SETUP.md`](./SYNCTHING_SETUP.md) for step-by-step instructions.

---

## Directory Structure

```
/srv/voice_notes/
├── inboxes/                    # Input directories (watched)
│   ├── bjj/                   # BJJ class recordings
│   ├── meeting/               # Meeting recordings
│   └── personal/              # Personal notes
├── archive/                   # Processed files
│   ├── bjj/done/             # Successfully processed BJJ files
│   ├── bjj/failed/           # Failed BJJ files (with error logs)
│   ├── meeting/done/
│   ├── meeting/failed/
│   └── ...
├── configs/
│   └── types/                 # Type configurations
│       ├── bjj.json          # BJJ config (techniques, positions)
│       └── meeting.json       # Meeting config (agenda, decisions)
├── logs/
│   └── transcription.log      # Service logs
├── transcribe_service_v3.py   # Main service (v3)
├── summarizer_local.py        # Standalone summarizer
├── type_manager.py            # Config loader
└── venv/                      # Python virtual environment
```

---

## Type Configuration System

Each note type is configured via JSON in `configs/types/`:

### Structure
```json
{
  "name": "Note Type Name",
  "description": "What this type is for",
  "sections": ["section1", "section2"],
  "prompts": {
    "system": "LLM system prompt",
    "user": "LLM user prompt with {{transcript}} placeholder"
  },
  "domains": {
    "terminology": ["term1", "term2"],
    "positions": ["position1", "position2"]
  },
  "output_template": "Markdown template with {{placeholders}}"
}
```

### Example: BJJ Config
```json
{
  "sections": [
    "techniques_demonstrated",
    "key_positions",
    "drills_practiced",
    "principles_taught",
    "personal_notes"
  ],
  "domains": {
    "techniques": ["armbar", "triangle choke", "rear naked choke", ...],
    "positions": ["mount", "guard", "side control", ...],
    "concepts": ["pressure", "timing", "leverage", ...]
  }
}
```

### Adding a New Type
1. Create folder: `mkdir -p /srv/voice_notes/inboxes/{type}`
2. Create config: `cp configs/types/meeting.json configs/types/{type}.json`
3. Edit config with custom prompts and domains
4. Restart service: `./service_control.sh restart`

---

## File Processing Pipeline

### Flow per Audio File

```
1. File Detection
   └─ Watchdog detects new file in inbox/{type}/

2. Validation
   ├─ Check file extension (mp3, m4a, wav, ogg, flac, opus)
   ├─ Wait 2s for write completion
   └─ Verify file size > 0

3. Transcription
   └─ Whisper model.transcribe() → raw transcript

4. Post-Processing
   └─ Apply domain dict corrections (terminology fixes)

5. Summarization
   ├─ Load type config
   ├─ Call summarizer_local.py via subprocess
   └─ OpenAI API generates summary

6. Storage
   ├─ Save to /srv/logseq_graph/pages/{page_name}.md
   └─ Add entry to daily journal

7. Archival
   ├─ Move file to archive/{type}/done/
   └─ Log: "✅ Complete: {filename}"

(On Error at any step)
   └─ Move to archive/{type}/failed/
   └─ Write error log: {filename}_error.txt
```

### File Movement Example

**Input:** `/srv/voice_notes/inboxes/bjj/Class-Mount-Escape.wav`

**Success:**
- Logseq page: `/srv/logseq_graph/pages/2025-01-22-Class-Mount-Escape.md`
- Archive: `/srv/voice_notes/archive/bjj/done/Class-Mount-Escape.wav`

**Failure:**
- Archive: `/srv/voice_notes/archive/bjj/failed/Class-Mount-Escape.wav`
- Error log: `/srv/voice_notes/archive/bjj/failed/Class-Mount-Escape_error.txt`

---

## Supported Formats

Audio formats (auto-detected):
- `.mp3`, `.m4a`, `.wav` ← Most common
- `.ogg`, `.flac`, `.opus`

Recommended: `.wav` (highest Whisper accuracy)

---

## Performance Characteristics

| Operation | Duration |
|-----------|----------|
| Whisper small transcription | 30-60s per minute of audio |
| OpenAI summarization | 5-10s (depends on transcript length) |
| Total (10-min recording) | ~2-3 minutes |
| Whisper model load | ~5-10s (on startup) |

**Memory:** ~550MB resident (Whisper small + Logseq output buffer)

---

## Domain Dictionaries

Terminology post-processing applies domain-specific corrections to the Whisper output before LLM summarization.

### How It Works
1. Whisper transcribes: "the armbar and the triangle choke"
2. Domain dict has: `"armbar"`, `"triangle choke"`
3. Corrected: "the armbar and the triangle choke" (no change if correct)
4. LLM receives clean transcript for accurate summarization

### BJJ Dictionary Included
- **Techniques:** armbar, triangle choke, rear naked choke, guillotine, kimura, etc.
- **Positions:** mount, guard, side control, north south, etc.
- **Concepts:** pressure, timing, leverage, hip escape, etc.

### Expanding Dictionary
Edit `/srv/voice_notes/configs/types/bjj.json`:
```json
"domains": {
  "techniques": [
    "armbar",
    "NEW_TECHNIQUE"  ← Add here
  ]
}
```
Restart service.

---

## Error Handling

### Common Issues & Solutions

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="sk-..."
./service_control.sh restart
```

**"Unknown note type"**
- Ensure config exists in `configs/types/{type}.json`
- Verify inbox folder name matches type name

**"File not ready"**
- Service waits 2s for file write completion
- Transient file system issues; usually resolves on retry

**"Summarizer error"**
- Check `/srv/voice_notes/logs/transcription.log`
- May indicate OpenAI API error
- File moved to `archive/{type}/failed/` with error log

### Debug Steps
```bash
# Follow live logs
./service_control.sh logs

# Check last 50 lines
./service_control.sh logs-recent

# Check service status
./service_control.sh status

# View failed file error
cat /srv/voice_notes/archive/bjj/failed/filename_error.txt
```

---

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY          # Required. OpenAI API key.
```

### Whisper Model Selection
Edit `transcribe_service_v3.py`, line 53:
```python
self.whisper_model = whisper.load_model("small")  # base, small, medium, large
```
- `base`: Faster, ~139MB (default in v2)
- `small`: Balanced (v3 default), ~1GB, better accuracy
- `medium`: High accuracy, ~3GB, ~5-10x slower
- `large`: Highest accuracy, ~3GB, very slow

### Service Management
Edit `/etc/systemd/system/voice-transcription.service` to change:
- User/group
- Working directory
- Restart policy
- Resource limits

---

## Monitoring

### Service Status
```bash
sudo systemctl status voice-transcription.service
```

### Real-Time Logs
```bash
sudo journalctl -u voice-transcription.service -f
```

### File Archives
```bash
# Count processed files
ls -la /srv/voice_notes/archive/bjj/done/ | wc -l

# Check failed files
ls -la /srv/voice_notes/archive/bjj/failed/
```

### Logseq Integration
- Pages appear in `/srv/logseq_graph/pages/` with date prefix
- Journal entries in `/srv/logseq_graph/journals/{YYYY_MM_DD}.md` with type tag
- Query: `#bjj #inbox` to see all BJJ voice notes

---

## API Integration

### Summarizer Subprocess Call
```bash
echo "transcript text" | python3 summarizer_local.py bjj filename.wav
```

Invoked by `transcribe_service_v3.py` for each audio file.

### OpenAI API Details
- Model: `gpt-4o-mini` (cost-effective)
- Temperature: 0.7 (balanced creativity/consistency)
- Max tokens: 2000 (summary length limit)
- Timeout: 120s per call

---

## Maintenance

### Regular Tasks
1. **Monitor archive size:** `du -sh /srv/voice_notes/archive/`
2. **Review failed files:** `ls /srv/voice_notes/archive/*/failed/`
3. **Check logs for errors:** `grep "ERROR" /srv/voice_notes/logs/transcription.log`

### Cleanup
```bash
# Remove old archives (keep 30 days)
find /srv/voice_notes/archive -mtime +30 -delete
```

---

## Development & Extension

### Adding Custom Post-Processing
Edit `summarizer_local.py`, function `correct_transcript_with_domain()`:
- Currently applies domain dict term replacement
- Can add regex-based corrections, phonetic fixes, etc.

### Custom Summarization Strategy
Edit `summarizer_local.py`, function `generate_summary()`:
- Currently uses OpenAI Chat API
- Could integrate with local LLM (Ollama), fine-tuned models, etc.

### Type-Specific Logic
Add to `type_manager.py`:
- Custom validation rules per type
- Special output formatting
- Type-specific archive retention policies

---

## Changelog

### v3.0 (Current)
- ✅ Multi-type support with config system
- ✅ Independent from project_wizard (OpenAI direct)
- ✅ Domain dictionaries for terminology correction
- ✅ Upgraded Whisper to small model
- ✅ File pipeline: inbox → done/failed
- ✅ Syncthing integration guide
- ✅ `.wav` support

### v2.0
- Whisper base + project_wizard summarizer
- Single inbox, all files treated as generic notes
- No domain dictionaries
- Files moved to /processed directory

### v1.0
- Initial Whisper transcription only

---

## FAQ

**Q: Can I change the summary format?**
A: Yes, edit the `output_template` in your type config JSON, or customize `format_output()` in `summarizer_local.py`.

**Q: How do I add more BJJ techniques to the dictionary?**
A: Edit `configs/types/bjj.json`, add terms to appropriate `domains` category, restart service.

**Q: Can I run this without OpenAI?**
A: Yes, edit `summarizer_local.py` to use a local LLM or rule-based summarization. Contact for help.

**Q: How are files synced to the server?**
A: Via Syncthing, which watches your desktop folders and auto-syncs to `/srv/voice_notes/inboxes/{type}/`.

**Q: What happens if the service crashes?**
A: Systemd automatically restarts it (10s delay). Check logs at `transcription.log`.

---

## Support & Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u voice-transcription.service -n 50 --no-pager
```

**Files not moving to archive:**
```bash
grep -i error /srv/voice_notes/logs/transcription.log
cat /srv/voice_notes/archive/{type}/failed/*_error.txt
```

**Summarization not working:**
- Check `OPENAI_API_KEY` is set
- Test API manually: `python3 -c "from openai import OpenAI; print(OpenAI())"`
- Verify API key has available credits

---

**For detailed Syncthing setup, see:** [SYNCTHING_SETUP.md](./SYNCTHING_SETUP.md)

**For type configuration examples, see:** `configs/types/`
