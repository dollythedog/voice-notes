#!/usr/bin/env python3
"""
Voice Transcript Summarizer v3 - Simplified Three-Stage Pipeline

Orchestrates:
1. Outline Generation: Extract key topics from raw transcript
2. Section Expansion: Generate sections sequentially with deduplication
3. Format for Logseq: Clean markdown structure

Uses project_wizard AI agents.
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import json

# Add project_wizard to path
sys.path.insert(0, '/srv/project_wizard')

from app.services.blueprint_registry import BlueprintRegistry
from app.services.ai_agents.llm_client import LLMClient
from app.services.ai_agents.section_agent import SectionAgentController


def generate_transcript_summary(
    transcript: str,
    audio_filename: str = "unknown.m4a",
    verify: bool = False
) -> str:
    """
    Generate transcript summary using simplified 2-stage pipeline.
    
    Args:
        transcript: Raw transcript text from Whisper
        audio_filename: Original audio filename
        verify: If True, run verification (currently disabled due to timeout)
        
    Returns:
        Final markdown summary
    """
    
    print("\n" + "="*80, file=sys.stderr)
    print("🎙️  VOICE TRANSCRIPT SUMMARIZER v3", file=sys.stderr)
    print("="*80, file=sys.stderr)
    
    try:
        # Initialize components
        llm_client = LLMClient()
        blueprint_registry = BlueprintRegistry()
        
        # Load blueprint and prompts
        blueprint = blueprint_registry.load_blueprint("transcript_summary")
        prompts = blueprint_registry.load_prompts("transcript_summary")
        
        print("\n📋 STAGE 1: Outline Generation", file=sys.stderr)
        print("-" * 80, file=sys.stderr)
        
        # Stage 1: Generate outline to guide section expansion
        outline = generate_outline(transcript, llm_client, prompts.get("outline_generation", {}))
        print(f"✅ Outline: {len(outline.get('key_topics', []))} topics identified", file=sys.stderr)
        
        # Stage 2: Expand sections sequentially
        print("\n🔧 STAGE 2: Section Expansion", file=sys.stderr)
        print("-" * 80, file=sys.stderr)
        
        user_inputs = {
            "transcript": transcript,
            "audio_filename": audio_filename,
            "outline": json.dumps(outline)
        }
        
        section_controller = SectionAgentController(
            llm_client=llm_client,
            blueprint=blueprint,
            pattern_name="transcript_summary"
        )
        
        sections = section_controller.generate_all_sections(
            user_inputs=user_inputs,
            prompts=prompts,
            max_regenerations=1  # Reduced for speed
        )
        
        # Assemble final markdown
        summary_markdown = assemble_summary_markdown(
            sections=sections,
            transcript=transcript,
            audio_filename=audio_filename
        )
        
        print(f"\n✅ Summary generated: {len(summary_markdown.split())} words", file=sys.stderr)
        return summary_markdown
        
    except Exception as e:
        print(f"\n⚠️  Summarizer error: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
        # Fallback to raw transcript
        return create_fallback_summary(transcript, audio_filename)


def generate_outline(transcript: str, llm_client, config: dict) -> dict:
    """Extract key topics and structure from transcript."""
    
    system_message = config.get("identity", "You are an outline architect.")
    instructions = config.get("instructions", "Create an outline.")
    
    prompt = f"""{instructions}

Transcript:
{transcript[:3000]}

Return JSON with main_topic, key_topics[], decisions[], action_items[]."""
    
    try:
        response = llm_client.generate(
            prompt=prompt,
            system_message=system_message,
            temperature=0.5,
            max_tokens=1500
        )
        
        content = response.content.strip()
        if content.startswith("```"):
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]
        
        return json.loads(content)
    except Exception as e:
        print(f"⚠️  Outline generation failed: {e}", file=sys.stderr)
        return {
            "main_topic": "Transcript Discussion",
            "key_topics": ["Discussion"],
            "decisions": [],
            "action_items": []
        }


def assemble_summary_markdown(sections, transcript: str, audio_filename: str) -> str:
    """Assemble sections into final Logseq-formatted markdown."""
    
    parts = []
    section_order = ["overview", "key_points", "detailed_notes", "next_steps"]
    
    for section_id in section_order:
        if section_id in sections:
            section_data = sections[section_id]
            content = section_data.content.strip()
            
            if content:
                parts.append(f"## {section_data.section_title}")
                parts.append("")
                parts.append(content)
                parts.append("")
    
    # Add transcript in collapsible section
    parts.extend([
        "---",
        "",
        "## 📄 Raw Transcript",
        "",
        "<details>",
        "<summary>Click to expand full transcript</summary>",
        "",
        transcript,
        "",
        "</details>"
    ])
    
    return "\n".join(parts)


def create_fallback_summary(transcript: str, audio_filename: str) -> str:
    """Create minimal fallback summary when AI generation fails."""
    
    return f"""## Summary

### Overview
- See raw transcript below

---

## 📄 Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

{transcript}

</details>"""


if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
        
        # Parse input: "transcript\n---FILENAME---\nfilename.m4a"
        parts = input_data.split("\n---FILENAME---\n")
        transcript = parts[0].strip() if parts else ""
        audio_filename = parts[1].strip() if len(parts) > 1 else "unknown.m4a"
        
        if transcript:
            try:
                summary = generate_transcript_summary(
                    transcript=transcript,
                    audio_filename=audio_filename,
                    verify=False  # Verification disabled due to timeout
                )
                print(summary)
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("ERROR: No transcript provided", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: echo 'transcript\\n---FILENAME---\\nfile.m4a' | python summarizer_v3.py")
        sys.exit(1)
