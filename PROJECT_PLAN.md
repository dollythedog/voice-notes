# Voice Notes Transcription System - Project Plan

**Project:** Voice Notes Transcription Service  
**Version:** 3.1.0  
**Last Updated:** 2026-01-31  
**Status:** Production / Active Maintenance  
**Repository:** Local Git Repository  

---

## Executive Summary

The Voice Notes Transcription System is a production-ready, automated pipeline that converts audio recordings into structured, searchable knowledge base entries. The system processes voice recordings from multiple sources (desktop, mobile), transcribes them using local Whisper AI, generates context-aware summaries using OpenAI's GPT models, and integrates seamlessly with Logseq for personal knowledge management.

### Key Metrics
- **Processing Time:** ~2-5 minutes for typical 30-minute recordings
- **Supported Formats:** WAV, MP3, M4A
- **Note Types:** 3 (BJJ, Meeting, Personal)
- **Concurrent Processing:** Multi-file support via watchdog
- **Storage:** Local with automatic archival

---

## Project Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Input Sources                             │
│  Desktop (Syncthing) → Phone (Syncthing) → Direct Upload    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Inbox Directories (Type-Specific)               │
│   /inboxes/meeting/  │  /inboxes/bjj/  │  /inboxes/personal/ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              File System Monitor (Watchdog)                  │
│                transcribe_service_v3.py                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            Transcription Engine (OpenAI Whisper)             │
│              Local "small" model with timestamps             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│        AI Summarization (OpenAI GPT-4o-mini)                │
│            summarizer_local.py + type configs                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Logseq Integration & Storage                    │
│   Pages: /srv/logseq_graph/pages/YYYY-MM-DD-title.md       │
│   Journals: /srv/logseq_graph/journals/YYYY_MM_DD.md       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Archival System                            │
│         /archive/{type}/done/  │  /archive/{type}/failed/   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. transcribe_service_v3.py
**Purpose:** Main service orchestrator  
**Responsibilities:**
- Monitor multiple inbox directories using watchdog
- Detect and validate audio files (.wav, .mp3, .m4a)
- Coordinate transcription and summarization pipeline
- Manage file archival and error handling
- Journal entry creation

**Key Features:**
- File stability checking (prevents processing during sync)
- Duplicate processing prevention
- Startup scan for existing files
- Graceful error handling with failed file logging

#### 2. summarizer_local.py
**Purpose:** AI-powered content processing  
**Responsibilities:**
- Load type-specific configurations
- Apply domain-specific transcript corrections
- Generate structured summaries via OpenAI API
- Format output as Logseq-compatible markdown
- Split long transcripts into manageable sections

**Key Features:**
- Type-aware prompt engineering
- Logseq outliner format compliance
- Automatic transcript chunking (100 lines/section)
- Fallback handling for API failures

#### 3. type_manager.py
**Purpose:** Configuration management  
**Responsibilities:**
- Load JSON configurations for each note type
- Provide type detection from directory paths
- Extract prompts, domains, and templates
- Validate configuration availability

**Supported Types:**
- `bjj` - Brazilian Jiu-Jitsu training notes
- `meeting` - Professional meeting minutes
- `personal` - Personal voice memos and reflections

---

## Technical Specifications

### Dependencies
```
openai==2.15.0
openai-whisper==20250625
python-dotenv==1.2.1
watchdog==4.0.0+
```

### Environment Requirements
- **Python:** 3.8+
- **OS:** Linux (Ubuntu)
- **Memory:** 2GB+ for Whisper small model
- **Storage:** ~500MB for model + working space
- **Network:** Internet access for OpenAI API

### Configuration Files

#### .env
```bash
OPENAI_API_KEY=sk-proj-...
```

#### Type Configurations (configs/types/*.json)
```json
{
  "name": "Meeting",
  "description": "Voice notes from meetings and discussions",
  "sections": ["overview", "attendees", "key_discussion_points", ...],
  "prompts": {
    "system": "You are a professional meeting secretary...",
    "user": "Create detailed, accurate meeting minutes..."
  },
  "domains": {
    "terminology": ["approval", "stakeholder", "deliverable", ...]
  }
}
```

---

## Implementation Timeline

### Phase 1: Initial Implementation (Completed)
**Date:** December 2025  
**Deliverables:**
- ✅ Basic transcription service (v1)
- ✅ Whisper integration
- ✅ Logseq output format
- ✅ Single note type support

