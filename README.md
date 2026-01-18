# 🔒 Lockin

> A bulletproof macOS terminal focus timer that actually works.

**Lockin** helps you maintain deep focus through structured work sessions and intelligent breaks. Unlike browser-based timers, Lockin runs as a native background process—your sessions survive terminal closures, system sleeps, and accidental quits.

**Note** Almost this entire repo is AI generated and is a work in progress. Expect slop-like problems for now. Things will improve.

```bash
lockin 30                    # Start 30-minute focus session
lockin                       # Beautiful live UI
lockin stats week            # Track your progress
```

Built for developers, writers, and anyone who needs uninterrupted focus time.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]() [![Python](https://img.shields.io/badge/python-3.9+-blue)]() [![License](https://img.shields.io/badge/license-MIT-blue)]()

**→ [See Terminal Output Examples](TERMINAL_EXAMPLES.md)** - Visual tour of the UI

## Why Lockin?

**Traditional timers fail when you need them most:**

- 🔴 Browser tabs get closed
- 🔴 Web apps lose state on refresh
- 🔴 Phone apps aren't with you at your desk
- 🔴 No terminal keeps you in flow

**Lockin is different:**

- ✅ **Persistent** - Runs as macOS background service
- ✅ **Terminal-native** - Stays in your development environment
- ✅ **Resilient** - Survives terminal closures, system sleep, network issues
- ✅ **Streak tracking** - Motivational without being stressful
- ✅ **Smart breaks** - Automatically recommends short vs. long breaks
- ✅ **Beautiful stats** - Rich terminal UI with progress bars and charts

## Quick Start

### Installation

```bash
cd lockin
./install.sh
```

That's it. The installer:

- Creates a dedicated Python environment
- Installs Lockin and dependencies
- Sets up the background engine as a LaunchAgent
- Adds `lockin` to your PATH

Restart your terminal or run:

```bash
source ~/.zshrc  # or ~/.bashrc
```

### First Session

```bash
# Start a 30-minute work session
lockin 30

# Attach to see live progress
lockin
```

**During the session:**

- Press `d` to detach (session continues)
- Press `q` to end early
- When time's up, choose your next move

### Your First Week

```bash
# Day 1: Single session
lockin 25                      # 25-minute pomodoro
# Press 'b' when done for automatic break

# Day 2: Longer focus block
lockin 90                      # 90-minute deep work

# Day 3: Check your progress
lockin stats week              # See your focused time
```

## Core Concepts

### Sessions

Two types: **work** and **break**

```bash
lockin 30              # 30-minute work session
lockin break short     # Short break (default: 5 min)
lockin break long      # Long break (default: 15 min)
lockin break 10        # Custom 10-minute break
```

### Session Lifecycle

```
   START             PLANNED END        DECISION          CHOICE
     │                    │                │                │
     ▼                    ▼                ▼                ▼
  ┌──────┐            ┌──────┐        ┌──────────┐     ┌──────┐
  │IDLE  │───start───▶│RUNNING│───────▶│ AWAITING │─quit▶│ENDED │
  └──────┘            └──────┘         │ DECISION │     └──────┘
      ▲                  │              └──────────┘
      │                  │                    │
      │                  │              continue
      │                  │                    │
      │                  │                    ▼
      │                  │              ┌──────────┐
      │                  │              │  BONUS   │
      │                  │              │   TIME   │
      │                  │              └──────────┘
      │                  │                    │
      │                  │                  quit
      │                  │                    │
      │                quit                   │
      │                  │                    │
      │                  ▼                    ▼
      │              ┌──────┐            ┌──────┐
      └──────────────│ENDED │◀───────────│ENDED │
                     └──────┘            └──────┘
```

**Key points:**

- Quitting is **always final** - you can't enter bonus time after quitting
- After planned time ends, you enter a decision window
- From decision window: quit (final) OR continue to bonus time
- From bonus time: quit when ready (final)

### Streaks

Your **streak** counts consecutive completed work sessions:

```
Session 1 (completed) ──[15 min gap]──▶ Session 2 (completed) ──[30 min gap]──▶ Session 3 (completed)
                                                                                   Streak: 3 ✨
```

**Streak continues if:**

- Sessions are < 1 hour apart
- Within the same day

**Streak resets if:**

- Gap ≥ 1 hour between sessions
- Midnight passes

**Streak NOT affected by:**

- Abandoned sessions
- Taking breaks
- Going into bonus time

### Smart Breaks

Lockin recommends breaks based on your streak:

```
Session 1 → "Take a short break" (5 min)
Session 2 → "Take a short break" (5 min)
Session 3 → "Take a short break" (5 min)
Session 4 → "Take a long break" (15 min)  ← Every 4th session
Session 5 → "Take a short break" (5 min)
```

Configurable via `lockin config long_break_every 4`

## Commands

### Starting Sessions

```bash
# Work sessions
lockin 25              # 25-minute focus session
lockin 45              # 45-minute focus session
lockin 90              # 90-minute deep work

# Breaks
lockin break short     # Short break (from config)
lockin break long      # Long break (from config)
lockin break 10        # Custom 10-minute break

# End session without attaching
lockin quit            # or: lockin stop
```

### Viewing & Tracking

```bash
# Show dashboard or attach to running session
lockin

# Statistics
lockin stats week                # This week
lockin stats month               # This month
lockin stats year                # This year
lockin stats week 150124         # Specific week (DDMMYY)
lockin stats month 010124        # Specific month
lockin stats year 2024           # Specific year
```

### Configuration

```bash
# View all settings
lockin config

# Change a setting
lockin config short_break_minutes 5
lockin config long_break_minutes 15
lockin config long_break_every 4

# Reset to defaults
lockin config reset
```

## Interactive Controls

When attached to a running session, use these keys:

### During Work Session (Before Completion)

| Key | Action |
|-----|--------|
| `q` | Quit session (ends early) |
| `d` | Detach UI (session continues in background) |

### After Session Completes (Decision Window)

| Key | Action |
|-----|--------|
| `q` | End session |
| `b` | Take recommended break (short or long) |
| `B` | Prompt for custom break duration |
| `c` | Continue into bonus time |
| `d` | Detach UI |
| *wait* | Auto-continues after 3 minutes |

### During Bonus time

| Key | Action |
|-----|--------|
| `q` | End session |
| `b` | Take recommended break |
| `B` | Custom break duration |
| `d` | Detach UI |

### During Break

| Key | Action |
|-----|--------|
| `q` | End break early |
| `s` | Switch to short break (if before short duration) |
| `l` | Switch to long break (if before long duration) |
| `d` | Detach UI |

## Configuration Reference

| Setting | Default | Description | Range |
|---------|---------|-------------|-------|
| `short_break_minutes` | 5 | Duration of short breaks | 1-1440 |
| `long_break_minutes` | 15 | Duration of long breaks | 1-1440 |
| `long_break_every` | 4 | Recommend long break every N sessions | 1-100 |
| `abandon_threshold_minutes` | 5 | Minimum time to log abandoned work sessions | 1-1440 |
| `break_scrap_threshold_minutes` | 2 | Minimum time to log breaks | 1-1440 |
| `decision_window_minutes` | 3 | Time to decide after session completes | 1-1440 |
| `auto_attach` | false | Automatically attach to session after starting | true/false |

**Examples:**

```bash
# Customize your pomodoro setup
lockin config short_break_minutes 5
lockin config long_break_minutes 20
lockin config long_break_every 3

# Be more forgiving with incomplete sessions
lockin config abandon_threshold_minutes 10

# Longer decision window
lockin config decision_window_minutes 5

# Automatically show the session UI when starting
lockin config auto_attach true
```

## Example Workflows

### Classic Pomodoro (25/5)

```bash
lockin config short_break_minutes 5
lockin config long_break_minutes 15
lockin config long_break_every 4

# Then
lockin 25              # Work
# Press 'b' → automatic 5-min break
# Repeat 4 times → automatic 15-min break
```

### Deep Work Blocks

```bash
lockin 90              # 90-minute focus session
# Let it complete or go into bonus time
lockin break long      # Substantial break afterward
```

### Time Blocking Your Day

```bash
# Morning: emails & admin
lockin 30

# Mid-morning: deep work
lockin 90

# Check progress
lockin stats week

# Afternoon: meetings & collaboration
# (no timer needed)

# Late afternoon: another focus block
lockin 60
```

## Understanding Statistics

### Weekly Stats View

```
┌─────────────────────────────────────┐
│ LOCKIN — Stats: Week of Dec 18, 2024 │
└─────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Focused (completed) │ 18h 30m │
│ Break time          │  1h 45m │
│ Completed sessions  │     37 │
└─────────────────────┴────────┘

Daily breakdown:

Mon 18    3h 30m (7 sessions)  ██████████████████
Tue 19    4h 15m (8 sessions)  ████████████████████████
Wed 20    2h 45m (6 sessions)  ██████████████
Thu 21    3h 30m (7 sessions)  ██████████████████
Fri 22    4h 30m (9 sessions)  ████████████████████████████
Sat 23     —
Sun 24     —
```

**Metrics:**

- **Focused (completed)** - Time in completed work sessions only
- **Break time** - Total break time
- **Completed sessions** - Sessions that reached their planned duration
- **Abandoned sessions** - Sessions quit early (but after threshold)

## Architecture

Lockin is designed for reliability and persistence:

```
┌─────────────────────────────────────┐
│         Terminal (You)              │
│  ┌──────────────────────────────┐  │
│  │   CLI (ephemeral)             │  │
│  │   • Command parsing           │  │
│  │   • Rich UI                   │  │
│  │   • Keyboard input            │  │
│  └──────┬───────────────┬────────┘  │
└─────────┼───────────────┼───────────┘
          │               │
    Queue │               │ Poll
   Command│               │ State
          │               │
   ┌──────▼───────────────▼──────┐
   │   SQLite Database           │
   │   (Single source of truth)  │
   └──────┬───────────────┬──────┘
          │               │
   Process│               │Update
   Command│               │State
          │               │
   ┌──────▼───────────────▼──────┐
   │   Engine (persistent)       │
   │   • LaunchAgent             │
   │   • Timer management        │
   │   • Notifications           │
   │   • State machine           │
   └─────────────────────────────┘
```

**Key Design Decisions:**

1. **SQLite for Communication** - Simple, reliable, transactional
2. **Engine as LaunchAgent** - True background persistence
3. **Command Queue Pattern** - Decouples CLI from engine
4. **State Machine** - Predictable, testable transitions

## Troubleshooting

### Engine Not Running

**Symptom:** `Warning: Lockin engine not running`

**Fix:**

```bash
# Check if engine is running
launchctl list | grep lockin

# If not running, start it
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# Or start manually for debugging
lockin-engine
```

### Session Not Starting

**Check logs:**

```bash
tail -f ~/.lockin/engine.log
tail -f ~/.lockin/engine.error.log
```

**Common issues:**

- Database permissions: `chmod 644 ~/.lockin/lockin.db`
- Conflicting session already running
- Engine crashed (restart it)

### Stats Not Showing

**Ensure database has data:**

```bash
sqlite3 ~/.lockin/lockin.db "SELECT COUNT(*) FROM sessions;"
```

**Should return a number > 0**

### Notifications Not Appearing

1. Check macOS Notification settings
2. Ensure Terminal/iTerm2 has notification permissions
3. Test manually:

   ```bash
   osascript -e 'display notification "Test" with title "Lockin"'
   ```

### Complete Reset

```bash
# Stop engine
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist

# Backup data (optional)
cp ~/.lockin/lockin.db ~/lockin-backup.db

# Remove all data
rm -rf ~/.lockin

# Reinstall
cd lockin
./install.sh
```

## Uninstallation

```bash
./uninstall.sh
```

You'll be asked whether to preserve your session history.

## Advanced Usage

### Manual Engine Control

```bash
# Stop engine
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist

# Start engine
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# Run engine in foreground (for debugging)
lockin-engine
```

### Database Inspection

```bash
# Open database
sqlite3 ~/.lockin/lockin.db

# View sessions
SELECT datetime(start_time, 'unixepoch', 'localtime') as start,
       session_type,
       state,
       actual_duration_minutes
FROM sessions
ORDER BY start_time DESC
LIMIT 10;

# View config
SELECT * FROM config;
```

### Export Data

```bash
# Export sessions to CSV
sqlite3 -header -csv ~/.lockin/lockin.db \
  "SELECT * FROM sessions" > ~/lockin-sessions.csv
```

## Development

Want to contribute? See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Project structure
- Testing guide
- Pull request guidelines

Quick start for developers:

```bash
# Clone and setup
git clone <repository>
cd lockin
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run engine locally
./dev-engine.sh
```

## FAQ

**Q: Does Lockin sync across devices?**  
A: No, Lockin is local-only by design. This ensures privacy and reliability.

**Q: Can I pause a session?**  
A: Not really—the philosophy is to commit to focus blocks. But you can quit early and restart.

**Q: What happens if my computer sleeps?**  
A: The engine handles sleep/wake gracefully. Time doesn't advance while asleep.

**Q: Can I run multiple sessions?**  
A: No, Lockin enforces one global session to prevent conflicts and maintain clarity.

**Q: How accurate is the timing?**  
A: Very accurate. The engine ticks every second and uses Unix timestamps for precision.

**Q: What if I accidentally quit a session?**  
A: Sessions shorter than `abandon_threshold_minutes` (default: 5) aren't logged, so quick mistakes don't affect stats.

**Q: Can I customize the UI colors?**  
A: Not yet, but the code uses Rich library which supports theming. PRs welcome!

**Q: Does this work on Linux/Windows?**  
A: Currently macOS only due to LaunchAgent and notification systems. Linux/Windows support could be added.

## Technical Details

- **Language:** Python 3.9+
- **Database:** SQLite 3
- **UI:** Rich library
- **Background Service:** macOS LaunchAgent
- **Notifications:** osascript (AppleScript)
- **Tests:** pytest

## Inspiration & Philosophy

Lockin is inspired by:

- **Pomodoro Technique** - Structured focus periods
- **Deep Work** (Cal Newport) - Uninterrupted concentration
- **Unix Philosophy** - Do one thing well
- **Terminal-first tools** - Stay in flow, minimize context switching

Design principles:

- **Reliable over fancy** - Core functionality must never fail
- **Respectful of attention** - No gamification, no manipulation
- **Transparent** - Clear data storage, no hidden behavior  
- **Minimal** - No feature bloat, no scope creep

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Inspired by countless pomodoro timers that almost worked
- Thanks to the Python and open source communities

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/lockin/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/lockin/discussions)
- **Email:** <support@lockin.dev>

---

**Made with focus.** 🔒
