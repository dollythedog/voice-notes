#!/usr/bin/env python3
"""Standalone summarizer using project_wizard AI agents."""

import sys
import os
sys.path.insert(0, '/srv/project_wizard')
os.chdir('/srv/project_wizard')

from pathlib import Path
from datetime import datetime
from jinja2 import Template

from app.services.ai_agents.llm_client import LLMClient
from app.services.ai_agents.section_agent import SectionAgentController
from app.services.blueprint_registry import BlueprintRegistry


def generate_summary(transcript: str, audio_filename: str) -> str:
    """Generate structured summary from raw transcript."""
    
    # Initialize components
    llm_client = LLMClient()
    blueprint_registry = BlueprintRegistry()
    
    # Load blueprint and prompts
    blueprint = blueprint_registry.load_blueprint("transcript_summary")
    prompts = blueprint_registry.load_prompts("transcript_summary")
    
    # Prepare inputs
    user_inputs = {
        "transcript": transcript,
        "audio_filename": audio_filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Generate sections
    section_agent = SectionAgentController(
        llm_client=llm_client,
        blueprint=blueprint
    )
    
    sections_dict = section_agent.generate_all_sections(
        user_inputs=user_inputs,
        prompts=prompts
    )
    
    # Build sections for template
    sections = {}
    for section_id, section_content in sections_dict.items():
        sections[section_id] = {
            "content": section_content.content,
            "word_count": section_content.word_count
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
    
    return summary


if __name__ == "__main__":
    # Read from stdin: transcript\n---FILENAME---\nfilename
    input_data = sys.stdin.read()
    
    if "---FILENAME---" in input_data:
        parts = input_data.split("---FILENAME---")
        transcript = parts[0].strip()
        filename = parts[1].strip()
    else:
        transcript = input_data.strip()
        filename = "unknown.m4a"
    
    summary = generate_summary(transcript, filename)
    print(summary)
