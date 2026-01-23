# Cronicle Setup for Voice Notes Monitoring

## Overview

Cronicle continuously monitors your voice notes archive and sends ntfy alerts when files are processed or fail. This follows your existing paperless workflow pattern.

## Architecture

```
transcribe_service_v3.py (continuously running)
    ↓ [processes files]
/srv/voice_notes/archive/{type}/{done,failed}/
    ↓ [Cronicle monitors]
voice_notes_monitor.sh (runs every 5 minutes)
    ↓ [detects new files]
ntfy alert → your phone/desktop
    ↓
Logseq updates in real-time
```

## Setup Instructions

### Step 1: Verify Script Exists

```bash
ls -lh /srv/cronicle/scripts/voice_notes_monitor.sh
# Should show: -rwxrwxr-x ... voice_notes_monitor.sh
```

### Step 2: Test Script Locally

```bash
/srv/cronicle/scripts/voice_notes_monitor.sh
# Check logs: cat /var/log/voice_notes_monitor.log
```

### Step 3: Create Cronicle Job

1. **Open Cronicle UI:** http://10.69.1.86:3012
2. **Click "Schedule a new event"** (or equivalent)
3. **Fill in details:**
   - **Event Title:** `Voice Notes Monitor`
   - **Event Description:** `Monitor voice notes archive and send ntfy alerts`
   - **Category:** `Automation` or similar
   - **Enabled:** ✓ (checked)

4. **Timing:**
   - **Run Every:** `5 minutes`
   - Or set specific times if preferred

5. **Action:**
   - **Command:** `/srv/cronicle/scripts/voice_notes_monitor.sh`
   - **Timeout:** `60 seconds`
   - **Run as User:** `ivesjl`

6. **Notifications (Cronicle):**
   - **On success:** Unchecked (we handle alerts in script)
   - **On failure:** Checked (alert if script errors)

7. **Click "Save Event"**

### Step 4: Verify Job is Running

```bash
# Check Cronicle UI for recent executions
# Should show successful runs every 5 minutes
```

## How It Works

### Success Alert
When a file successfully processes:
```
Title: 🎙️ bjj Note Processed
Priority: low
Tags: voice-note, bjj

Message:
File: half-butterfly.wav

Successfully transcribed and summarized.

Check your Logseq inbox for details.
```

### Failure Alert
When a file fails to process:
```
Title: ⚠️ bjj Note Failed
Priority: high
Tags: warning, voice-note, bjj

Message:
File: half-butterfly.wav

Processing failed.

Error: [error details from error log]

Check logs for details.
```

## ntfy Configuration

The script sends to `https://ntfy.sh/bunto-alerts` topic.

To **receive notifications on your phone:**
1. **Download ntfy app** (iOS/Android)
2. **Subscribe to topic:** `bunto-alerts`
3. **Notifications appear in real-time**

Or **browse online:** https://ntfy.sh/bunto-alerts

## State Tracking

The script tracks which files have been notified (in `/tmp/voice_notes_monitor/`):
- `bjj_processed.txt` - Notified success files
- `bjj_failed.txt` - Notified failed files
- Similarly for `meeting` and `personal`

This prevents duplicate notifications for the same file.

## Logs

Monitor job logs:
```bash
# Cronicle execution log
tail -f /var/log/voice_notes_monitor.log

# Or check Cronicle UI for job history
```

## Customization

### Change Notification Topic
Edit `/srv/cronicle/scripts/voice_notes_monitor.sh`, line 9:
```bash
NTFY_TOPIC="bunto-alerts"  # Change to your topic
```

### Add Daily Summary

To add a daily summary notification:
1. Create a separate Cronicle job
2. Run once per day (e.g., 9 PM)
3. Script: Count files in `archive/*/done/` from today, send summary alert

### Add Slack Integration

Replace curl calls with:
```bash
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Message here"}' \
    $SLACK_WEBHOOK_URL
```

## Troubleshooting

### Alerts Not Sending
1. **Check ntfy connectivity:** `curl -d "test" https://ntfy.sh/bunto-alerts`
2. **Verify topic name:** Should match your subscription
3. **Check script logs:** `cat /var/log/voice_notes_monitor.log`

### Job Not Running
1. **Verify Cronicle job is enabled** in UI
2. **Check Cronicle status:** Is it running?
3. **Manual test:** `/srv/cronicle/scripts/voice_notes_monitor.sh`

### Duplicate Alerts
1. **Check state files:** `ls /tmp/voice_notes_monitor/`
2. **Clear state if needed:** `rm /tmp/voice_notes_monitor/*.txt`
3. **Restart job**

## Integration with Logseq

Voice notes appear in your daily journal query:
```
{{query (and [[voice-note]] (property processed false))}}
```

When you see the **ntfy alert**, check your Logseq inbox to find the new note. Mark it `processed:: true` to remove from inbox.

**Timeline:**
1. File drops in Syncthing inbox → ~30 seconds to server
2. Service transcribes → 30-60 minutes (depends on audio length)
3. Service summarizes → 10 seconds
4. **Cronicle detects completion** → sends ntfy alert
5. You check Logseq inbox, see new note
6. You process it and mark `processed:: true`

---

**Status:** ✅ Ready to deploy

Once you create the Cronicle job, the monitoring will be fully automated!
