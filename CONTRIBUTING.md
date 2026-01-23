# Contributing to Voice Notes

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/dollythedog/voice-notes.git
cd voice-notes
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Testing Changes

Before submitting changes:

1. Run the test suite:
```bash
./test_pipeline.sh
```

2. Test with a sample audio file:
```bash
cp test_audio.wav inboxes/meeting/
./service_control.sh logs
```

3. Verify code formatting (PEP 8):
```bash
# If you have black installed
black --check *.py

# If you have flake8 installed
flake8 *.py
```

## Submitting Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit with descriptive messages:
```bash
git commit -m "feat: add new feature

- Detailed description of what changed
- Why the change was necessary

Co-Authored-By: Your Name <your.email@example.com>"
```

3. Push your branch and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Commit Message Guidelines

Follow conventional commits format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Handle errors with appropriate logging

## Adding New Note Types

1. Create configuration file: `configs/types/newtype.json`
2. Add domain dictionary and Logseq page configuration
3. Create inbox folder: `mkdir -p inboxes/newtype`
4. Create archive folders: `mkdir -p archive/newtype/{done,failed}`
5. Update WARP.md with new type documentation
6. Test with sample audio file

## Questions or Issues?

- Check existing documentation in the repository
- Review WARP.md for project-specific guidelines
- Open an issue for bugs or feature requests
