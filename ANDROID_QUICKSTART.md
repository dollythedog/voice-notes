# 📱 Android Voice Notes - Quick Start Guide

## Simplest Method: Manual Syncthing Setup

Since the systemd service had an issue, here's the manual approach that always works:

### Step 1: Start Syncthing on Server (Manual)

```bash
# Run this command to start Syncthing
syncthing

# OR run in background
nohup syncthing > /tmp/syncthing.log 2>&1 &
```

This will:
- Start Syncthing web UI on http://10.69.1.86:8384
- Create config in `~/.config/syncthing/`
- Show you the Device ID

### Step 2: Configure Firewall (if needed)

```bash
# Allow Syncthing ports
sudo ufw allow 8384/tcp   # Web UI
sudo ufw allow 22000/tcp  # Sync protocol
sudo ufw allow 21027/udp  # Discovery
```

### Step 3: Access Web UI

Open browser: **http://10.69.1.86:8384**

You'll see the Syncthing dashboard!

### Step 4: Get Device ID

In Syncthing Web UI:
- Click **Actions** → **Show ID**
- You'll see a QR code and Device ID string
- Keep this open for phone setup

### Step 5: Add Voice Notes Folder

In Syncthing Web UI:
1. Click **"Add Folder"** button
2. Fill in:
   - **Folder Label:** Voice Notes
   - **Folder Path:** `/srv/voice_notes/inbox`
   - **Folder ID:** (auto-generated, like "abc12-xyz34")
3. Click **Save**

### Step 6: Install Syncthing on Android

1. Open **Google Play Store**
2. Search: **"Syncthing"**
3. Install **Syncthing** by Syncthing community
4. Open the app
5. Grant storage permissions

### Step 7: Connect Phone to Server

**On Android Syncthing app:**

1. Tap **+** button (bottom right or top right)
2. Tap **"Add Device"**
3. Tap **"Scan QR Code"**
4. Scan the QR code from server web UI (Step 4)
   - OR manually type the Device ID
5. Give it a name: **"bunto-server"**
6. Tap **✓** to save

**Back on Server Web UI:**
- You'll see notification: **"Device ... wants to connect"**
- Click **"Add Device"**
- Name it: **"Android Phone"**
- Click **Save**

### Step 8: Create Folder on Phone

**On Android:**

1. Open **Files** app (or any file manager)
2. Navigate to main storage
3. Create new folder: **"VoiceNotes"**
   - Full path will be: `/storage/emulated/0/VoiceNotes/`

### Step 9: Share Folder from Phone

**In Android Syncthing app:**

1. Tap **+** → **"Add Folder"**
2. Tap **folder icon** to browse
3. Select the **VoiceNotes** folder you created
4. Settings:
   - **Folder Label:** Voice Notes
   - **Folder Type:** **Send Only**
5. Scroll down to **"Sharing"** section
6. Enable **"bunto-server"**
7. Tap **✓** to save

**On Server Web UI:**
- New notification: **"Device ... wants to share folder"**
- Click **"Add"**
- Make sure path is `/srv/voice_notes/inbox`
- **Folder Type:** **Receive Only**
- Click **Save**

### Step 10: Install Voice Recorder

**Recommended Apps:**

**Option 1: Easy Voice Recorder** (Easiest)
1. Install from Play Store
2. Open app
3. Settings → **Save Location** → Browse to `/VoiceNotes/`
4. Settings → **Audio Format** → **M4A** or **MP3**
5. Settings → **Audio Quality** → **High** or **Medium**

**Option 2: Simple Voice Recorder** (Open Source)
1. Install from F-Droid or Play Store
2. Settings → **Save recordings to** → Custom folder
3. Browse and select `/VoiceNotes/`

**Option 3: Use Built-in Recorder**
- Most Android phones have a built-in voice recorder
- Check if you can set save location to custom folder

### Step 11: Test Everything!

1. **Record a test voice note:**
   - Open Voice Recorder on phone
   - Press Record
   - Say: **"TODO Test the voice transcription system on Android"**
   - Stop and save

2. **Watch Syncthing sync:**
   - Open Syncthing app on Android
   - Watch the "Voice Notes" folder
   - Should show "Syncing" then "Up to Date"

