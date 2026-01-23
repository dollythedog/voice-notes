#!/usr/bin/env python3
"""
Voice Note Transcription Service
Watches inbox folder and transcribes audio files to Logseq format.
"""

import os
import time
import whisper
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
INBOX_DIR = Path("/srv/voice_notes/inbox")
PROCESSED_DIR = Path("/srv/voice_notes/processed")
LOGSEQ_PAGES = Path("/srv/logseq_graph/pages")
LOGSEQ_JOURNALS = Path("/srv/logseq_graph/journals")
LOG_FILE = Path("/srv/voice_notes/logs/transcription.log")

# Supported audio formats
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.ogg', '.flac', '.opus'}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load Whisper model (cached after first load)
logger.info("Loading Whisper model...")
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
logger.info("Whisper model loaded successfully")


class VoiceNoteHandler(FileSystemEventHandler):
    """Handles new audio files in inbox."""
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's an audio file
        if file_path.suffix.lower() not in AUDIO_EXTENSIONS:
            logger.debug(f"Ignoring non-audio file: {file_path.name}")
            return
        
        # Wait for file to finish writing (especially for sync)
        time.sleep(2)
        
        # Verify file still exists and is not empty
        if not file_path.exists():
            logger.warning(f"File disappeared before processing: {file_path.name}")
            return
        
        if file_path.stat().st_size == 0:
            logger.warning(f"Empty file detected: {file_path.name}")
            return
        
        logger.info(f"New voice note detected: {file_path.name}")
        self.process_voice_note(file_path)
    
    def process_voice_note(self, audio_path: Path):
        """Transcribe and format voice note."""
        try:
            start_time = time.time()
            
            # Transcribe audio
            logger.info(f"Transcribing {audio_path.name}...")
            result = model.transcribe(str(audio_path), language="en")
            transcription = result["text"].strip()
            
            elapsed = time.time() - start_time
            logger.info(f"Transcription complete ({len(transcription)} chars, {elapsed:.1f}s)")
            
            # Generate Logseq markdown
            markdown = self.format_as_logseq(transcription, audio_path.name)
            
            # Save to Voice Inbox page
            self.append_to_voice_inbox(markdown)
            
            # Move processed file
            processed_path = PROCESSED_DIR / audio_path.name
            audio_path.rename(processed_path)
            
            logger.info(f"✓ Processed: {audio_path.name} → Voice Inbox")
            logger.info(f"Transcription: {transcription[:100]}...")
            
        except Exception as e:
            logger.error(f"Error processing {audio_path.name}: {e}", exc_info=True)
    
    def format_as_logseq(self, text: str, filename: str) -> str:
        """Format transcription as Logseq markdown."""
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M")
        
        # Simple heuristic: if text contains "TODO" or action words, format as task
        action_keywords = ['need to', 'have to', 'should', 'must', 'remember to', 'todo', 'remind me']
        is_action = any(keyword in text.lower() for keyword in action_keywords)
        
        if is_action:
            # Format as TODO - clean up the text
            task_text = text
            # Remove "TODO" or "todo" from the beginning
            for keyword in ['TODO', 'todo', 'Todo', 'Reminder to', 'Remember to', 'Need to', 'Have to']:
                if task_text.startswith(keyword):
                    task_text = task_text[len(keyword):].strip()
            
            markdown = f"""- TODO {task_text} #voice-note
  source:: Voice recording
  recorded:: [[{date_str}]] at {time_str}
  file:: {filename}
"""
        else:
            # Format as regular note
            markdown = f"""- 🎙️ Voice Note ({time_str})
  recorded:: [[{date_str}]]
  file:: {filename}
  - {text}
"""
        
        return markdown
    
    def append_to_voice_inbox(self, content: str):
        """Append to Voice Inbox page."""
        inbox_page = LOGSEQ_PAGES / "📥 Voice Inbox.md"
        
        # Create inbox page if it doesn't exist
        if not inbox_page.exists():
            header = """# 📥 Voice Inbox

type:: inbox
tags:: #voice-notes #inbox

---

## 🎙️ Recent Voice Notes

"""
            inbox_page.write_text(header, encoding='utf-8')
            logger.info("Created Voice Inbox page")
        
        # Append new content
        with open(inbox_page, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}\n")


def main():
    """Start the transcription service."""
    logger.info("=" * 60)
    logger.info("Voice Note Transcription Service Starting...")
    logger.info("=" * 60)
    
    # Ensure directories exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Inbox directory: {INBOX_DIR}")
    logger.info(f"Processed directory: {PROCESSED_DIR}")
    logger.info(f"Logseq pages: {LOGSEQ_PAGES}")
    logger.info(f"Log file: {LOG_FILE}")
    
    # Setup file watcher
    event_handler = VoiceNoteHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    
    logger.info(f"✓ Watching for voice notes in: {INBOX_DIR}")
    logger.info("✓ Service is running. Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Service stopped by user")
    
    observer.join()


if __name__ == "__main__":
    main()
