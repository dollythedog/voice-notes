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

### Fixed - 2026-01-31
- **Missing Logseq metadata in meeting notes**: Fixed fallback format to include proper `tags::`, `recorded::`, and `processed:: false` properties so notes appear in Logseq queries
- **AI summary not generated**: Fixed subprocess call to use `sys.executable` instead of hardcoded `python3`, ensuring the venv's Python interpreter with required packages (openai, python-dotenv) is used
- **Note type tag extraction**: Fixed note_type parameter passing in `summarizer_local.py` to correctly tag notes (e.g., `#meeting`, `#bjj`, `#personal`) instead of blank tags
- **Logseq performance issues with long transcripts**: Implemented transcript splitting into chunks of 100 lines per collapsible section to prevent performance degradation
- **Transcript not in outliner format**: Fixed transcript formatting to prefix each line with `- ` so Logseq treats them as separate editable blocks instead of a single uneditable blob

### Changed - 2026-01-31
- Updated `transcribe_service_v3.py`:
  - Changed subprocess call from `"python3"` to `sys.executable`
  - Enhanced `_format_fallback()` to include full Logseq metadata header
- Updated `summarizer_local.py`:
  - Modified `format_output_logseq()` to accept `note_type` as parameter
  - Added transcript line formatting as Logseq bullets (`- ` prefix)
  - Implemented automatic transcript splitting for transcripts >100 lines
  - Fixed note type tag to use passed parameter instead of extracting from filename path
