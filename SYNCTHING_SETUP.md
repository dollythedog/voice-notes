# Syncthing Setup for Voice Notes

## Overview
Configure Syncthing to automatically sync voice notes from your desktop to the server. Files dropped into type-specific folders on your desktop will be synced to the server inboxes and automatically processed.

## Server-Side Setup (Already Done)

Directory structure is ready:
- `/srv/voice_notes/inboxes/bjj/` - BJJ class recordings
- `/srv/voice_notes/inboxes/meeting/` - Meeting recordings
- `/srv/voice_notes/inboxes/personal/` - Personal notes

Output locations:
- `/srv/logseq_graph/pages/` - Processed summaries as Logseq pages
- `/srv/voice_notes/archive/{type}/done/` - Successfully processed files
- `/srv/voice_notes/archive/{type}/failed/` - Failed files with error logs

## Desktop-Side Setup

### Step 1: Create Desktop Folders
On your desktop computer, create the mirror folder structure:

```bash
# Example paths (adjust to your setup)
~/Desktop/voice_notes/
├── bjj/           # Drop BJJ recordings here
├── meeting/       # Drop meeting recordings here
└── personal/      # Drop personal notes here
```

### Step 2: Configure Syncthing

1. **Open Syncthing UI** (usually at `http://localhost:8384` on your desktop)

2. **Add New Folder:**
   - Click "Add Folder" button
   - Set Label: `Voice Notes - BJJ`
   - Set Folder Path: `~/Desktop/voice_notes/bjj`
   - Set Folder ID: `voice-notes-bjj`
   - Under Sharing, select your Bunto server device
   - Click Save

3. **Repeat for other types:**
   - Label: `Voice Notes - Meeting`, Path: `~/Desktop/voice_notes/meeting`, ID: `voice-notes-meeting`
   - Label: `Voice Notes - Personal`, Path: `~/Desktop/voice_notes/personal`, ID: `voice-notes-personal`

### Step 3: Configure Server-Side Folders

1. **On the server**, your Syncthing should receive sync requests
2. **Accept** the folder shares from your desktop
3. Set the server folder paths to:
   - `/srv/voice_notes/inboxes/bjj`
   - `/srv/voice_notes/inboxes/meeting`
   - `/srv/voice_notes/inboxes/personal`

4. Set Advanced > File Pull Order to "Alphabetic" (so oldest files process first)

## Workflow

1. **On Desktop:**
   - Record audio using any app (Voice Memos, Audacity, etc.)
   - Export as `.wav` or `.m4a` format
   - Drop into appropriate folder:
     - `~/Desktop/voice_notes/bjj/` for class recordings
     - `~/Desktop/voice_notes/meeting/` for meetings
     - etc.

2. **Syncthing:**
   - File is automatically synced to server inbox
   - Within seconds, visible in `/srv/voice_notes/inboxes/{type}/`

3. **Service:**
   - Transcription service detects new file
   - Whisper transcribes audio
   - OpenAI generates type-specific summary
   - Summary saved to Logseq
   - Original file moved to `archive/{type}/done/`

4. **Result:**
   - Summary appears in `/srv/logseq_graph/pages/` as a new Logseq page
   - Entry added to today's Logseq journal with tags like `#bjj #inbox`
   - Original audio archived at `archive/{type}/done/{filename}`

## Naming Conventions

### BJJ Recordings
```
BJJ Class - Mount Escape Fundamentals.wav
BJJ - Professor John - 2025-01-22.wav
Gi Class - Side Control Escape.wav
```

### Meeting Recordings
```
Team Sync - 2025-01-22.wav
Client Kickoff - ProjectName.wav
One-on-One - John Doe.wav
```

### Personal Notes
```
Idea - New Feature Concept.wav
Reflection - 2025-01-22.wav
Learning Note - REST API Design.wav
```

## Troubleshooting

### Files Not Syncing
- Check Syncthing UI on desktop: confirm folders are connected
- Check Syncthing UI on server: confirm folders are synced
- Look at sync progress bars in Syncthing UI

### Files Not Processing
- Check service status: `./service_control.sh status`
- View logs: `./service_control.sh logs`
- Verify file moved to `archive/{type}/done/` or `archive/{type}/failed/`

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set on server
- Check API key is valid and has available credits
- View error in: `/srv/voice_notes/logs/transcription.log`

### Domain Dictionary Not Correcting Terms
- Terms in domain dictionary must match (case-insensitive)
- Add missing terms to `/srv/voice_notes/configs/types/bjj.json` under `domains`
- Restart service: `./service_control.sh restart`

## Adding New Note Types

To add a new note type (e.g., "lecture"):

1. Create folder: `mkdir -p /srv/voice_notes/inboxes/lecture`
2. Create config: Copy `meeting.json` to `configs/types/lecture.json`
3. Edit config to customize prompts and domains
4. Restart service: `./service_control.sh restart`
5. Create desktop folder: `~/Desktop/voice_notes/lecture/`
6. Configure Syncthing folder pair

## Service Management

```bash
cd /srv/voice_notes

# Control service
./service_control.sh start
./service_control.sh stop
./service_control.sh restart
./service_control.sh status

# View logs
./service_control.sh logs           # Follow live
./service_control.sh logs-recent    # Last 50 lines

# Test with file
./service_control.sh test path/to/audio.wav
```

## Performance Notes

- **Whisper small model**: ~30-60s per minute of audio
- **OpenAI API**: ~5-10s per call (depends on transcript length)
- Total processing time for 10-minute recording: ~2-3 minutes

If processing is slow, Whisper model can be downgraded to "base" in transcribe_service_v3.py (line 47) but will be less accurate for technical content.

---

**Questions?** Check logs at `/srv/voice_notes/logs/transcription.log` for detailed error messages.
