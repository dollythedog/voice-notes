# Voice Notes Transcription System - Issues Tracker

**Last Updated:** 2026-01-31  
**Version:** 3.1.0

This document tracks known issues, resolved issues, and planned improvements for the Voice Notes Transcription System.

---

## Status Legend
- 🔴 **Critical** - System-breaking, requires immediate attention
- 🟡 **High** - Significant impact on functionality or user experience
- 🟢 **Medium** - Minor impact, workaround available
- 🔵 **Low** - Nice to have, minimal impact
- ✅ **Resolved** - Issue has been fixed
- 🚧 **In Progress** - Currently being worked on
- 📋 **Backlog** - Planned for future release

---

## Recently Resolved Issues (2026-01-31)

### ✅ Issue #1: Missing Logseq Metadata in Generated Notes
**Status:** Resolved  
**Severity:** 🔴 Critical  
**Date Reported:** 2026-01-30  
**Date Resolved:** 2026-01-31

**Description:**  
Meeting notes were being generated without proper Logseq metadata properties (`tags::`, `recorded::`, `processed::`), preventing them from appearing in Logseq queries. The fallback format in `transcribe_service_v3.py` only included the summary and transcript without the required header.

**Impact:**  
- Voice notes were invisible to Logseq's query system
- Unable to track processing status
- Notes not categorized by type

**Root Cause:**  
The `_format_fallback()` function in `transcribe_service_v3.py` did not include metadata properties, only providing raw summary and transcript sections.

**Resolution:**  
Updated `_format_fallback()` to include:
```markdown
# 🎙️ {title}

tags:: #voice-note #{note_type} #inbox
recorded:: [[{date}]]
processed:: false

---
```

**Files Changed:**
- `transcribe_service_v3.py`

---

### ✅ Issue #2: AI Summary Generation Failure
**Status:** Resolved  
**Severity:** 🔴 Critical  
**Date Reported:** 2026-01-30  
**Date Resolved:** 2026-01-31

**Description:**  
AI summaries were not being generated for meeting notes. The system was falling back to "Unable to generate AI summary" message despite OpenAI API key being correctly configured in `.env`.

**Impact:**  
- No AI-generated summaries for meetings
- Loss of key meeting insights (attendees, action items, decisions)
- Manual summary creation required

**Root Cause:**  
The subprocess call in `transcribe_service_v3.py` used hardcoded `"python3"` instead of `sys.executable`, causing the subprocess to use the system Python rather than the virtual environment Python. This meant the subprocess couldn't access installed packages (openai, python-dotenv).

**Resolution:**  
Changed subprocess call from:
```python
["python3", str(BASE_DIR / "summarizer_local.py"), ...]
```
to:
```python
[sys.executable, str(BASE_DIR / "summarizer_local.py"), ...]
```

**Files Changed:**
- `transcribe_service_v3.py`

---

### ✅ Issue #3: Incorrect Note Type Tags
**Status:** Resolved  
**Severity:** 🟡 High  
**Date Reported:** 2026-01-31  
**Date Resolved:** 2026-01-31

**Description:**  
Note type tags were showing as blank (`#`) instead of the correct type (`#meeting`, `#bjj`, `#personal`). The summarizer was trying to extract the note type from the filename path using `Path(filename).parent.name`, but the filename parameter only contained the audio filename, not the full path.

**Impact:**  
- Notes not properly categorized by type
- Queries filtering by note type wouldn't work
- Difficult to distinguish between note types in Logseq

**Root Cause:**  
The `note_type` was available in the main() function but wasn't being passed to `format_output_logseq()`. The function tried to extract it from the filename path, which only contained the base filename.

**Resolution:**  
1. Updated `format_output_logseq()` signature to accept `note_type` parameter
2. Changed extraction logic from `Path(filename).parent.name` to use passed `note_type`
3. Updated the function call in main() to pass `note_type`

**Files Changed:**
- `summarizer_local.py`

---

### ✅ Issue #4: Logseq Performance Issues with Long Transcripts
**Status:** Resolved  
**Severity:** 🟡 High  
**Date Reported:** 2026-01-31  
**Date Resolved:** 2026-01-31

**Description:**  
Long transcripts (800+ lines) were causing severe performance degradation in Logseq. The entire transcript was placed in a single block, making the page slow to load and difficult to edit.

**Impact:**  
- Logseq UI became unresponsive when opening notes with long transcripts
- Could not edit or navigate transcript content
- User experience significantly degraded for meeting notes

**Root Cause:**  
Transcripts were output as a single large text block without line breaks or structure, causing Logseq to treat it as one massive block.

**Resolution:**  
Implemented automatic transcript splitting:
- Split transcripts into chunks of 100 lines
- Each chunk wrapped in separate `<details>` sections
- Sections labeled "Part X of Y" for easy navigation
- Example: 833-line transcript → 9 sections of ~100 lines each

