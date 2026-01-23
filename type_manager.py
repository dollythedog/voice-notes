#!/usr/bin/env python3
"""
Type Manager: Load and manage voice note type configurations.
Detects note type from directory path and returns appropriate config.
"""

import json
from pathlib import Path
from typing import Dict, Optional

CONFIGS_DIR = Path(__file__).parent / "configs" / "types"


def get_type_from_path(inbox_path: str) -> str:
    """
    Extract note type from inbox directory path.
    Examples:
        /srv/voice_notes/inboxes/bjj -> bjj
        /srv/voice_notes/inboxes/meeting -> meeting
    """
    path = Path(inbox_path)
    if path.name in ["meeting", "bjj", "personal", "lecture"]:
        return path.name
    # Default to generic if not recognized
    return "meeting"


def load_config(note_type: str) -> Dict:
    """
    Load configuration for a specific note type.
    Returns config dict or raises FileNotFoundError if type config missing.
    """
    config_file = CONFIGS_DIR / f"{note_type}.json"
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Config not found for type '{note_type}'. "
            f"Available types: {list_available_types()}"
        )
    
    with open(config_file, 'r') as f:
        return json.load(f)


def list_available_types() -> list:
    """List all available note types."""
    if not CONFIGS_DIR.exists():
        return []
    return [f.stem for f in CONFIGS_DIR.glob("*.json")]


def get_config_for_inbox(inbox_path: str) -> Dict:
    """
    Load config for an inbox directory path.
    Type is detected from the directory name.
    """
    note_type = get_type_from_path(inbox_path)
    return load_config(note_type)


def get_domain_dictionary(config: Dict) -> Dict:
    """
    Extract domain dictionary from config.
    Returns dict with terminology lists for post-processing transcript.
    """
    return config.get("domains", {})


def get_section_headers(config: Dict) -> list:
    """Get ordered list of section headers for this type."""
    return config.get("sections", [])


def get_prompts(config: Dict) -> Dict:
    """Get LLM prompts (system and user) for this type."""
    return config.get("prompts", {})


def get_output_template(config: Dict) -> str:
    """Get Markdown template for output."""
    return config.get("output_template", "# {{title}}\n\n{{sections}}\n\n{{transcript}}")


if __name__ == "__main__":
    # Test: list available types
    print(f"Available types: {list_available_types()}")
    
    # Test: load BJJ config
    try:
        bjj_config = load_config("bjj")
        print(f"\nBJJ Config sections: {get_section_headers(bjj_config)}")
        print(f"BJJ domains: {list(get_domain_dictionary(bjj_config).keys())}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
