# Contributing to Lockin

Thanks for your interest in improving Lockin! This guide will help you get started with development.

## Development Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd lockin
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install in development mode

```bash
pip install -e .
```

### 4. Install development dependencies

```bash
pip install -e ".[dev]"
```

## Running in Development

### Option 1: Use the development script

The easiest way to test changes:

```bash
./dev-engine.sh
```

This runs the engine in the foreground without installing as a LaunchAgent.

In another terminal:
```bash
source .venv/bin/activate
lockin 30        # Start session
lockin           # Attach to session
```

### Option 2: Manual testing

Terminal 1 - Run engine:
```bash
source .venv/bin/activate
python -m lockin.engine_main
```

Terminal 2 - Use CLI:
```bash
source .venv/bin/activate
lockin 30
```

## Project Structure

```
lockin/
├── src/lockin/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── database.py          # SQLite database layer
│   ├── config.py            # Configuration management
│   ├── engine.py            # Background engine logic
│   ├── engine_main.py       # Engine entry point
│   └── cli.py               # Terminal UI with Rich
├── tests/
│   └── test_database.py     # Unit tests
├── pyproject.toml           # Package configuration
├── README.md                # User documentation
├── CONTRIBUTING.md          # This file
├── install.sh               # Installation script
├── uninstall.sh             # Uninstallation script
├── dev-engine.sh            # Development mode script
└── com.lockin.engine.plist  # LaunchAgent template
```

## Architecture Overview

### Components

1. **Database (`database.py`)**
   - SQLite backend for all persistence
   - Session logging, config storage, state management
   - Command queue for CLI → Engine communication

2. **Config (`config.py`)**
   - Manages configuration with defaults
   - Validates config values
   - Property accessors for type safety

3. **Engine (`engine.py`)**
   - Background process managing all timing
   - State machine for session states
   - Processes commands from CLI
   - Sends macOS notifications
   - Runs continuously as LaunchAgent

4. **CLI (`cli.py`)**
   - Terminal UI using Rich library
   - Polls engine state every second
   - Queues commands via database
   - Handles keyboard input for interactions

5. **Main (`__main__.py`)**
   - CLI entry point
   - Parses commands
   - Routes to appropriate UI methods

### State Flow

```
idle → running → awaiting_decision → running_bonus time
                      ↓
                    ended
```

### Communication

```
CLI ──(queue command)──> Database ──(poll)──> Engine
CLI <──(poll state)───── Database <──(update)── Engine
```

## Testing

### Run tests

```bash
pytest tests/ -v
```

### Run specific test

```bash
pytest tests/test_database.py::test_session_logging -v
```

### Test coverage

```bash
pytest --cov=lockin tests/
```

## Code Style

- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and small
- Document complex logic with comments

## Adding Features

### New Configuration Options

1. Add to `DEFAULT_CONFIG` in `config.py`
2. Add property accessor if needed
3. Update README with new config option
4. Consider migration for existing databases

### New Commands

1. Add command parsing in `__main__.py`
2. Add UI method in `cli.py` if needed
3. Add engine handler in `engine.py` if needed
4. Update command queue processing
5. Document in README

### New Session States

1. Update `SessionState` enum in `engine.py`
2. Update state transition logic in `Engine.tick()`
3. Update UI rendering in `cli.py`
4. Add tests for new state

## Common Development Tasks

### Testing Database Changes

```python
from pathlib import Path
from lockin.database import Database

db = Database(Path('/tmp/test.db'))
# Test your changes...
```

### Testing UI Changes

```bash
# Start engine
./dev-engine.sh

# In another terminal, test UI
lockin 1  # Quick 1-minute session
lockin    # Attach and see UI
```

### Testing Notifications

```python
import subprocess

subprocess.run([
    'osascript', '-e',
    'display notification "Test" with title "Lockin Test"'
])
```

## Debugging

### View Engine State

```python
from pathlib import Path
from lockin.database import Database

db = Database(Path.home() / '.lockin' / 'lockin.db')
state = db.get_engine_state()
print(state)
```

### View Database Contents

```bash
sqlite3 ~/.lockin/lockin.db
> .schema
> SELECT * FROM sessions;
> SELECT * FROM engine_state;
```

### View Engine Logs

```bash
tail -f ~/.lockin/engine.log
tail -f ~/.lockin/engine.error.log
```

## Pull Request Guidelines

1. **Create an issue first** for significant changes
2. **Write tests** for new functionality
3. **Update documentation** (README, docstrings)
4. **Follow existing code style**
5. **Keep commits focused** - one logical change per commit
6. **Write clear commit messages**

### Commit Message Format

```
[component] Brief description

Longer explanation if needed. Wrap at 72 characters.

- Bullet points for multiple changes
- Reference issue numbers like #123
```

Examples:
```
[engine] Fix streak calculation across midnight

[cli] Add color coding for abandoned sessions

[database] Optimize session query performance
```

## Ideas for Contributions

### Easy
- Add more tests
- Improve error messages
- Add config validation
- Better progress bar animations

### Medium
- Export statistics to CSV
- Custom notification sounds
- Integration with calendar apps
- Dark/light theme support

### Hard
- Windows/Linux support
- Web dashboard
- Machine learning for optimal break timing
- Integration with other productivity tools

## Questions?

Feel free to open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
