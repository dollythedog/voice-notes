#!/usr/bin/env python3
"""Test the complete voice notes integration."""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Extract transcript from Logseq
voice_inbox = Path("/srv/logseq_graph/pages/📥 Voice Inbox.md")
content = voice_inbox.read_text()

# Get the transcript section
start = content.find("- TODO Then")
end = content.find("  source::")
transcript = content[start:end].strip()

# Remove TODO markers and bullet points
transcript = transcript.replace("- TODO ", "")
transcript = transcript.replace("- ", "")

print("📝 Extracted transcript...")
print(f"Length: {len(transcript)} characters\n")

# Generate summary
print("🤖 Generating AI summary...")
result = subprocess.run(
    ["/srv/project_wizard/venv/bin/python3", "/srv/voice_notes/summarizer.py"],
    input=f"{transcript}\n---FILENAME---\nMeeting-hollingsworth.m4a",
    capture_output=True,
    text=True,
    timeout=120
)

if result.returncode != 0:
    print(f"❌ Error: {result.stderr}")
    sys.exit(1)

summary = result.stdout

# Save to Logseq pages
pages_dir = Path("/srv/logseq_graph/pages")
page_name = f"{datetime.now().strftime('%Y-%m-%d')}-Meeting-hollingsworth"
page_file = pages_dir / f"{page_name}.md"

page_file.write_text(summary, encoding='utf-8')
print(f"✓ Created page: {page_file.name}")

# Add to journal
journals_dir = Path("/srv/logseq_graph/journals")
today = datetime.now().strftime("%Y_%m_%d")
journal_file = journals_dir / f"{today}.md"

with open(journal_file, 'a', encoding='utf-8') as f:
    f.write(f"\n- 🎙️ [[{page_name}]] #voice-note #inbox\n")

print(f"✓ Added to journal: {journal_file.name}")
print(f"\n✅ Integration test complete!")
print(f"\nView the page: {page_file}")