### Phase 2: Multi-Type System (Completed)
**Date:** January 2026  
**Deliverables:**
- ✅ Type-specific inbox monitoring
- ✅ Configuration-driven processing
- ✅ Domain-specific prompts
- ✅ Syncthing compatibility

### Phase 3: Production Hardening (Completed)
**Date:** January 28-29, 2026  
**Deliverables:**
- ✅ Timestamp support in transcripts
- ✅ File stability detection
- ✅ Startup scanning
- ✅ Environment variable management
- ✅ Enhanced error handling

### Phase 4: Logseq Integration Fixes (Completed)
**Date:** January 31, 2026  
**Deliverables:**
- ✅ Fixed metadata properties (tags::, recorded::, processed::)
- ✅ Corrected subprocess Python execution (venv support)
- ✅ Implemented transcript splitting (performance optimization)
- ✅ Logseq outliner format compliance
- ✅ Note type tag extraction

---

## Current Status

### Production Features
- ✅ Multi-type audio processing
- ✅ Automatic transcription with timestamps
- ✅ AI-powered summarization
- ✅ Logseq integration with query support
- ✅ Syncthing file sync compatibility
- ✅ Long transcript handling (split sections)
- ✅ Outliner format for editing

### Known Limitations
- Single Whisper model size (small) - no dynamic selection
- English-language optimized (multi-language support limited)
- Requires internet for AI summaries
- No real-time transcription (file-based only)

---

## Future Roadmap

### Short-Term (Next 1-3 Months)
- [ ] Add support for additional note types (lecture, interview, podcast)
- [ ] Implement retry logic with exponential backoff for API failures
- [ ] Add transcript quality metrics and confidence scores
- [ ] Create web dashboard for monitoring and management
- [ ] Add email/notification support for processing completion

### Medium-Term (3-6 Months)
- [ ] Multi-language support with language detection
- [ ] Speaker diarization (identify multiple speakers)
- [ ] Integration with project management tools (JIRA, Asana)
- [ ] Mobile app for direct recording and upload
- [ ] Batch reprocessing tool for existing files

### Long-Term (6-12 Months)
- [ ] Real-time transcription support
- [ ] Custom model fine-tuning for domain-specific terminology
- [ ] Cloud deployment option (Docker/Kubernetes)
- [ ] Multi-user support with authentication
- [ ] API for external integrations

---

## Success Criteria

### Performance Metrics
- **Transcription Accuracy:** >95% word accuracy for clear audio
- **Processing Speed:** <5 minutes for 30-minute recording
- **Uptime:** >99% service availability
- **Error Rate:** <1% failed processing

### Quality Metrics
- **Summary Relevance:** User satisfaction >90%
- **Metadata Accuracy:** 100% compliance with Logseq format
- **Note Discoverability:** All notes queryable in Logseq

---

## Maintenance & Operations

### Service Management
```bash
# Start service
./service_control.sh start

# Stop service
./service_control.sh stop

# Restart service
./service_control.sh restart

# View logs
./service_control.sh logs
```

### Monitoring Points
1. **Inbox Directories:** Ensure files are being detected
2. **Processing Logs:** Check for errors in transcription.log
3. **Archive Directories:** Verify files move to done/failed
4. **Logseq Pages:** Confirm new pages are created
5. **OpenAI API:** Monitor usage and rate limits

### Backup Strategy
- **Configurations:** Git version control
- **Audio Files:** Archived in /archive/{type}/done/
- **Logseq Pages:** Synced via Logseq's native sync
- **Logs:** Rotated daily, kept for 30 days

---

## Risk Assessment

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API outage | Medium | High | Implement fallback format, queue for retry |
| Disk space exhaustion | Low | High | Automated cleanup, alerts at 80% capacity |
| Whisper model corruption | Low | Medium | Model validation on startup, backup copy |
| Syncthing sync conflicts | Medium | Low | Conflict detection and manual resolution |

### Operational Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Service crash | Low | Medium | Systemd auto-restart, health checks |
| Configuration errors | Medium | Medium | Schema validation, config tests |
| API key exposure | Low | High | Environment variables, .gitignore |

---

## Team & Responsibilities

**Primary Developer:** Jonathan Ives  
**AI Assistant:** Warp (Co-Author)  
**Deployment Environment:** Local Ubuntu server (bunto-server)  
**User Base:** Personal use (single user)

---

## References

- [CHANGELOG.md](CHANGELOG.md) - Version history and changes
- [README.md](README.md) - Quick start and usage guide
- [MAINTENANCE.md](MAINTENANCE.md) - Maintenance procedures
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Logseq Documentation](https://docs.logseq.com)
