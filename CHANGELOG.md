# Changelog

All notable changes to the Voice Notes Transcription Service will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added - 2026-01-29
- **Timestamp support in transcripts**: Whisper now outputs transcripts with segment timestamps in format `(MM:SS) text` for better readability
- **OpenAI API integration**: Added `.env` file support and `python-dotenv` loading for secure API key management
- **Enhanced file detection**: Added `on_modified()` and `on_moved()` handlers to catch Syncthing file sync events
- **Startup file scanning**: Service now processes existing files in inbox on startup
- **File stability checking**: Added `_is_file_stable()` method to ensure files are fully synced before processing
- **Processed files tracking**: Prevents duplicate processing of the same file

### Fixed - 2026-01-29
- **Summary generation for personal notes**: Fixed OpenAI API key not being loaded, summaries were falling back to raw transcript only
- **Personal note config**: Simplified prompt to generate detailed, point-by-point summaries
- **Syncthing compatibility**: Files synced via Syncthing now trigger processing correctly
- **Duplicate handler creation**: Fixed startup scan creating duplicate handlers

### Changed - 2026-01-29
- Updated `transcribe_service_v3.py` to load environment variables from `.env`
- Updated `summarizer_local.py` to load environment variables from `.env`
- Modified `_transcribe()` method to include word-level timestamps
- Updated personal note type configuration with simpler, more direct prompts

## [3.0.0] - 2026-01-27
### Added
- Multi-type support (bjj, meeting, personal)
- Type-specific configurations and prompts
- Dedicated inbox folders per type

## [2.0.0] - Prior
### Added
- Initial multi-stage summarization
- Domain-specific corrections
- Logseq integration
