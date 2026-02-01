#!/usr/bin/env python3
"""
Voice Notes Transcription Service v3 - Multi-Type Support
Watches multiple inbox folders, transcribes audio, generates summaries.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Add voice_notes to path
sys.path.insert(0, str(Path(__file__).parent))

import type_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(__file__).parent.absolute()

# Load environment variables
load_dotenv(BASE_DIR / ".env")
INBOX_DIR = BASE_DIR / "inboxes"
ARCHIVE_DIR = BASE_DIR / "archive"
LOGSEQ_PAGES = Path("/srv/logseq_graph/pages")
LOGSEQ_JOURNALS = Path("/srv/logseq_graph/journals")
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".WAV", ".MP3", ".M4A"}

# Load whisper model once at startup
logger.info("🔄 Loading Whisper model (small)...")
import whisper
WHISPER_MODEL = whisper.load_model("small")
logger.info("✓ Whisper model loaded")


class VoiceNoteHandler(FileSystemEventHandler):
    """Handles new audio files in type-specific inboxes."""
    
    def __init__(self, note_type: str, config: dict):
        self.note_type = note_type
        self.config = config
        self.processing = set()  # Track files being processed
        self.processed_files = set()  # Track completed files
    
    def on_created(self, event):
        """Process new audio file."""
        if event.is_directory:
            return
        self._handle_audio_event(Path(event.src_path))
    
    def on_modified(self, event):
        """Process modified audio file (e.g., from Syncthing)."""
        if event.is_directory:
            return
        self._handle_audio_event(Path(event.src_path))
    
    def on_moved(self, event):
        """Process moved audio file (e.g., Syncthing temp -> final)."""
        if event.is_directory:
            return
        self._handle_audio_event(Path(event.dest_path))
    
    def _handle_audio_event(self, audio_path: Path):
        """Common handler for all file events."""
        # Check file extension
        if audio_path.suffix.lower() not in AUDIO_EXTENSIONS:
            return
        
        # Skip if already processed
        if str(audio_path) in self.processed_files:
            return
        
        # Avoid duplicate processing
        if str(audio_path) in self.processing:
            return
        
        # Check if file exists and is stable (not being written)
        if not audio_path.exists():
            return
        
        if not self._is_file_stable(audio_path):
            return
        
        self.processing.add(str(audio_path))
        
        try:
            logger.info(f"📥 New {self.note_type} audio: {audio_path.name}")
            self._process_audio(audio_path)
            self.processed_files.add(str(audio_path))
        except Exception as e:
            logger.error(f"❌ Error processing {audio_path.name}: {e}")
            self._move_to_failed(audio_path, self.note_type, str(e))
        finally:
            self.processing.discard(str(audio_path))
    
    def _is_file_stable(self, file_path: Path, wait_seconds=3) -> bool:
        """Check if file is done being written by comparing size over time."""
        try:
            size1 = file_path.stat().st_size
            if size1 == 0:
                return False
            time.sleep(wait_seconds)
            size2 = file_path.stat().st_size
            return size1 == size2
        except Exception:
            return False
    
    def process_existing_file(self, audio_path: Path):
        """Process an existing file (called on startup)."""
        self._handle_audio_event(audio_path)
    def _process_audio(self, audio_path: Path):
        """Transcribe and summarize audio file."""
        filename = audio_path.stem
        
        # 1. Transcribe
        logger.info("🎤 Transcribing...")
        transcript = self._transcribe(audio_path)
        logger.info(f"✓ Transcript: {len(transcript)} chars")
        
        # 2. Generate summary
        logger.info(f"🤖 Generating {self.note_type} summary...")
        summary = self._generate_summary(transcript, self.note_type, self.config, filename)
        
        # 3. Save to Logseq
        page_path = self._save_to_logseq(summary, filename)
        logger.info(f"✓ Created page: {page_path.name}")
        
        # 4. Add to journal
        self._add_to_journal(filename, page_path.stem)
        logger.info(f"✓ Added to journal: {datetime.now().strftime('%Y_%m_%d')}.md")
        
        # 5. Archive
        done_path = self._move_to_done(audio_path, self.note_type)
        logger.info(f"✓ Moved to done: {done_path.relative_to(BASE_DIR)}")
        logger.info(f"✅ Complete: {audio_path.name}")
    
    def _transcribe(self, audio_path: Path) -> str:
        """Transcribe audio using Whisper with timestamps."""
        result = WHISPER_MODEL.transcribe(str(audio_path), word_timestamps=True)
        
        # Format with timestamps for readability
        segments = result.get("segments", [])
        if not segments:
            return result["text"].strip()
        
        formatted_lines = []
        for segment in segments:
            start_time = self._format_timestamp(segment["start"])
            text = segment["text"].strip()
            formatted_lines.append(f"({start_time}) {text}")
        
        return "\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS timestamp."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def _generate_summary(self, transcript: str, note_type: str, config: dict, filename: str) -> str:
        """Call local summarizer via subprocess."""
        try:
            env = os.environ.copy()
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "summarizer_local.py"), note_type, filename],
                input=transcript,
                capture_output=True,
                text=True,
                env=env,
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
        title = Path(filename).stem
        
        # Format with proper Logseq metadata
        return f"""# 🎙️ {title}

