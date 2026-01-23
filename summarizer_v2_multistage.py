#!/usr/bin/env python3
"""
Multi-stage summarizer for BJJ class notes.
Uses specialized prompts for each section to create teachable, system-focused notes.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict
import json

sys.path.insert(0, str(Path(__file__).parent))

from openai import OpenAI
import type_manager

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_techniques(transcript: str, config: Dict) -> str:
    """Extract techniques demonstrated with minimal, teach-friendly descriptions."""
    prompt = f"""Extract the techniques demonstrated in this BJJ class transcript.

Format as a bulleted list with brief descriptions (1 sentence max each).

DOMAIN CONTEXT:
{json.dumps(config.get('domain_dictionary', {}), indent=2)}

Transcript:
{transcript}

Output format:
- Technique Name
  - One sentence describing what it is and why it matters

List only the major techniques, 4-6 items."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_key_positions(transcript: str, config: Dict) -> str:
    """Extract key positions with descriptions."""
    prompt = f"""Extract the key positions described in this BJJ transcript.

These are the main positional milestones students will reach during the lesson.

Format each position with:
- Position Name
  - What it is and how you know you're in it (1-2 sentences)

Transcript:
{transcript}

List 4-6 key positions that represent major waypoints in the system."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_primary_sequence(transcript: str, config: Dict) -> str:
    """Extract the primary attack sequence in step-by-step format."""
    prompt = f"""Extract the PRIMARY attack sequence from this BJJ transcript.
This is the main entry and first technique the instructor emphasizes.

Format as numbered steps:
1. [Starting position] - What you begin with
2. [Grip/Control] - How you control your opponent
3. [Movement] - The key motion
4. [Result] - Where you end up

Keep to 5-7 steps maximum.
Each step should be 1 sentence.
Include at each step: what you're looking for / how you know you're doing it right.

Transcript:
{transcript}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_follow_ups(transcript: str, config: Dict) -> str:
    """Extract follow-up techniques based on opponent reactions."""
    prompt = f"""Extract the follow-up techniques from this BJJ transcript.
These are reactions to what the opponent does after the primary attack.

Format each follow-up as:
### [Follow-up Technique Name]
**When to use:** [What opponent does to trigger this]
**Steps:**
1. [Step]
2. [Step]
(Keep to 3-5 steps max)

List the main follow-ups (typically 2-4 options).

Transcript:
{transcript}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_drills(transcript: str, config: Dict) -> str:
    """Extract drills with progression (entry → detail → reaction)."""
    prompt = f"""Extract the drills and training progressions from this BJJ transcript.

Each drill should follow this structure:
### Drill N: [Name]
**Starting position:** [Where]
**Goal:** [What position you're trying to reach]
**Steps:**
1. [Basic entry step]
2. [Key detail to focus on]
3. [How opponent commonly reacts / what to adjust]

Create 3-4 drills in teaching progression order.
Keep each to 3-5 steps.
Structure as: Basic entry → Add detail → React to opponent

Transcript:
{transcript}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_core_concepts(transcript: str, config: Dict) -> str:
    """Extract principles, key insights, and teaching notes."""
    prompt = f"""Extract the core concepts, principles, and key teaching points from this BJJ transcript.

Organize into three subsections:

**Principles Taught**
- Bullet points of fundamental concepts (max 5)

**Key Insights**
- Teaching emphasis points the instructor highlighted (max 5)

**Common Mistakes to Avoid**
- Things students commonly do wrong (max 3-4)

Keep each point to 1-2 sentences max.
Remove any redundancy between sections.

Transcript:
{transcript}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_overview(techniques: str, positions: str, primary: str, followups: str, drills: str) -> str:
    """Synthesize overview after all content is extracted."""
    prompt = f"""Write a brief Overview section for BJJ class notes.
This is written LAST after all other content is extracted.

Use this information to create:

**Primary Attack**
A 2-3 sentence intro explaining the main entry point and why it matters.

**Overview of Options**
2-3 sentences explaining the follow-ups and decision tree.

Use this extracted content as reference:

Techniques Demonstrated:
{techniques}

Key Positions:
{positions}

Primary Sequence Summary:
{primary[:200]}...

Follow-ups Available:
{followups[:300]}...

Drills Overview:
{drills[:300]}...

The overview should connect these pieces into a coherent teaching narrative.
Do not repeat details - just tie them together."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def format_output(
    overview: str,
    techniques: str,
    positions: str,
    core_concepts: str,
    primary: str,
    followups: str,
    drills: str,
    transcript: str,
    filename: str
) -> str:
    """Format all sections into final markdown."""
    
    date = datetime.now().strftime("%Y-%m-%d")
    title = Path(filename).stem.replace("-", " ").replace("_", " ").title()
    
    output = f"""# 🎙️ {title}

tags:: #voice-note #bjj #inbox
recorded:: [[{date}]]
processed:: false

---

## Overview
{overview}

### Techniques Demonstrated
{techniques}

### Key Positions
{positions}

## Core Concepts
{core_concepts}

## Techniques

### Primary Sequence
{primary}

### Follow-ups
{followups}

## Drills
{drills}

---

## 📄 Raw Transcript

<details>
<summary>Click to expand full transcript</summary>

{transcript}

</details>
"""
    return output


def main():
    """Main entry point."""
    
    if sys.stdin.isatty():
        print("Usage: cat transcript.txt | python summarizer_v2_multistage.py bjj filename.wav", file=sys.stderr)
        sys.exit(1)
    
    # Parse arguments
    note_type = sys.argv[1] if len(sys.argv) > 1 else "bjj"
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
        
        # Stage 1: Extract techniques
        print(f"📖 Extracting techniques...", file=sys.stderr)
        techniques = extract_techniques(transcript, config)
        
        # Stage 2: Extract key positions
        print(f"📍 Extracting key positions...", file=sys.stderr)
        positions = extract_key_positions(transcript, config)
        
        # Stage 3: Extract primary sequence
        print(f"🎯 Extracting primary sequence...", file=sys.stderr)
        primary = extract_primary_sequence(transcript, config)
        
        # Stage 4: Extract follow-ups
        print(f"🔄 Extracting follow-ups...", file=sys.stderr)
        followups = extract_follow_ups(transcript, config)
        
        # Stage 5: Extract drills
        print(f"🏋️ Extracting drills...", file=sys.stderr)
        drills = extract_drills(transcript, config)
        
        # Stage 6: Extract core concepts
        print(f"💡 Extracting core concepts...", file=sys.stderr)
        concepts = extract_core_concepts(transcript, config)
        
        # Stage 7: Generate overview (LAST)
        print(f"📋 Synthesizing overview...", file=sys.stderr)
        overview = generate_overview(techniques, positions, primary, followups, drills)
        
        # Format final output
        output = format_output(
            overview, techniques, positions, concepts,
            primary, followups, drills, transcript, filename
        )
        
        print(output)
        print(f"✓ Summary generated", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
