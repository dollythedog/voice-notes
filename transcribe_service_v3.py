#!/usr/bin/env python3
"""
Multi-Type Voice Notes Transcription Service v3
- Supports multiple note types (bjj, meeting, personal, etc.)
- Watches separate inboxes per type
- Routes to type-specific summarizer
- Moves files to done/failed archive
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

import whisper
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
import type_manager


# Configuration
BASE_DIR = Path("/srv/voice_notes")
INBOXES_DIR = BASE_DIR / "inboxes"
ARCHIVE_DIR = BASE_DIR / "archive"
LOGSEQ_PAGES = Path("/srv/logseq_graph/pages")
LOGSEQ_JOURNALS = Path("/srv/logseq_graph/journals")
LOG_DIR = BASE_DIR / "logs"

AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".opus"}

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


class MultiTypeAudioHandler(FileSystemEventHandler):
    """Handle audio files with type-specific processing."""
    
    def __init__(self):
        logger.info("🔄 Loading Whisper model (small)...")
        self.whisper_model = whisper.load_model("small")
        logger.info("✓ Whisper model loaded")
        self.note_type = None
    
    def on_created(self, event):
        """Process new audio file."""
        if event.is_directory:
            return
        
        audio_path = Path(event.src_path)
        
        # Check file extension
        if audio_path.suffix.lower() not in AUDIO_EXTENSIONS:
            return
        
        # Extract note type from parent directory
        inbox_parent = audio_path.parent.parent.name  # inboxes
        note_type = audio_path.parent.name  # bjj, meeting, etc.
        
        logger.info(f"📥 New {note_type} audio: {audio_path.name}")
        
        try:
            # Wait for file write completion
            time.sleep(2)
            
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                logger.warning(f"⚠️  File not ready: {audio_path.name}")
                return
            
            # Load type config
            try:
                config = type_manager.load_config(note_type)
            except FileNotFoundError:
                logger.error(f"Unknown note type: {note_type}")
                self._move_to_failed(audio_path, note_type, "Unknown note type")
                return
            
            # Stage 1: Transcribe with Whisper
            logger.info(f"🎤 Transcribing...")
            result = self.whisper_model.transcribe(str(audio_path), language="en")
            transcript = result["text"].strip()
            logger.info(f"✓ Transcript: {len(transcript)} chars")
            
            # Stage 2: Generate type-specific summary
            logger.info(f"🤖 Generating {note_type} summary...")
            summary = self._generate_summary(transcript, note_type, config, audio_path.name)
            
            # Stage 3: Save to Logseq
            page_name = self._create_page_name(audio_path.name)
            self._save_to_logseq(summary, page_name)
            
            # Stage 4: Add entry to daily journal
            self._add_to_journal(page_name, note_type)
            
            # Stage 5: Move to done
            self._move_to_done(audio_path, note_type)
            logger.info(f"✅ Complete: {audio_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {audio_path.name}: {e}", exc_info=True)
            self._move_to_failed(audio_path, note_type, str(e))
    
    def _generate_summary(self, transcript: str, note_type: str, config: dict, filename: str) -> str:
        """Call local summarizer via subprocess."""
        try:
            result = subprocess.run(
                ["python3", str(BASE_DIR / "summarizer_local.py"), note_type, filename],
                input=transcript,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"Summarizer error: {result.stderr}")
                return self._format_fallback(transcript, filename)
            
            return result.stdout
        except Exception as e:
            logger.error(f"Summarizer exception: {e}")
            return self._format_fallback(transcript, filename)
    
    def _format_fallback(self, transcript: str, filename: str) -> str:
        """Fallback format if summarization fails."""
        date = datetime.now().strftime("%Y-%m-%d")
        return f"""## Summary

Unable to generate AI summary. See raw transcript below.

---

## Raw Transcript

{transcript}"""
    
    def _create_page_name(self, filename: str) -> str:
        """Create Logseq page name from audio filename."""
        import re
        name = Path(filename).stem
        name = re.sub(r'^(Voice|Recording|Audio)\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[\s_]+', '-', name)
        name = re.sub(r'[^\w\-#]', '', name)
        date = datetime.now().strftime("%Y-%m-%d")
        return f"{date}-{name}"
    
    def _save_to_logseq(self, content: str, page_name: str):
        """Save as individual Logseq page."""
        LOGSEQ_PAGES.mkdir(parents=True, exist_ok=True)
        page_file = LOGSEQ_PAGES / f"{page_name}.md"
        page_file.write_text(content, encoding='utf-8')
        logger.info(f"✓ Created page: {page_name}.md")
    
    def _add_to_journal(self, page_name: str, note_type: str):
        """Add link to today's journal."""
        LOGSEQ_JOURNALS.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y_%m_%d")
        journal_file = LOGSEQ_JOURNALS / f"{today}.md"
        
        if not journal_file.exists():
            journal_file.write_text("", encoding='utf-8')
        
        entry = f"\n- 🎙️ [[{page_name}]] #{note_type} #inbox\n"
        with open(journal_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        logger.info(f"✓ Added to journal: {today}.md")
    
    def _move_to_done(self, audio_path: Path, note_type: str):
        """Move processed file to archive/done."""
        done_dir = ARCHIVE_DIR / note_type / "done"
        done_dir.mkdir(parents=True, exist_ok=True)
        dest = done_dir / audio_path.name
        audio_path.rename(dest)
        logger.info(f"✓ Moved to done: archive/{note_type}/done/{audio_path.name}")
    
    def _move_to_failed(self, audio_path: Path, note_type: str, error: str):
        """Move failed file to archive/failed with error log."""
        failed_dir = ARCHIVE_DIR / note_type / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)
        
        dest = failed_dir / audio_path.name
        if audio_path.exists():
            audio_path.rename(dest)
        
        # Write error log
        error_log = failed_dir / f"{audio_path.stem}_error.txt"
        with open(error_log, 'w') as f:
            f.write(f"Error processing {audio_path.name}:\n{error}\n")
        
        logger.info(f"✓ Moved to failed: archive/{note_type}/failed/{audio_path.name}")


def main():
    """Run the multi-type transcription service."""
    INBOXES_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("🎙️  Voice Notes Service v3 (Multi-Type)")
    logger.info("=" * 60)
    logger.info(f"Watching: {INBOXES_DIR}")
    logger.info(f"Pages: {LOGSEQ_PAGES}")
    logger.info(f"Archive: {ARCHIVE_DIR}")
    logger.info(f"Available types: {type_manager.list_available_types()}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    event_handler = MultiTypeAudioHandler()
    observer = Observer()
    
    # Watch all type inboxes
    for type_dir in INBOXES_DIR.iterdir():
        if type_dir.is_dir():
            logger.info(f"Watching inbox: {type_dir.name}")
            observer.schedule(event_handler, str(type_dir), recursive=False)
    
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
