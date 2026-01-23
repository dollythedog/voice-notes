#!/usr/bin/env python3
"""
Local Summarizer: Standalone AI summarization using OpenAI API.
No project_wizard dependency. Generates Logseq-formatted summaries.

Output follows strict Logseq markdown rules:
- Each bullet on separate line starting with dash (-)
- Tab indentation for nested hierarchy
- No bullet symbols (•, ◦, *)
- No empty lines between bullets
- Proper metadata properties (processed:: false)
"""

import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add voice_notes to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import type_manager


def correct_transcript_with_domain(transcript: str, domain_dict: Dict) -> str:
    """
    Apply domain-specific corrections to transcript.
    Replaces common Whisper misrecognitions with correct terms.
    """
    corrected = transcript
    
    # Process all domain categories (techniques, positions, concepts, terminology)
    for category, terms in domain_dict.items():
        if not isinstance(terms, list):
            continue
        
        for term in terms:
            # Case-insensitive search and replace
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            # Find matches and preserve original case where possible
            matches = re.finditer(pattern, corrected, re.IGNORECASE)
            for match in matches:
                original_text = match.group(0)
                # Replace with the term from our domain dict (correct spelling)
                corrected = corrected[:match.start()] + term + corrected[match.end():]
    
    return corrected


def generate_summary(
    transcript: str,
    note_type: str,
    config: Dict,
    filename: str = "unknown"
) -> str:
    """
    Generate type-specific summary using OpenAI API.
    
    Args:
        transcript: Raw transcript text
        note_type: Type of note (bjj, meeting, etc.)
        config: Type configuration dict
        filename: Original audio filename
    
    Returns:
        Logseq markdown summary
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Install with: pip install openai", file=sys.stderr)
        return _fallback_summary(transcript, config)
    
    # Initialize OpenAI client (uses OPENAI_API_KEY env var)
    try:
        client = OpenAI()
    except Exception as e:
        print(f"ERROR: Failed to initialize OpenAI client: {e}", file=sys.stderr)
        return _fallback_summary(transcript, config)
    
    prompts = type_manager.get_prompts(config)
    system_prompt = prompts.get("system", "You are a helpful summarizer.")
    user_prompt_template = prompts.get("user", "Summarize: {{transcript}}")
    
    # Substitute transcript into prompt
    user_prompt = user_prompt_template.replace("{{transcript}}", transcript[:4000])
    
    # Add Logseq formatting requirements to system prompt
    enhanced_system = system_prompt + "\n\nIMPORTANT OUTPUT FORMAT:\n- Output must use markdown outline format\n- Each bullet on SEPARATE LINE starting with dash (-)\n- Use tab indentation for nested points (one tab = one level)\n- Do NOT use bullet symbols like •, ◦, or *\n- Do NOT put multiple points in single paragraph\n- Do NOT leave empty lines between bullets"
    
    try:
        print(f"🤖 Calling OpenAI API for {note_type} summary...", file=sys.stderr)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": enhanced_system},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        summary_text = response.choices[0].message.content.strip()
        print(f"✓ Summary generated ({len(summary_text.split())} words)", file=sys.stderr)
        return summary_text
        
    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}", file=sys.stderr)
        return _fallback_summary(transcript, config)


def _fallback_summary(transcript: str, config: Dict) -> str:
    """Generate minimal fallback summary when LLM fails."""
    return f"""## Summary
