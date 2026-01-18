# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lockin is a macOS-only terminal-based focus timer with a persistent background engine. It uses a **persistent engine + ephemeral CLI** architecture where the engine runs as a macOS LaunchAgent and the CLI can attach/detach without losing session state.

## Development Commands

```bash
# Development setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run engine locally (Terminal 1)
./dev-engine.sh

# Use CLI (Terminal 2)
source .venv/bin/activate
lockin 30                    # Start 30-min session
lockin                       # Attach to running session

# Run tests
pytest tests/ -v
pytest tests/test_database.py::test_session_logging -v  # Single test
pytest --cov=lockin tests/   # With coverage

# Full integration test
python final_verification.py
```

## Architecture

### Core Pattern: Database as Message Bus

The CLI and engine communicate through SQLite - the CLI queues commands, the engine polls and processes them. Both poll the shared `engine_state` table for current state.

```
CLI → (queue command) → SQLite → (poll/process) → Engine
CLI ← (poll state)    ← SQLite ← (update state) ← Engine
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `cli.py` | Rich-based terminal UI, keyboard input, state polling (1 Hz) |
| `engine.py` | State machine, timer logic, notifications, runs as LaunchAgent |
| `database.py` | SQLite layer with 4 tables: `sessions`, `config`, `engine_state`, `commands` |
| `config.py` | Configuration with defaults and validation |
| `__main__.py` | CLI entry point, argument parsing, command routing |

### State Machine

```
IDLE → RUNNING → AWAITING_DECISION → RUNNING_BONUS → ENDED
                        ↓
                      ENDED
```

- `AWAITING_DECISION`: Work session complete, waiting for user choice (quit/continue/break)
- `RUNNING_BONUS`: Extended time beyond planned duration
- Decision window auto-continues to bonus after 3 minutes

### Key Constraints

- **Single session enforced**: `engine_state` table has `CHECK (id = 1)` constraint
- **macOS only**: Uses LaunchAgent (`~/Library/LaunchAgents/com.lockin.engine.plist`) and osascript for notifications
- **Data location**: `~/.lockin/` contains `lockin.db`, `venv/`, and logs

## Extending the Code

**New command**: Add parsing in `__main__.py` → UI method in `cli.py` → engine handler in `engine.py`

**New config option**: Add to `DEFAULT_CONFIG` in `config.py` → add property accessor

**New session state**: Update `SessionState` enum in `engine.py` → update `Engine.tick()` transitions → update `cli.py` rendering

## Debugging

```bash
# Check if engine is running
launchctl list | grep lockin

# View logs
tail -f ~/.lockin/engine.log
tail -f ~/.lockin/engine.error.log

# Inspect database
sqlite3 ~/.lockin/lockin.db ".schema"
sqlite3 ~/.lockin/lockin.db "SELECT * FROM engine_state;"
```

## Commit Message Format

```
[component] Brief description
```

Components: `[engine]`, `[cli]`, `[database]`, `[config]`
