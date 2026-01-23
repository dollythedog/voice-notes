# Android Voice Notes Setup Guide

## Overview
Two methods to get voice recordings from your Android phone to bunto-server automatically.

---

## Method 1: Syncthing (Recommended)

### Why Syncthing?
- ✅ Already in your infrastructure plan
- ✅ Works on LAN and remotely (via Tailscale)
- ✅ Automatic, continuous sync
- ✅ Open source, secure, no cloud
- ✅ Syncs Logseq graph too

### Step 1: Install Syncthing on bunto-server

```bash
# Install Syncthing
sudo apt update
sudo apt install -y syncthing

# Enable and start Syncthing service for your user
sudo systemctl enable syncthing@ivesjl.service
sudo systemctl start syncthing@ivesjl.service

# Check it's running
systemctl status syncthing@ivesjl.service
```

### Step 2: Configure Syncthing on Server

```bash
# Access Syncthing web UI
# From browser: http://10.69.1.86:8384
# (Should auto-open on first start)

# Get your Syncthing Device ID
syncthing -device-id
```

**In Syncthing Web UI (http://10.69.1.86:8384):**
1. Go to Actions → Settings
2. Note your "Device ID" (long string like: ABC123-XYZ789-...)
3. Under "GUI" section:
   - Set GUI Authentication (username/password)
   - Allow connections from LAN (10.69.1.0/24)

### Step 3: Add Voice Notes Folder

**In Syncthing Web UI:**
1. Click "Add Folder"
2. Settings:
   - **Folder Label:** VoiceNotes
   - **Folder ID:** voicenotes (auto-generated)
   - **Folder Path:** `/srv/voice_notes/inbox`
   - **Folder Type:** Receive Only (server receives, doesn't send back)
3. Save

### Step 4: Install Syncthing on Android

**On your Android phone:**
1. Open Google Play Store
2. Search for **"Syncthing"** (by Syncthing community)
3. Install the app
4. Open Syncthing app

### Step 5: Connect Phone to Server

**On Android Syncthing app:**
1. Tap the **+** button (top right)
2. Select "Add Device"
3. Scan QR Code from server web UI:
   - On server: http://10.69.1.86:8384 → Actions → Show ID → QR Code
   - Or manually enter Device ID
4. Give it a name: "bunto-server"
5. Tap ✓ to save

**On server web UI (http://10.69.1.86:8384):**
- You'll see a notification "New device wants to connect"
- Click "Add Device"
- Confirm and save

### Step 6: Share Voice Notes Folder to Phone

**On Android Syncthing app:**
1. Tap the **+** button → "Add Folder"
2. Settings:
   - **Folder Label:** VoiceNotes
   - **Folder ID:** voicenotes (match server)
   - **Folder Path:** `/storage/emulated/0/VoiceNotes/`
   - **Folder Type:** Send Only (phone sends, doesn't receive)
3. Under "Devices" section:
   - Enable "bunto-server"
4. Save

**On server web UI:**
- Accept the folder share request
- Verify folder path is `/srv/voice_notes/inbox`
- Set as "Receive Only"
- Save

### Step 7: Test Sync

**On Android:**
1. Open file manager
2. Navigate to `/VoiceNotes/` folder
3. Copy a file there (any file to test)
4. In Syncthing app, watch it sync

**On server:**
```bash
# Watch inbox directory
watch -n 1 ls -lh /srv/voice_notes/inbox/

# Should see file appear within seconds
```

### Step 8: Configure Voice Recorder

**Option A: Built-in Recorder**
1. Open your phone's Voice Recorder app
2. Settings → Storage Location → Change to `/VoiceNotes/`
3. Record a test note
4. It should auto-sync!

**Option B: Install a Better Recorder**
Recommended: **Voice Recorder by Sony** or **Easy Voice Recorder**
1. Install from Play Store
2. Settings:
   - Save Location: `/VoiceNotes/`
   - Format: M4A or MP3 (smaller files)
   - Quality: Medium (good balance)

### Step 9: Test End-to-End

1. **Record voice note on phone:**
   - "TODO Test the voice transcription system"
2. **Watch Syncthing sync** (should be 5-30 seconds)
3. **Watch transcription happen:**
   ```bash
   sudo journalctl -u voice-transcription.service -f
   ```
4. **Check Voice Inbox in Logseq:**
   ```bash
   cat /srv/logseq_graph/pages/📥\ Voice\ Inbox.md
   ```

---

## Method 2: Simple SSH/SCP Upload (Alternative)

If you want something simpler for now:

### Android App: Termux (Terminal + SSH)

1. Install **Termux** from F-Droid or Play Store
2. In Termux:
   ```bash
   pkg install openssh
   ```
3. Create upload script:
   ```bash
   cat > upload_voice.sh << 'SCRIPT'
   #!/bin/bash
   # Upload voice note to server
   FILE="$1"
   scp "$FILE" ivesjl@10.69.1.86:/srv/voice_notes/inbox/
   SCRIPT
   
   chmod +x upload_voice.sh
   ```
4. Use it:
   ```bash
   ./upload_voice.sh /path/to/voice_note.m4a
   ```

**Pros:** Simple, no extra services  
**Cons:** Manual upload, requires terminal access

---

## Method 3: Tailscale + Syncthing (Remote Access)

For recording voice notes when away from home:

1. Install **Tailscale** on Android (Play Store)
2. Connect to your Tailscale network
3. Follow Syncthing steps above
4. Use Tailscale IP instead of LAN IP
5. Works anywhere with internet!

---

## Recommended Voice Recording Apps for Android

### 1. **Voice Recorder by Sony** (Free)
- Simple, clean interface
- Good quality
- Custom save location
- No ads

### 2. **Easy Voice Recorder** (Free)
- High quality recording
- Many formats (M4A, MP3, WAV)
- Cloud sync support
- Folder organization

### 3. **RecForge II** (Free/Pro)
- Professional features
- Multiple formats
- Noise reduction
- Bookmark important parts

### 4. **Voice Recorder & Audio Editor** (Free)
- Record and edit
- Trim, cut, merge
- Good quality
- Easy sharing

---

## Troubleshooting

### Syncthing not syncing
```bash
# On server - check Syncthing status
systemctl status syncthing@ivesjl.service

# Check Syncthing logs
journalctl -u syncthing@ivesjl.service -f

# On Android - check Syncthing app
# Settings → Run Conditions
# Make sure WiFi is enabled
```

### File not transcribing
```bash
# Check if file arrived
ls -lh /srv/voice_notes/inbox/

# Check transcription service
sudo systemctl status voice-transcription.service

# Watch logs
sudo journalctl -u voice-transcription.service -f

# Check file format is supported
file /srv/voice_notes/inbox/your_file.m4a
```

### Poor transcription quality
- Speak clearly and slowly
- Reduce background noise
- Hold phone closer to mouth
- Try different recorder app with higher quality
- Consider using better quality format (WAV instead of MP3)

---

## Quick Reference Card

### Record Voice Note:
1. Open Voice Recorder on Android
2. Press Record
3. Say: "TODO [your task]" or just speak naturally
4. Stop recording
5. File auto-saves to VoiceNotes folder

### Syncthing auto-syncs (5-30 seconds)
### Transcription happens automatically (~15-60 seconds)
### Check result in Logseq Voice Inbox!

---

## Network Diagram

```
┌─────────────────┐
│  Android Phone  │
│                 │
│  Voice Recorder │
│       ↓         │
│  /VoiceNotes/   │
└────────┬────────┘
         │ Syncthing
         │ (LAN or Tailscale)
         ↓
┌─────────────────────────────┐
│    bunto-server             │
│    10.69.1.86               │
│                             │
│  /srv/voice_notes/inbox/    │
│         ↓                   │
│  Whisper Transcription      │
│         ↓                   │
│  /srv/logseq_graph/pages/   │
│  📥 Voice Inbox.md          │
└─────────────────────────────┘
         ↓
    Syncthing
         ↓
┌─────────────────┐
│  Desktop PC     │
│                 │
│  Logseq App     │
│  sees note!     │
└─────────────────┘
```

---

## Security Notes

- Syncthing uses TLS encryption
- Only connects to devices you explicitly add
- LAN-only or Tailscale for remote
- No cloud services involved
- All data stays on your devices

---

## Next Steps After Setup

1. Record 5+ test voice notes
2. Verify transcription accuracy
3. Adjust recording quality if needed
4. Create Logseq queries for voice notes
5. Integrate into daily workflow

---

**Created:** 2025-12-09  
**For:** Android → bunto-server voice note sync