**Files Changed:**
- `summarizer_local.py`

---

### ✅ Issue #5: Transcript Not in Logseq Outliner Format
**Status:** Resolved  
**Severity:** 🟡 High  
**Date Reported:** 2026-01-31  
**Date Resolved:** 2026-01-31

**Description:**  
Transcript lines were not formatted as Logseq bullets, causing them to appear as a single uneditable text blob. Users couldn't edit individual transcript lines or collapse/expand sections.

**Impact:**  
- Transcript content not editable in Logseq
- Could not use Logseq's outliner features on transcript
- Poor user experience for reviewing/editing transcripts

**Root Cause:**  
Transcript lines were output as plain text without the required `- ` prefix that Logseq uses to identify outliner blocks.

**Resolution:**  
Modified transcript formatting to prefix each line with `- `:
```python
transcript_bullets = [f"- {line}" for line in transcript_lines if line.strip()]
```

**Files Changed:**
- `summarizer_local.py`

---

## Open Issues

### 📋 Issue #6: No Retry Logic for API Failures
**Status:** Backlog  
**Severity:** 🟢 Medium  
**Date Reported:** 2026-01-31

**Description:**  
When OpenAI API calls fail (timeout, rate limit, network error), the system immediately falls back to the basic format without retrying.

**Proposed Solution:**  
Implement exponential backoff retry logic with configurable attempts (e.g., 3 retries with 1s, 2s, 4s delays).

**Priority:** Medium  
**Estimated Effort:** 2-4 hours

---

### 📋 Issue #7: No Language Detection / Multi-Language Support
**Status:** Backlog  
**Severity:** 🔵 Low  
**Date Reported:** 2026-01-31

**Description:**  
System is optimized for English transcription. Non-English audio may have poor transcription quality or summaries.

**Proposed Solution:**  
- Add language detection to Whisper transcription
- Pass detected language to OpenAI for better summaries
- Support language-specific prompts and configurations

**Priority:** Low  
**Estimated Effort:** 4-8 hours

---

### 📋 Issue #8: Single Whisper Model Size
**Status:** Backlog  
**Severity:** 🔵 Low  
**Date Reported:** 2026-01-31

**Description:**  
Currently uses only the "small" Whisper model. No option to use larger models for better accuracy or smaller models for faster processing.

**Proposed Solution:**  
Add configuration option to select Whisper model size (tiny, base, small, medium, large).

**Priority:** Low  
**Estimated Effort:** 1-2 hours

---

### 📋 Issue #9: No Web Dashboard for Monitoring
**Status:** Backlog  
**Severity:** 🔵 Low  
**Date Reported:** 2026-01-31

**Description:**  
No visual interface for monitoring processing status, viewing logs, or managing files. All monitoring must be done via CLI and log files.

**Proposed Solution:**  
Create lightweight web dashboard (Flask/Streamlit) showing:
- Processing queue status
- Recent transcriptions
- Error logs
- System health metrics

**Priority:** Low  
**Estimated Effort:** 8-16 hours

---

## Known Limitations

### English Language Optimization
**Impact:** 🟢 Medium  
**Status:** Accepted

The system is optimized for English-language audio. While Whisper supports multiple languages, prompts and domain terminology are English-focused.

**Workaround:** None currently available for non-English audio.

---

### Internet Required for AI Summaries
**Impact:** 🟢 Medium  
**Status:** Accepted

AI summary generation requires internet connection to access OpenAI API. Transcription works offline (local Whisper), but summaries will fall back to basic format.

**Workaround:** Process files when internet is available, or manually summarize from transcript.

---

### File-Based Only (No Real-Time)
**Impact:** 🔵 Low  
**Status:** Accepted

System processes pre-recorded audio files only. No support for real-time transcription during recording.

**Workaround:** Record to file first, then process.

---

## Issue Reporting

To report a new issue, add it to this file with the following template:

```markdown
### 🚧 Issue #{number}: {Title}
**Status:** {Open/In Progress/Resolved/Backlog}  
**Severity:** {🔴 Critical / 🟡 High / 🟢 Medium / 🔵 Low}  
**Date Reported:** YYYY-MM-DD

**Description:**  
{Detailed description of the issue}

**Impact:**  
- {Impact point 1}
- {Impact point 2}

**Root Cause:**  
{If known}

**Proposed Solution:**  
{Suggested fix or approach}

**Priority:** {High/Medium/Low}  
**Estimated Effort:** {hours or days}
```

---

## Resolved Issues Archive

For historical reference, see:
- [CHANGELOG.md](CHANGELOG.md) for version-specific fixes
- Git commit history for detailed change information
