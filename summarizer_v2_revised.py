#!/usr/bin/env python3
"""
Multi-stage summarizer v2 (REVISED) for BJJ class notes.
Uses specialized prompts for each section to create teachable, system-focused notes.
Adapted for any BJJ system/class.
"""

import sys
import os
from pathlib import Path
from typing import Dict
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from openai import OpenAI
import type_manager

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_techniques(transcript: str, config: Dict) -> str:
    """Extract techniques demonstrated with teaching overview focus."""
    prompt = f"""YOUR TASK: Generate a list of techniques demonstrated in this BJJ class to provide 
a quick reference for what students will learn.

PURPOSE: Help instructors and students understand the scope of techniques covered. 
This is a teaching overview, not exhaustive documentation.

OUTPUT FORMAT: Bullet list, one technique per line, 1-sentence description max

POSITIVE EXAMPLE:
- Half Butterfly Guard
  - A guard position using inside leg positioning for control and leg lock setups
- Single Leg X-Guard
  - A leg entanglement position for sweeps and leg lock attacks

DOMAIN CONTEXT (use these terms):
{json.dumps(config.get('domain_dictionary', {}), indent=2)}

Transcript:
{transcript[:3000]}

Generate 4-6 key techniques only. Be specific to what was actually taught."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_key_positions(transcript: str, config: Dict) -> str:
    """Extract positional waypoints students will reach."""
    prompt = f"""YOUR TASK: Extract the major positional waypoints students will reach during this 
lesson, so they can recognize when they've achieved each milestone.

PURPOSE: Create a positional roadmap for the system. Each position should be 
recognizable and specific to what's being taught.

OUTPUT FORMAT: Bullet list, position name with 1-sentence description of recognition

POSITIVE EXAMPLE:
- Knee Shield
  - Your knee is across opponent's body, blocking their advance
- Half Butterfly Guard
  - One hook deep near opponent's hip, other leg creating space

Transcript:
{transcript[:3000]}

List 4-5 key positions in the system. Describe how to recognize each one."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_entry_to_position(transcript: str, config: Dict) -> str:
    """Extract entry drill - how to get into the main position."""
    prompt = f"""YOUR TASK: Generate step-by-step instructions for ENTERING the primary position 
of this system, so a student can follow the progression clearly.

PURPOSE: This is the entry drill. Students learn to get into the starting position 
for this system. Make it teachable and clear.

OUTPUT FORMAT: 
- Numbered steps (3-4 max)
- One sentence per step
- Each step is one clear action/concept

POSITIVE EXAMPLE:
1. Establish knee shield with bottom hook on opponent's shin
2. Control opponent's shoulder with arm drag grip, pulling tight
3. Transition butterfly hook close to opponent's hip as they posture up

NEGATIVE EXAMPLE (avoid):
❌ 1. Get your knee shield going and maintain control of the opponent's upper body
   2. As the opponent starts to move, you're going to want to shift your leg position

Transcript:
{transcript}

Find the ENTRY sequence - how to get into the main guard/position from a starting point.
Keep steps concise and actionable. Each line should be ONE clear thing to do."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_primary_sequence(transcript: str, config: Dict) -> str:
    """Extract the primary attack sequence."""
    prompt = f"""YOUR TASK: Generate the step-by-step PRIMARY attack sequence for this system, 
so instructors can teach the main technique clearly.

PURPOSE: The primary sequence is the main technique students should practice first. 
It's the foundation of the system.

OUTPUT FORMAT:
- Numbered steps (4-5 max)
- One sentence per step
- Include what to feel/look for (verification point)

POSITIVE EXAMPLE:
1. From half butterfly, secure arm drag grip on wrist and shoulder
2. Shoot your knee deep behind opponent's hips to bump their weight forward
3. Fall flat on your back while maintaining shoulder control
4. Step on opponent's hip and knock them off balance to one side
5. Achieve single leg X with your shin across their leg

NEGATIVE EXAMPLE (avoid):
❌ 1. Make sure you have good upper body control in place
   2. Your leg is going to move in a particular way that creates pressure
   3. You should end up in a good position from here

Transcript:
{transcript}

Extract the PRIMARY/MAIN attack - the first sequence to learn after entry.
Each step must be concrete and actionable, not vague."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_reactions(transcript: str, config: Dict) -> str:
    """Extract follow-up techniques based on opponent reactions."""
    prompt = f"""YOUR TASK: Extract the 2 main opponent reactions and the counter-technique for each, 
so students know how to adapt when the primary doesn't work.

PURPOSE: Teach the decision tree: "If they do this, do that." This mirrors real rolling.

OUTPUT FORMAT:
For each reaction (max 2):
### Reaction N: [Name]
**When to use:** One sentence describing opponent's action that triggers this
- Step 1 description
- Step 2 description
- Step 3 description

POSITIVE EXAMPLE:
### Reaction 1: Choi Bar (Cross Face Defense)
**When to use:** Opponent attempts to cross face your head
- Sit up and reach for their head to create space
- Isolate their arm by controlling shoulder and wrist
- Pull their shoulder tight to your chest and fall back
- Flatten hips to secure the arm bar finish

Transcript:
{transcript}

Find the main opponent reactions and how to counter each one.
Use concrete, action-based steps. No vague descriptions."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_core_concepts(transcript: str, config: Dict) -> str:
    """Extract principles, key insights, and common mistakes."""
    prompt = f"""YOUR TASK: Extract teaching principles, key insights, and common mistakes so 
instructors can emphasize what matters and prevent bad habits.

PURPOSE: Help students understand the "why" behind techniques, not just the "how."

