# Lockin

A terminal focus timer that doesn't die when you close the terminal.

```
╭────────────────────╮
│ LOCKIN — work      │
╰────────────────────╯

17:42 remaining

████████████████░░░░░░░░░░░░░░░░░░░░░░░░

Started: 09:15
Planned: 30 min
Elapsed: 12:18

Today: 2h 15m focused · 4 sessions · streak 3

[q] quit   [d] detach
```

```
╭──────────────────────────────────╮
│ LOCKIN — Stats: Week of Jan 13   │
╰──────────────────────────────────╯

╭─────────────────────┬─────────╮
│ Metric              │   Value │
├─────────────────────┼─────────┤
│ Focused (completed) │  8h 30m │
│ Break time          │  1h 45m │
│ Completed sessions  │      17 │
╰─────────────────────┴─────────╯

Daily breakdown:

Mon 13       1h 30m ( 3 sessions)  ████████████
Tue 14       2h  0m ( 4 sessions)  ████████████████
Wed 15       1h 45m ( 4 sessions)  ██████████████
Thu 16       1h 30m ( 3 sessions)  ████████████
Fri 17       1h 45m ( 3 sessions)  ██████████████
Sat 18            —
Sun 19            —
```

Start a focus session, close your terminal, open a new one, run `lockin` — your timer is still running. Lockin uses a background engine that persists through terminal sessions, SSH disconnects, and accidental `Ctrl+C`.

**Why Lockin?**
- Sessions survive terminal close (background engine via LaunchAgent)
- Detach mid-session with `d`, reattach anytime with `lockin`
- Tracks focus time with daily, weekly, and monthly stats
- Pomodoro-inspired break system: short breaks by default, long break every N sessions (configurable)
- macOS native notifications when sessions complete

## Quick Start

```bash
./install.sh               # Install (restart terminal after)

lockin 30                   # Start 30-minute focus session
lockin                      # Attach to running session
lockin stats week           # View weekly stats
```

## Installation

```bash
./install.sh
```

Restart your terminal or `source ~/.zshrc`.

## Usage

### Sessions

```bash
# Work sessions
lockin 25              # 25-minute focus
lockin 90              # 90-minute deep work

# Breaks
lockin break short     # Short break (5 min default)
lockin break long      # Long break (15 min default)
lockin break 10        # Custom 10-minute break

# End session
lockin quit            # End if past threshold
lockin quit --scrap    # Force end regardless of time
```

### Interactive Controls

**During session:**
| Key | Action |
|-----|--------|
| `q` | Quit session |
| `d` | Detach (session continues in background) |

**After session completes:**
| Key | Action |
|-----|--------|
| `q` | End session |
| `b` | Take recommended break |
| `B` | Custom break duration |
| `c` | Continue into bonus time |

**During break:**
| Key | Action |
|-----|--------|
| `q` | End break |
| `s` | Switch to short break |
| `l` | Switch to long break |

### Statistics

```bash
lockin stats week      # This week
lockin stats month     # This month
lockin stats year      # This year
```

### Session Log

```bash
lockin log             # Show 10 most recent sessions
lockin log 20          # Show 20 most recent sessions
lockin log --work      # Show only work sessions
lockin log --break     # Show only break sessions
lockin log 5 --work    # Show 5 most recent work sessions
```

### Deleting Sessions

```bash
lockin delete 1        # Delete most recent session
lockin delete 3        # Delete 3rd most recent session
```

The position number corresponds to the `#` column in `lockin log`. Deletion always uses the unfiltered log (ignores `--work`/`--break` filters). You'll be asked to confirm before deletion.

**Note:** After deleting a session, the position numbers shift—what was #3 becomes #2, etc.

### Configuration

```bash
lockin config                        # View settings
lockin config short_break_minutes 5  # Change setting
lockin config reset                  # Reset to defaults
```

| Setting | Default | Description |
|---------|---------|-------------|
| `short_break_minutes` | 5 | Short break duration |
| `long_break_minutes` | 15 | Long break duration |
| `long_break_every` | 4 | Long break every N sessions |
| `abandon_threshold_minutes` | 5 | Min time to log work sessions |
| `break_scrap_threshold_minutes` | 2 | Min time to log breaks |
| `decision_window_minutes` | 3 | Time to decide after completion |
| `auto_attach` | false | Auto-attach after starting session |
| `default_to_overtime` | true | Enter overtime mode when session ends |
| `overtime_max_minutes` | 60 | Max overtime before auto-end (0=unlimited) |

### Overtime Behavior

When a work session's planned time ends, you enter a decision window where you can quit, take a break, or continue working. If you don't decide within `decision_window_minutes`, the session automatically continues into "overtime" (bonus time).

- **`default_to_overtime`**: Set to `false` to skip overtime entirely—sessions end and log automatically when time is up.
- **`overtime_max_minutes`**: Caps how long overtime can last. After this, the session auto-ends. Set to `0` for unlimited overtime.

## How It Works

Lockin uses a persistent background engine (macOS LaunchAgent) that keeps running even when you close your terminal. The CLI communicates with the engine through SQLite.

```
CLI ──queue command──▶ SQLite ◀──process──Engine (background)
CLI ◀──poll state───── SQLite ◀──update─── Engine
```

## Troubleshooting

### macOS Security Warnings

macOS may flag Lockin because it installs a LaunchAgent (background process). This is expected behavior for a persistent timer.

**"Cannot be opened because it is from an unidentified developer"** or similar:
```bash
# Remove quarantine flag from downloaded files
xattr -r -d com.apple.quarantine install.sh uninstall.sh
```

**Corporate security software (CrowdStrike, etc.):**
- The LaunchAgent at `~/Library/LaunchAgents/com.lockin.engine.plist` may be flagged
- The Python process running from `~/.lockin/venv/` may be flagged
- You may need to request an exception from IT, or run the engine manually instead:
  ```bash
  # Skip LaunchAgent, run engine in a terminal tab instead
  lockin-engine
  ```

### General

```bash
# Check if engine is running
launchctl list | grep lockin

# Start engine manually (if LaunchAgent isn't working)
lockin-engine

# View logs
tail -f ~/.lockin/engine.log

# Complete reset
./uninstall.sh && ./install.sh
```

## Uninstall

```bash
./uninstall.sh
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

```bash
uv pip install -e ".[dev]"
uv run pytest tests/ -v
```

## Project Status

For a detailed assessment of the project (features, limitations, known issues) and a prioritized roadmap, see [docs/report.md](docs/report.md).

## License

MIT - see [LICENSE](LICENSE)