3. **Check server received it:**
   ```bash
   ls -lh /srv/voice_notes/inbox/
   ```

4. **Watch transcription:**
   ```bash
   sudo journalctl -u voice-transcription.service -f
   ```

5. **Check result:**
   ```bash
   cat /srv/logseq_graph/pages/📥\ Voice\ Inbox.md
   ```

---

## Workflow After Setup

### Daily Use:
1. Pull out phone
2. Open Voice Recorder
3. Record your thought
4. Save (auto-saves to VoiceNotes folder)
5. Syncthing syncs in background (5-30 seconds)
6. Transcription happens automatically (~15-60 seconds)
7. Open Logseq → See transcribed note in Voice Inbox!

### Pro Tips:
- Say "TODO" at start for automatic task creation
- Keep recordings under 2 minutes for faster transcription
- Use when you have an idea but hands are busy
- Great for capturing meeting notes on the go

---

## Troubleshooting

### Syncthing not syncing?

**On Phone:**
- Open Syncthing app
- Check it says "Active" not "Disabled"
- Settings → Run Conditions:
  - Enable "Run on WiFi"
  - Optionally enable "Run on Mobile Data"
- Make sure you're on same network as server

**On Server:**
- Check Syncthing is running:
  ```bash
  ps aux | grep syncthing
  ```
- If not, start it:
  ```bash
  syncthing &
  ```

### File not appearing in inbox?

```bash
# Check Syncthing folder status
ls -lh /srv/voice_notes/inbox/

# If empty, check Syncthing logs
cat ~/.config/syncthing/syncthing.log | tail -50
```

### Transcription not working?

```bash
# Check service is running
sudo systemctl status voice-transcription.service

# If not running
sudo systemctl start voice-transcription.service

# Watch logs
sudo journalctl -u voice-transcription.service -f
```

---

## Alternative: Quick Test Without Syncthing

Want to test transcription right now without setting up Syncthing?

### Using SCP from Computer:

```bash
# From your desktop/laptop with an audio file
scp your_voice_note.m4a ivesjl@10.69.1.86:/srv/voice_notes/inbox/

# Watch it get transcribed
ssh ivesjl@10.69.1.86 "sudo journalctl -u voice-transcription.service -f"
```

### Using Android SSH App:

1. Install **Termux** from Play Store
2. In Termux:
   ```bash
   pkg install openssh
   scp /path/to/recording.m4a ivesjl@10.69.1.86:/srv/voice_notes/inbox/
   ```

---

## Keep Syncthing Running

To make Syncthing start automatically:

### Option 1: Add to crontab
```bash
crontab -e

# Add this line:
@reboot sleep 30 && /usr/bin/syncthing serve --no-browser
```

### Option 2: Create simple systemd user service
```bash
mkdir -p ~/.config/systemd/user/

cat > ~/.config/systemd/user/syncthing.service << 'SERVICE'
[Unit]
Description=Syncthing
After=network.target

[Service]
ExecStart=/usr/bin/syncthing serve --no-browser
Restart=always

[Install]
WantedBy=default.target
SERVICE

systemctl --user enable syncthing.service
systemctl --user start syncthing.service
```

---

## Summary Checklist

- [ ] Syncthing installed on server
- [ ] Syncthing started (manual or service)
- [ ] Web UI accessible at http://10.69.1.86:8384
- [ ] Syncthing installed on Android
- [ ] Devices paired (phone ↔ server)
- [ ] VoiceNotes folder created on phone
- [ ] Folder shared and syncing
- [ ] Voice Recorder app installed
- [ ] Recorder saves to VoiceNotes folder
- [ ] Test recording made
- [ ] File synced to server
- [ ] Transcription appeared in Logseq

---

**Total Setup Time:** 15-20 minutes
**Daily Use Time:** 5 seconds (just record!)

---

Need help? Check:
- `/srv/voice_notes/README.md` - Full documentation
- `/srv/voice_notes/MOBILE_SETUP_GUIDE.md` - Detailed guide
- Syncthing Forum: https://forum.syncthing.net/
