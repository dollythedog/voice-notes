# Voice Notes Transcription System

## Overview
Automated voice note transcription system using OpenAI Whisper for Logseq integration.

## Installation Status
✅ **Phase 1 Complete** - Whisper installed and tested (2025-12-09)
✅ **Phase 2 Complete** - Transcription service running (2025-12-09)

## Quick Start

### Service Management
```bash
# Check if service is running
sudo systemctl status voice-transcription.service

# View live logs
sudo journalctl -u voice-transcription.service -f

# Or use helper script
/srv/voice_notes/service_control.sh status
/srv/voice_notes/service_control.sh logs
```

### Testing
To test the transcription:
1. Copy an audio file to `/srv/voice_notes/inbox/`
2. Watch the logs: `sudo journalctl -u voice-transcription.service -f`
3. Check the output in `/srv/logseq_graph/pages/📥 Voice Inbox.md`
4. Original file will be moved to `/srv/voice_notes/processed/`

Example formats supported: `.mp3`, `.m4a`, `.wav`, `.ogg`, `.flac`, `.opus`

## Directory Structure
```
/srv/voice_notes/
├── inbox/                   # Drop audio files here (auto-monitored)
├── processed/               # Completed transcriptions archived here
├── logs/
│   └── transcription.log    # Service logs
├── venv/                    # Python virtual environment
├── transcribe_service.py    # Main service script
├── service_control.sh       # Helper management script
├── manual_test.sh           # Manual testing mode
└── README.md                # This file
```

## How It Works

1. **Drop audio file** → `/srv/voice_notes/inbox/`
2. **Service detects** → File watcher triggers processing
3. **Whisper transcribes** → ~10-15 seconds for 1-minute audio
4. **Smart formatting** → Detects TODOs vs regular notes
5. **Logseq output** → Appends to Voice Inbox page
6. **Archive** → Moves processed file to `/processed/`

## Features

### Smart Task Detection
Voice notes containing these keywords become TODOs:
- "TODO" or "todo"
- "Need to" / "Have to"
- "Should" / "Must"
- "Remember to" / "Remind me"

Example:
- Voice: "TODO Review the project plan with the team"
- Output: `TODO Review the project plan with the team #voice-note`

### Logseq Integration
All transcriptions append to: `/srv/logseq_graph/pages/📥 Voice Inbox.md`

Format includes:
- Timestamp (date and time)
- Original filename
- Full transcription text
- Automatic TODO formatting (if detected)
- Tags: `#voice-note`

## Installed Components
- Python 3.12.3 virtual environment
- openai-whisper 20250625
- watchdog 6.0.0 (file monitoring)
- python-dotenv 1.2.1
- torch 2.9.1 (with CUDA support)

## Cached Models
- `tiny.pt` (73MB) - Testing model
- `base.pt` (139MB) - Production model ⭐ **Active**
- Location: `~/.cache/whisper/`

## Performance
- Model loading: 2 seconds (cached)
- 1-minute audio: ~10-15 seconds transcription
- 5-minute audio: ~50-75 seconds transcription
- Supported languages: English (en) configured

## Service Configuration
- **Systemd unit:** `/etc/systemd/system/voice-transcription.service`
- **User:** ivesjl
- **Auto-start:** Enabled (starts on boot)
- **Auto-restart:** Yes (10 second delay on failure)
- **Logging:** systemd journal + `/srv/voice_notes/logs/transcription.log`

## Management Commands

Using helper script (`/srv/voice_notes/service_control.sh`):
```bash
./service_control.sh status      # Show status
./service_control.sh start       # Start service
./service_control.sh stop        # Stop service
./service_control.sh restart     # Restart service
./service_control.sh logs        # Follow live logs
./service_control.sh logs-recent # Show last 50 lines
./service_control.sh test <file> # Test with audio file
```

Direct systemd commands:
```bash
sudo systemctl status voice-transcription.service
sudo systemctl start voice-transcription.service
sudo systemctl stop voice-transcription.service
sudo systemctl restart voice-transcription.service
sudo journalctl -u voice-transcription.service -f
```

## Next Steps
1. ✅ Phase 1: Whisper setup - COMPLETE
2. ✅ Phase 2: Transcription service - COMPLETE
3. ⏭️ Phase 3: Test with audio file
4. ⏭️ Phase 3: Configure Syncthing sync
5. ⏭️ Phase 3: Set up mobile device

## Documentation
- Full plan: `/srv/logseq_graph/pages/📱 Voice Notes Integration Plan.md`
- Service logs: `sudo journalctl -u voice-transcription.service -f`
- Transcription log: `/srv/voice_notes/logs/transcription.log`

## Troubleshooting

### Service not running
```bash
sudo systemctl status voice-transcription.service
sudo journalctl -u voice-transcription.service -n 50
```

### Audio file not processing
1. Check file is in `/srv/voice_notes/inbox/`
2. Check file format is supported (mp3, m4a, wav, etc.)
3. Check service is running: `systemctl is-active voice-transcription.service`
4. Watch logs: `sudo journalctl -u voice-transcription.service -f`

### Low transcription accuracy
- Speak clearly and slowly
- Reduce background noise
- Use higher quality audio format
- Consider upgrading model: edit `/srv/voice_notes/transcribe_service.py`
  - Change `model = whisper.load_model("base")` to `"small"` or `"medium"`

## System Requirements
- ✅ Python 3.11+ (we have 3.12.3)
- ✅ 2GB+ RAM available (we have 2.8GB)
- ✅ 1GB+ disk space for models (we have 32GB)
- ✅ ffmpeg for audio processing
- ✅ Network access for initial model download

---

**Created:** 2025-12-09  
**Status:** Phase 2 Complete - Service Active 🟢  
**Ready for:** Audio file testing & mobile integration