tags:: #voice-note #{self.note_type} #inbox
recorded:: [[{date}]]
processed:: false

---

## Summary
- Unable to generate AI summary. See raw transcript below.

---

## 📄 Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

{transcript}

</details>"""
        """Fallback format if summarization fails."""
        date = datetime.now().strftime("%Y-%m-%d")
        return f"""## Summary

Unable to generate AI summary. See raw transcript below.

---

## 📄 Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

{transcript}

</details>"""
    
    def _save_to_logseq(self, content: str, filename: str) -> Path:
        """Save summary to Logseq pages directory."""
        date = datetime.now().strftime("%Y-%m-%d")
        page_name = f"{date}-{filename}.md"
        page_path = LOGSEQ_PAGES / page_name
        
        page_path.write_text(content, encoding="utf-8")
        return page_path
    
    def _add_to_journal(self, filename: str, page_stem: str):
        """Add link to today's journal."""
        date = datetime.now().strftime("%Y_%m_%d")
        journal_path = LOGSEQ_JOURNALS / f"{date}.md"
        
        link = f"\n- [[{page_stem}]]\n"
        
        if journal_path.exists():
            content = journal_path.read_text(encoding="utf-8")
            if link not in content:
                journal_path.write_text(content + link, encoding="utf-8")
        else:
            journal_path.write_text(link, encoding="utf-8")
    
    def _move_to_done(self, audio_path: Path, note_type: str) -> Path:
        """Move audio to done archive."""
        done_dir = ARCHIVE_DIR / note_type / "done"
        done_dir.mkdir(parents=True, exist_ok=True)
        
        dest = done_dir / audio_path.name
        audio_path.rename(dest)
        return dest
    
    def _move_to_failed(self, audio_path: Path, note_type: str, error: str):
        """Move audio to failed archive with error log."""
        failed_dir = ARCHIVE_DIR / note_type / "failed"
        failed_dir.mkdir(parents=True, exist_ok=True)
        
        dest = failed_dir / audio_path.name
        audio_path.rename(dest)
        
        error_log = failed_dir / f"{audio_path.stem}_error.txt"
        error_log.write_text(f"{datetime.now()}\n{error}\n", encoding="utf-8")
        logger.info(f"✓ Moved to failed: {dest.relative_to(BASE_DIR)}")


def main():
    """Start watching all type-specific inboxes."""
    logger.info("=" * 60)
    logger.info("🎙️  Voice Notes Service v3 (Multi-Type)")
    logger.info("=" * 60)
    logger.info(f"Watching: {INBOX_DIR}")
    logger.info(f"Pages: {LOGSEQ_PAGES}")
    logger.info(f"Archive: {ARCHIVE_DIR}")
    
    # Load available types
    types = type_manager.list_available_types()
    logger.info(f"Available types: {types}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Create observer
    observer = Observer()
    
    # Register handler for each type
    for note_type in types:
        config = type_manager.load_config(note_type)
        handler = VoiceNoteHandler(note_type, config)
        inbox_path = INBOX_DIR / note_type
        inbox_path.mkdir(parents=True, exist_ok=True)
        
        observer.schedule(handler, str(inbox_path), recursive=False)
        logger.info(f"Watching inbox: {note_type}")
    
    # Store handlers for startup scan
    handlers = {}
    
    # Register handler for each type
    for note_type in types:
        config = type_manager.load_config(note_type)
        handler = VoiceNoteHandler(note_type, config)
        handlers[note_type] = handler
        inbox_path = INBOX_DIR / note_type
        inbox_path.mkdir(parents=True, exist_ok=True)
        
        observer.schedule(handler, str(inbox_path), recursive=False)
        logger.info(f"Watching inbox: {note_type}")
    
    # Start watching
    observer.start()
    
    # Process any existing files on startup
    logger.info("🔍 Scanning for existing files...")
    for note_type, handler in handlers.items():
        inbox_path = INBOX_DIR / note_type
        
        if inbox_path.exists():
            for audio_file in inbox_path.iterdir():
                if audio_file.is_file() and audio_file.suffix.lower() in AUDIO_EXTENSIONS:
                    logger.info(f"Found existing file: {audio_file.name}")
                    handler.process_existing_file(audio_file)
    logger.info("✓ Startup scan complete")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Stopping...")
    
    observer.join()


if __name__ == "__main__":
    main()
