#!/usr/bin/env python3
"""
Enhanced transcription service with AI-powered summarization.

Watches for audio files, transcribes them with Whisper, then generates
structured summaries using project_wizard's AI agent pipeline.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project_wizard to path
sys.path.insert(0, '/srv/project_wizard')

import whisper
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import project_wizard components
from app.services.ai_agents.llm_client import LLMClient
from app.services.ai_agents.section_agent import SectionAgentController
from app.models.blueprint import get_registry
from jinja2 import Template


# Configuration
INBOX_DIR = Path("/srv/voice_notes/inbox")
PROCESSED_DIR = Path("/srv/voice_notes/processed")
LOGSEQ_PAGE = Path("/srv/logseq_graph/pages/📥 Voice Inbox.md")
LOG_DIR = Path("/srv/voice_notes/logs")
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


class TranscriptSummarizer:
    """Generate structured summaries from transcripts using project_wizard agents."""
    
    def __init__(self):
        """Initialize AI components."""
        self.llm_client = LLMClient()
        self.blueprint_registry = get_registry()
        
        # Load transcript_summary blueprint
        try:
            self.blueprint = self.blueprint_registry.load_blueprint("transcript_summary")
            self.prompts = self.blueprint_registry.load_prompts("transcript_summary")
            logger.info("✓ Loaded transcript_summary blueprint")
        except Exception as e:
            logger.error(f"Failed to load transcript_summary blueprint: {e}")
            raise
    
    def generate_summary(self, transcript: str, audio_filename: str) -> str:
        """
        Generate structured summary from raw transcript.
        
        Args:
            transcript: Raw transcript text from Whisper
            audio_filename: Original audio filename for reference
            
        Returns:
            Formatted markdown summary
        """
        logger.info("🤖 Generating AI summary...")
        
        # Prepare user inputs for the blueprint
        user_inputs = {
            "transcript": transcript,
            "audio_filename": audio_filename,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Use SectionAgentController for section-by-section generation
        section_agent = SectionAgentController(
            llm_client=self.llm_client,
            blueprint=self.blueprint,
            user_inputs=user_inputs,
            draft_config=self.prompts.get("draft_generation", {})
        )
        
        # Generate all sections
        section_agent.generate_all_sections()
        
        # Build sections dict for template
        sections = {}
        for section in section_agent.sections:
            sections[section.section_id] = {
                "content": section.content,
                "word_count": section.word_count
            }
        
        # Render template
        template_path = Path("/srv/project_wizard/patterns/transcript_summary/template.j2")
        with open(template_path) as f:
            template = Template(f.read())
        
        summary = template.render(
            timestamp=user_inputs["timestamp"],
            audio_filename=audio_filename,
            transcript=transcript,
            sections=sections
        )
        
        logger.info(f"✓ Summary generated ({sum(s['word_count'] for s in sections.values())} words)")
        return summary


class AudioFileHandler(FileSystemEventHandler):
    """Handle new audio files in inbox."""
    
    def __init__(self):
        self.whisper_model = whisper.load_model("base")
        self.summarizer = TranscriptSummarizer()
        logger.info("✓ Whisper model and AI summarizer loaded")
    
    def on_created(self, event):
        """Process new audio file."""
        if event.is_directory:
            return
        
        audio_path = Path(event.src_path)
        
        if audio_path.suffix.lower() not in AUDIO_EXTENSIONS:
            return
        
        logger.info(f"📥 New audio file detected: {audio_path.name}")
        
        try:
            # Wait for file to be fully written
            time.sleep(2)
            
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                logger.warning(f"⚠️  File not ready: {audio_path.name}")
                return
            
            # Transcribe with Whisper
            logger.info(f"🎤 Transcribing {audio_path.name}...")
            result = self.whisper_model.transcribe(str(audio_path), language="en")
            transcript = result["text"].strip()
            logger.info(f"✓ Transcription complete ({len(transcript)} chars)")
            
            # Generate AI summary
            summary = self.summarizer.generate_summary(transcript, audio_path.name)
            
            # Append to Logseq
            self._append_to_logseq(summary)
            
            # Move to processed
            dest = PROCESSED_DIR / audio_path.name
            audio_path.rename(dest)
            logger.info(f"✅ Complete: {audio_path.name} → {dest.name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {audio_path.name}: {e}", exc_info=True)
    
    def _append_to_logseq(self, content: str):
        """Append content to Logseq Voice Inbox page."""
        # Ensure page exists with header
        if not LOGSEQ_PAGE.exists():
            LOGSEQ_PAGE.parent.mkdir(parents=True, exist_ok=True)
            LOGSEQ_PAGE.write_text("# 📥 Voice Inbox\n\n")
        
        # Append new note
        with open(LOGSEQ_PAGE, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}\n")
        
        logger.info(f"✓ Appended to {LOGSEQ_PAGE.name}")


def main():
    """Run the transcription service."""
    # Ensure directories exist
    INBOX_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("🎙️  Voice Notes Transcription Service with AI Summarization")
    logger.info("=" * 60)
    logger.info(f"Watching: {INBOX_DIR}")
    logger.info(f"Output: {LOGSEQ_PAGE}")
    logger.info(f"Processed: {PROCESSED_DIR}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Start file watcher
    event_handler = AudioFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping service...")
        observer.stop()
    
    observer.join()
    logger.info("✓ Service stopped")


if __name__ == "__main__":
    main()
