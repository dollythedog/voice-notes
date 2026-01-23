#!/usr/bin/env python3
"""
Enhanced voice notes transcription service with AI summarization.
Creates individual Logseq pages for each voice note.
"""

import os
import sys
import time
import logging
import subprocess
import re
from pathlib import Path
from datetime import datetime

import whisper
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Configuration
INBOX_DIR = Path("/srv/voice_notes/inbox")
PROCESSED_DIR = Path("/srv/voice_notes/processed")
LOGSEQ_PAGES = Path("/srv/logseq_graph/pages")
LOGSEQ_JOURNALS = Path("/srv/logseq_graph/journals")
LOG_DIR = Path("/srv/voice_notes/logs")
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".opus"}
PROJECT_WIZARD_VENV = "/srv/project_wizard/venv/bin/python3"
SUMMARIZER_SCRIPT = "/srv/voice_notes/summarizer_v3.py"

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "transcription.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AudioFileHandler(FileSystemEventHandler):
    """Handle new audio files with transcription + AI summary."""
    
    def __init__(self):
        logger.info("🔄 Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        logger.info("✓ Whisper model loaded")
    
    def on_created(self, event):
        """Process new audio file."""
        if event.is_directory:
            return
        
        audio_path = Path(event.src_path)
        
        if audio_path.suffix.lower() not in AUDIO_EXTENSIONS:
            return
        
        logger.info(f"📥 New audio: {audio_path.name}")
        
        try:
            # Wait for file write completion
            time.sleep(2)
            
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                logger.warning(f"⚠️  File not ready: {audio_path.name}")
                return
            
            # Stage 1: Transcribe with Whisper
            logger.info(f"🎤 Transcribing...")
            result = self.whisper_model.transcribe(str(audio_path), language="en")
            transcript = result["text"].strip()
            logger.info(f"✓ Transcript: {len(transcript)} chars")
            
            # Stage 2: Generate AI summary
            logger.info(f"🤖 Generating AI summary...")
            summary = self._generate_summary(transcript, audio_path.name)
            
            # Stage 3: Save as Logseq page
            page_name = self._create_page_name(audio_path.name)
            self._save_to_logseq(summary, page_name)
            
            # Stage 4: Add entry to daily journal
            self._add_to_journal(page_name)
            
            # Move to processed
            dest = PROCESSED_DIR / audio_path.name
            audio_path.rename(dest)
            logger.info(f"✅ Complete: {audio_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
    
    def _create_page_name(self, filename: str) -> str:
        """Create Logseq page name from audio filename."""
        # Remove extension
        name = Path(filename).stem
        
        # Remove common prefixes
        name = re.sub(r'^(Voice|Recording|Audio)\s*', '', name, flags=re.IGNORECASE)
        
        # Clean up
        name = re.sub(r'[\s_]+', '-', name)
        name = re.sub(r'[^\w\-#]', '', name)
        
        # Add date prefix
        date = datetime.now().strftime("%Y-%m-%d")
        return f"{date}-{name}"
    
    def _generate_summary(self, transcript: str, filename: str) -> str:
        """Call project_wizard summarizer."""
        result = subprocess.run(
            [PROJECT_WIZARD_VENV, SUMMARIZER_SCRIPT],
            input=f"{transcript}\n---FILENAME---\n{filename}",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            logger.error(f"Summarizer error: {result.stderr}")
            return self._format_fallback(transcript, filename)
        
        return result.stdout
    
    def _format_fallback(self, transcript: str, filename: str) -> str:
        """Fallback format if AI summarization fails."""
        date = datetime.now().strftime("%Y-%m-%d")
        return f"""# 🎙️ {Path(filename).stem}

tags:: #voice-note #inbox
recorded:: [[{date}]]
processed:: false

---

## Transcript

{transcript}
"""
    
    def _save_to_logseq(self, content: str, page_name: str):
        """Save as individual Logseq page."""
        LOGSEQ_PAGES.mkdir(parents=True, exist_ok=True)
        
        page_file = LOGSEQ_PAGES / f"{page_name}.md"
        page_file.write_text(content, encoding='utf-8')
        
        logger.info(f"✓ Created page: {page_name}.md")
    
    def _add_to_journal(self, page_name: str):
        """Add link to today's journal."""
        LOGSEQ_JOURNALS.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime("%Y_%m_%d")
        journal_file = LOGSEQ_JOURNALS / f"{today}.md"
        
        # Create journal if doesn't exist
        if not journal_file.exists():
            journal_file.write_text("", encoding='utf-8')
        
        # Append voice note link
        entry = f"\n- 🎙️ [[{page_name}]] #voice-note #inbox\n"
        with open(journal_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        logger.info(f"✓ Added to journal: {today}.md")


def main():
    """Run the transcription service."""
    INBOX_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("🎙️  Voice Notes Service (Whisper + AI → Logseq)")
    logger.info("=" * 60)
    logger.info(f"Watching: {INBOX_DIR}")
    logger.info(f"Pages: {LOGSEQ_PAGES}")
    logger.info(f"Journals: {LOGSEQ_JOURNALS}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    event_handler = AudioFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping...")
        observer.stop()
    
    observer.join()
    logger.info("✓ Stopped")


if __name__ == "__main__":
    main()