- Unable to generate AI summary. See raw transcript below."""


def format_output_logseq(
    summary: str,
    transcript: str,
    filename: str,
    config: Dict
) -> str:
    """
    Format final output as Logseq markdown following strict rules:
    - Proper metadata (processed:: false)
    - Tab-indented hierarchy
    - No empty lines between bullets
    - Correct heading structure
    """
    
    # Create title from filename
    title = Path(filename).stem
    title = re.sub(r'^(Voice|Recording|Audio)\s*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[_\-]+', ' ', title)
    
    date = datetime.now().strftime("%Y-%m-%d")
    note_type_tag = Path(filename).parent.name  # bjj, meeting, etc.
    
    # Build output following Logseq rules
    output_lines = []
    
    # Header (H1)
    output_lines.append(f"# 🎙️ {title}")
    output_lines.append("")  # Blank line after header
    
    # Metadata properties (must come before content)
    output_lines.append(f"tags:: #voice-note #{note_type_tag} #inbox")
    output_lines.append(f"recorded:: [[{date}]]")
    output_lines.append(f"processed:: false")
    output_lines.append("")  # Blank line after metadata
    
    # Separator
    output_lines.append("---")
    output_lines.append("")  # Blank line after separator
    
    # Summary content (ensure proper formatting)
    output_lines.append("## Summary")
    
    # Process summary to ensure Logseq bullet format
    summary_formatted = _ensure_logseq_format(summary)
    output_lines.append(summary_formatted)
    
    output_lines.append("")  # Blank line before next section
    output_lines.append("---")
    output_lines.append("")  # Blank line
    
    # Raw transcript in collapsible details
    output_lines.append("## 📄 Raw Transcript")
    output_lines.append("")
    output_lines.append("<details>")
    output_lines.append("<summary>Click to expand full transcript</summary>")
    output_lines.append("")
    output_lines.append(transcript)
    output_lines.append("")
    output_lines.append("</details>")
    
    return "\n".join(output_lines)


def _ensure_logseq_format(text: str) -> str:
    """
    Ensure text follows Logseq bullet format rules:
    - Each line starts with dash (-)
    - Tab indentation for nesting
    - No empty lines between bullets
    """
    lines = text.split("\n")
    output = []
    
    for line in lines:
        line = line.rstrip()
        
        # Skip empty lines
        if not line.strip():
            continue
        
        # If it's a heading (##, ###), keep it as-is
        if line.strip().startswith("#"):
            output.append(line)
            continue
        
        # Ensure bullet format
        stripped = line.lstrip()
        
        # Count leading spaces/tabs for indentation
        leading = len(line) - len(stripped)
        indent_level = leading // 2  # Approximate tab level
        
        # If already a bullet, keep as-is
        if stripped.startswith("-"):
            output.append(line)
        # If starts with number (1., 2.), convert to bullet
        elif re.match(r"^\d+\.", stripped):
            bullet_text = re.sub(r"^\d+\.\s*", "", stripped)
            tabs = "\t" * indent_level if indent_level > 0 else ""
            output.append(f"{tabs}- {bullet_text}")
        # If starts with •, ◦, etc., convert to dash
        elif re.match(r"^[•◦▪]\s", stripped):
            bullet_text = re.sub(r"^[•◦▪]\s*", "", stripped)
            tabs = "\t" * indent_level if indent_level > 0 else ""
            output.append(f"{tabs}- {bullet_text}")
        # Otherwise, make it a bullet
        else:
            tabs = "\t" * indent_level if indent_level > 0 else ""
            output.append(f"{tabs}- {stripped}")
    
    return "\n".join(output)


def main():
    """Main entry point for CLI usage."""
    
    if sys.stdin.isatty():
        print("Usage: cat transcript.txt | python summarizer_local.py bjj filename.wav", file=sys.stderr)
        sys.exit(1)
    
    # Parse arguments
    note_type = sys.argv[1] if len(sys.argv) > 1 else "meeting"
    filename = sys.argv[2] if len(sys.argv) > 2 else "unknown.wav"
    
    # Read transcript from stdin
    transcript = sys.stdin.read().strip()
    
    if not transcript:
        print("ERROR: No transcript provided on stdin", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load type config
        config = type_manager.load_config(note_type)
        print(f"📋 Processing {note_type} note: {filename}", file=sys.stderr)
        
        # Step 1: Correct transcript with domain dictionary
        domain_dict = type_manager.get_domain_dictionary(config)
        if domain_dict:
            print(f"📖 Applying domain corrections...", file=sys.stderr)
            transcript = correct_transcript_with_domain(transcript, domain_dict)
        
        # Step 2: Generate summary
        summary = generate_summary(transcript, note_type, config, filename)
        
        # Step 3: Format output for Logseq
        output = format_output_logseq(summary, transcript, filename, config)
        
        # Output to stdout
        print(output)
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