OUTPUT FORMAT:
Three subsections, bullet list, ONE SENTENCE per item (max 5 per section)

POSITIVE EXAMPLE:
**Principles Taught**
- Control upper body to manage opponent's balance and reactions
- Use knee shield to create distance before committing to butterfly hook
- Keep foot deep near hip for leg entanglements, wide for sweeps

**Key Insights**
- Knee shield is the entry; don't rush to butterfly hook
- Primary sequence sets up all follow-up reactions
- Opponent's weight distribution determines which reaction to use

**Common Mistakes to Avoid**
- Placing butterfly hook too wide or too loose early on
- Using butterfly hook before establishing upper body control
- Staying on your side instead of falling flat during primary sequence

Transcript:
{transcript}

Extract the core teaching points from this class.
Each bullet must be ONE clear sentence. No multi-sentence bullets."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_drills(transcript: str, config: Dict) -> str:
    """Extract progressive drills for teaching."""
    prompt = f"""YOUR TASK: Generate 3-4 progressive drills that build on each other, so students 
can practice incrementally from basic entry to complex reactions.

PURPOSE: Create a class structure: drill entry → drill primary → drill reactions.

OUTPUT FORMAT:
For each drill:
### Drill N: [Name]
**Starting position:** Where drill begins
**Goal:** What position/technique students are learning
**Steps:**
1. Step description
2. Step description
3. Step description

POSITIVE EXAMPLE:
### Drill 1: Knee Shield to Half Butterfly Entry
**Starting position:** Knee shield guard
**Goal:** Transition into half butterfly guard
**Steps:**
1. Establish knee shield with bottom hook on opponent's shin
2. Control opponent's shoulder with arm drag grip
3. Transition butterfly hook close to hip as opponent postures up

### Drill 2: Half Butterfly to Single Leg X
**Starting position:** Half butterfly guard
**Goal:** Execute primary sequence to single leg X
**Steps:**
1. Secure arm drag grip with shoulder control
2. Shoot knee deep behind hips, bump weight forward
3. Fall flat on back, maintain control, step on hip

Transcript:
{transcript}

Create progressive drills showing the teaching sequence of this class.
Each drill must have clear starting position and goal.
Steps should be concrete and actionable (one sentence each)."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_overview(techniques: str, positions: str, entry: str, primary: str, reactions: str, drills: str) -> str:
    """Synthesize overview after all content is extracted."""
    prompt = f"""YOUR TASK: Create a brief teaching overview that ties together the complete 
system (entry → primary → reactions), so students understand the flow.

PURPOSE: Opening remarks for class. Answer: "What are we learning and why?"

OUTPUT FORMAT:
**Primary Entry**
1-2 sentences about the entry point

**Main Technique**
1-2 sentences about the primary sequence

**Reaction Framework**
1-2 sentences about how reactions work

POSITIVE EXAMPLE:
**Primary Entry**
Today we're learning the half butterfly system starting from knee shield position. 
The knee shield allows us to control distance while setting up for more aggressive attacks.

**Main Technique**
The primary attack is the single leg X-guard entry, which uses weight distribution 
and upper body control to put the opponent off-balance.

**Reaction Framework**
When the opponent reacts, you have two main options: Choi Bar for cross face attempts, 
or Saddle entry when they put heavy weight on their opposite leg.

Use this extracted content as reference:

Entry to Position Summary:
{entry[:300]}

Primary Sequence Summary:
{primary[:300]}

Reactions Summary:
{reactions[:300]}

Drills Summary:
{drills[:300]}

Write a compelling, concise overview that connects entry → primary → reactions."""

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
    entry: str,
    primary: str,
    reactions: str,
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

## Techniques Demonstrated
{techniques}

## Key Positions
{positions}

## Core Concepts
{core_concepts}

## Techniques

### Entry to Position
{entry}

### Primary Sequence
{primary}

### Reactions
{reactions}

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
        print("Usage: cat transcript.txt | python summarizer_v2_revised.py bjj filename.wav", file=sys.stderr)
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
        print(f"📋 Processing {note_type} class notes: {filename}", file=sys.stderr)
        
        # Stage 1: Extract techniques
        print(f"📖 Extracting techniques...", file=sys.stderr)
        techniques = extract_techniques(transcript, config)
        
        # Stage 2: Extract key positions
        print(f"📍 Extracting key positions...", file=sys.stderr)
        positions = extract_key_positions(transcript, config)
        
        # Stage 3: Extract entry to position
        print(f"🚪 Extracting entry to position...", file=sys.stderr)
        entry = extract_entry_to_position(transcript, config)
        
        # Stage 4: Extract primary sequence
        print(f"🎯 Extracting primary sequence...", file=sys.stderr)
        primary = extract_primary_sequence(transcript, config)
        
        # Stage 5: Extract reactions
        print(f"🔄 Extracting reactions...", file=sys.stderr)
        reactions = extract_reactions(transcript, config)
        
        # Stage 6: Extract drills
        print(f"🏋️ Extracting drills...", file=sys.stderr)
        drills = extract_drills(transcript, config)
        
        # Stage 7: Extract core concepts
        print(f"💡 Extracting core concepts...", file=sys.stderr)
        concepts = extract_core_concepts(transcript, config)
        
        # Stage 8: Generate overview (LAST)
        print(f"📋 Synthesizing overview...", file=sys.stderr)
        overview = generate_overview(techniques, positions, entry, primary, reactions, drills)
        
        # Format final output
        output = format_output(
            overview, techniques, positions, concepts,
            entry, primary, reactions, drills, transcript, filename
        )
        
        print(output)
        print(f"✓ BJJ class notes generated", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
