# Voice Notes Transcription System - Project Rules

## Project Overview
Voice Notes is an automated voice note transcription and summarization system that integrates with Logseq. It uses OpenAI Whisper for transcription and GPT-4o-mini for intelligent summarization, supporting multiple note types (BJJ training notes, meetings, etc.) with type-specific processing rules.

## Architecture
- **Transcription Service**: `transcribe_service_v3.py` - Watches multiple inbox folders, transcribes audio using Whisper
- **Summarizer**: `summarizer_v2_revised.py` - Multi-stage summarization pipeline with OpenAI API
- **Type Manager**: `type_manager.py` - Handles type-specific configurations and domain dictionaries
- **Service Control**: Systemd service at `/etc/systemd/system/voice-transcription.service`

## Key Technologies
- **Whisper**: small model for transcription (~30-60s per minute of audio)
- **OpenAI API**: gpt-4o-mini for summarization
- **Python**: 3.12.3 with watchdog for file monitoring
- **Logseq**: Output target at `/srv/logseq_graph/pages/`

## Directory Structure
```
/srv/voice_notes/
├── inboxes/           # Type-specific input folders (e.g., bjj/, meeting/)
├── archive/           # Processed files organized by type (done/failed)
├── configs/           # Type configurations
│   └── types/         # JSON configs per type (bjj.json, meeting.json)
├── logs/              # Service logs
├── processed/         # Legacy folder from v1/v2
└── venv/              # Python virtual environment
```

## Configuration Management
- Type configs stored in `configs/types/*.json`
- Each type has: logseq_page, domain_dictionary, summary_prompt_override
- Domain dictionaries provide context for technical jargon (e.g., BJJ terms)
- Service requires `OPENAI_API_KEY` environment variable

## Development Workflow
1. Service runs as systemd daemon
2. Test changes with `./service_control.sh restart`
3. Monitor with `./service_control.sh logs` or `logs-recent`
4. Test individual files by copying to appropriate inbox: `cp audio.wav inboxes/bjj/`

## Testing
- Use `manual_test.sh` for quick tests
- `test_pipeline.sh` for full pipeline validation
- Test transcription: `test_whisper.py`, `test_transcription.py`
- Test summarization: `test_summary_generation.py`
- Integration test: `test_integration.py`

## Code Standards
- Follow PEP 8 for Python code
- Use descriptive function names and clear documentation
- Error handling with detailed logging
- Keep functions focused and modular

## Service Management
```bash
./service_control.sh status        # Check service status
./service_control.sh restart       # Restart service
./service_control.sh logs          # Follow logs
./service_control.sh logs-recent   # Last 50 lines
```

## Adding New Note Types
1. Create `configs/types/newtype.json` with logseq_page, domain_dictionary, summary_prompt_override
2. Create inbox folder: `mkdir -p inboxes/newtype`
3. Create archive folders: `mkdir -p archive/newtype/{done,failed}`
4. Restart service: `./service_control.sh restart`

## Dependencies
- openai-whisper==20250625
- watchdog==6.0.0
- torch==2.9.1
- openai (for API access)

## Mobile Integration
- Syncthing setup documented in `SYNCTHING_SETUP.md`
- Android quickstart in `ANDROID_QUICKSTART.md`
- Mobile setup guide in `MOBILE_SETUP_GUIDE.md`

## Automation
- Cronicle integration documented in `CRONICLE_SETUP.md`
- Service auto-starts on boot via systemd

## Maintenance Notes
- Whisper models cached in `~/.cache/whisper/`
- Currently using `small` model (balance of speed/accuracy)
- OpenAI API usage: ~500-1000 tokens per summary
- Monitor disk space in archive folders

## Version History
- v1: Basic transcription to Logseq
- v2: Added OpenAI summarization
- v3: Multi-type support with domain dictionaries (current)

## Security Considerations
- API keys stored in environment variables, never in code
- No sensitive data in logs (file paths and metadata only)
- Audio files archived, not uploaded to cloud

## Future Enhancements
- See `IMPLEMENTATION_SUMMARY.md` for completed features
- Potential: speaker diarization, real-time transcription, additional output formats
