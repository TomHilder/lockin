# Lockin User Guide

Complete guide to using Lockin effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Best Practices](#best-practices)
5. [Customization](#customization)
6. [Tips & Tricks](#tips--tricks)

## Getting Started

### First Time Setup

After installation, Lockin is ready to use immediately:

```bash
# Verify installation
lockin config

# Start your first session
lockin 25
```

### Understanding the Dashboard

When you run `lockin` with no session active, you see the idle dashboard:

```
┌──────────────┐
│ LOCKIN — idle│
└──────────────┘

Last session:
  Work — 42 min (completed) — today 18:12

Today:
  Focused: 3h 10m
  Breaks: 40m
  Sessions: 5

Next:
  lockin 30
  lockin break
  lockin stats
```

This shows:
- **Last session** - Your most recent activity
- **Today's stats** - Your progress so far
- **Next steps** - Quick commands to continue

### Your First Session

**1. Start a session:**
```bash
lockin 30
```

**2. Attach to see progress:**
```bash
lockin
```

You'll see:
```
┌────────────┐
│ LOCKIN — work│
└────────────┘

25:14 remaining
████████████████████▍

Started: 10:05
Planned: 30 min
Elapsed: 04:46

Today: 3h 10m focused · 5 sessions · streak 3

[q] quit (end early)   [d] detach
```

**3. When time's up:**

You'll get a notification and see:

```
04:12 remaining
█████████▌

[q] quit (end)   [b/B] break (short/custom)   [c] continue   [d] detach
Defaulting to continue in 1:37
```

Choose your action:
- `q` - End the session
- `b` - Take a recommended break
- `B` - Specify custom break duration
- `c` - Continue working (bonus time)
- `d` - Detach (decision window continues)
- *Wait* - Automatically continues after 3 minutes

## Basic Usage

### Starting Work Sessions

The most common command:

```bash
lockin <minutes>
```

**Common durations:**
```bash
lockin 25          # Pomodoro (25 min)
lockin 30          # Half hour
lockin 45          # Three quarters
lockin 60          # One hour
lockin 90          # Deep work block
```

**Limits:**
- Minimum: 1 minute
- Maximum: 1440 minutes (24 hours)

### Taking Breaks

**Predefined breaks:**
```bash
lockin break short     # Uses config value (default: 5 min)
lockin break long      # Uses config value (default: 15 min)
```

**Custom breaks:**
```bash
lockin break 3         # 3-minute break
lockin break 10        # 10-minute break
lockin break 20        # 20-minute break
```

**Break philosophy:**
Lockin recommends breaks based on your streak. After 4 completed sessions, it suggests a long break. Otherwise, short breaks.

### Viewing Statistics

**Basic stats:**
```bash
lockin stats week      # Current week
lockin stats month     # Current month
lockin stats year      # Current year
```

**Historical stats:**
```bash
lockin stats week 150124     # Week containing Jan 15, 2024
lockin stats month 010124    # January 2024
lockin stats year 2024       # All of 2024
```

**Date formats:**
- Week/Month: `DDMMYY` (e.g., `150124` for Jan 15, 2024)
- Year: `YYYY` (e.g., `2024`)

## Advanced Features

### Session Persistence

Sessions run in the background and survive:
- **Terminal closure** - Close all terminal windows, session continues
- **System sleep** - Close your laptop, time doesn't advance
- **Network issues** - No internet required
- **App crashes** - Engine restarts automatically (LaunchAgent)

**Test it:**
```bash
# Terminal 1
lockin 30

# Terminal 2 (or close and reopen)
lockin              # Attach to same session
```

### Bonus time

When a session completes, you enter a "decision window":

```
[q] quit (end)   [b/B] break (short/custom)   [c] continue   [d] detach
Defaulting to continue in 1:37
```

If you don't choose, you automatically continue into **bonus time**.

**Bonus time is:**
- Still counted as work time
- Marked as "completed" when you quit
- Shown separately in your stats
- Part of your streak

**Use bonus time when:**
- You're in deep flow
- Almost done with a task
- Want to finish a thought

### Break Switching

During a break, you can switch types:

**Rules:**
- Before short duration ends → Switch to either short or long
- After short duration ends → Can only switch to long
- After long duration ends → Break automatically ends

**Example:**
```bash
lockin break short    # Start 5-min break

# 3 minutes in...
[s] switch to short   # ✓ Available
[l] switch to long    # ✓ Available

# 6 minutes in...
[s] switch to short   # ✗ Too late
[l] switch to long    # ✓ Available

# 16 minutes in...
# Break automatically ends
```

### Streak Tracking

Your streak shows consecutive completed sessions:

**Streak increments:**
```
Session 1 (10:00-10:30) [completed]
   ↓ 20 min gap
Session 2 (10:50-11:20) [completed]  ← Streak: 2
   ↓ 25 min gap
Session 3 (11:45-12:15) [completed]  ← Streak: 3
```

**Streak resets:**
```
Session 3 (12:15 ends)
   ↓ 65 min gap (> 60 min)
Session 4 (13:20-13:50) [completed]  ← Streak: 1 (reset)
```

**Streak NOT affected by:**
- Abandoned sessions (quit early)
- Break time (doesn't count toward gap)
- Bonus time

**Streak DOES reset:**
- Gap ≥ 60 minutes between completed sessions
- At midnight (new day = new streak)

### Command Queue

When the engine isn't running, commands queue up:

```bash
# Engine stopped
lockin 30              # Queues: "start_session"

# Engine starts
# → Processes queued command
# → Session starts automatically
```

This ensures you never lose a command due to timing issues.

## Best Practices

### Choosing Session Lengths

**25 minutes (Pomodoro)**
- ✅ Good for: Tasks with clear stopping points
- ✅ Good for: Maintaining energy all day
- ✅ Good for: Building the habit
- ❌ Not ideal for: Deep technical work

**45-60 minutes**
- ✅ Good for: Writing, coding, reading
- ✅ Good for: Getting into flow
- ❌ Not ideal for: Repetitive tasks

**90 minutes (Deep Work)**
- ✅ Good for: Complex problem-solving
- ✅ Good for: Creative work
- ✅ Good for: Learning new concepts
- ❌ Not ideal for: Afternoon sessions (fatigue)

### Break Strategy

**Take breaks even if you feel fine:**
- Short breaks (5 min) - Physically move, look away from screen
- Long breaks (15 min) - Walk, eat, genuine rest

**During breaks:**
- ✅ Stand up, walk around
- ✅ Look at distant objects (eye relief)
- ✅ Hydrate
- ✅ Light stretching
- ❌ Check email/social media (not real rest)
- ❌ Start another task

### Tracking Effectiveness

**Use stats to find your rhythm:**

```bash
# Check your week
lockin stats week

# Look for patterns:
# - Which days are most productive?
# - What session length works best?
# - How many sessions until fatigue?
```

**Adjust based on data:**
- Too many abandoned sessions? → Shorter durations
- High streaks? → You've found your rhythm
- Uneven daily totals? → Schedule focus blocks

### Building the Habit

**Week 1: Consistency over duration**
```bash
# Just do 2-3 sessions daily
lockin 25
lockin 25
```

**Week 2-3: Find your pattern**
```bash
# Experiment with timing
# Morning: 45 min
# Afternoon: 25 min
```

**Week 4+: Optimize**
```bash
# Use stats to refine
lockin stats month
# Adjust config based on data
```

## Customization

### Personalize Break Timing

```bash
# Shorter, more frequent breaks
lockin config short_break_minutes 3
lockin config long_break_minutes 10
lockin config long_break_every 3

# Longer, less frequent breaks
lockin config short_break_minutes 7
lockin config long_break_minutes 20
lockin config long_break_every 5
```

### Adjust Thresholds

**Abandon threshold** (when to log incomplete sessions):

```bash
# Default: 5 minutes
lockin config abandon_threshold_minutes 5

# More forgiving (log even shorter sessions):
lockin config abandon_threshold_minutes 2

# More strict (only log substantial work):
lockin config abandon_threshold_minutes 10
```

**Break scrap threshold** (minimum break time to log):

```bash
# Default: 2 minutes
lockin config break_scrap_threshold_minutes 2
```

### Decision Window

How long to decide what to do after a session:

```bash
# Default: 3 minutes
lockin config decision_window_minutes 3

# Faster decisions:
lockin config decision_window_minutes 1

# More time to decide:
lockin config decision_window_minutes 5
```

## Tips & Tricks

### Multiple Terminals

Lockin works great with multiple terminals:

**Terminal 1:** Long-running task
```bash
npm run build     # Long build process
```

**Terminal 2:** Focus timer
```bash
lockin 30         # Track your focus time
```

### Integration with Task Management

Use Lockin alongside your task tracker:

```bash
# Start Asana/Todoist timer
# Start Lockin
lockin 45

# Both track the time
```

### Time Blocking Your Calendar

**Morning routine:**
```bash
lockin 30         # Email & admin
lockin 90         # Deep work block 1
lockin stats      # Check progress
```

**Afternoon:**
```bash
lockin 60         # Post-lunch focused work
# Meetings (no timer)
lockin 45         # Final focus block
```

### Screen Time Comparison

Track both:
1. **Lockin** - Focused work time
2. **macOS Screen Time** - Total computer time

Gap = unfocused time. Use this to improve.

### Pomodoro with Lockin

Traditional Pomodoro (25/5/15):

```bash
# Configure
lockin config short_break_minutes 5
lockin config long_break_minutes 15
lockin config long_break_every 4

# Use
lockin 25     # Repeat, taking suggested breaks
```

### Keyboard Maestro Integration

Create shortcuts:

```applescript
-- "Start Focus" shortcut
tell application "Terminal"
    do script "lockin 45"
end tell
```

### Morning Ritual

```bash
#!/bin/bash
# ~/bin/morning-focus

echo "☀️ Morning Focus Session"
echo "========================"
echo ""
echo "Yesterday's stats:"
lockin stats week
echo ""
echo "Starting 90-minute deep work block..."
sleep 2
lockin 90
```

Then: `chmod +x ~/bin/morning-focus && morning-focus`

### End of Day Review

```bash
#!/bin/bash
# ~/bin/day-review

echo "📊 Today's Focus Report"
echo "======================"
echo ""
lockin stats week | tail -n 8
echo ""
echo "Tomorrow:"
echo "  • Morning: 90-min deep work"
echo "  • Afternoon: 2x 45-min blocks"
```

### Export for Other Tools

```bash
# Export sessions to CSV
sqlite3 -header -csv ~/.lockin/lockin.db \
  "SELECT 
    datetime(start_time, 'unixepoch', 'localtime') as start,
    datetime(end_time, 'unixepoch', 'localtime') as end,
    session_type,
    actual_duration_minutes,
    state
   FROM sessions
   WHERE date(start_time, 'unixepoch', 'localtime') = date('now', 'localtime')" \
  > today.csv
```

### Debugging Sessions

```bash
# Watch engine in real-time
tail -f ~/.lockin/engine.log

# Check database directly
sqlite3 ~/.lockin/lockin.db "SELECT * FROM engine_state;"
```

### Reset Mid-Day

If you want a fresh start:

```bash
# This doesn't delete history
# Just ends current session
lockin
# Press 'q'
```

Your streak and stats are preserved.

## Common Workflows

### Writer's Block Breaker

```bash
lockin 15      # Short sprint
# Write anything, no editing
# When done, take break
# Repeat 4 times
```

### Deep Technical Problem

```bash
lockin 90      # Long uninterrupted block
# No Slack, no email
# Just the problem
```

### Learning New Tech

```bash
lockin 45      # Tutorial/documentation
lockin break short
lockin 45      # Hands-on practice
lockin break short
lockin 30      # Build something
```

### Code Review Session

```bash
lockin 30      # Focus on quality
# No rushing
# Thoughtful feedback
```

### Debugging Marathon

```bash
lockin 60
# If not solved by end:
# Press 'c' for bonus time
# Stay in flow
```

## Troubleshooting Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed help.

**Quick fixes:**

```bash
# Session seems stuck
lockin          # Check actual state
# Press 'q' to force quit if needed

# Stats missing
sqlite3 ~/.lockin/lockin.db "SELECT COUNT(*) FROM sessions;"

# Engine not running
launchctl list | grep lockin
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how Lockin works
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to add features
- Join discussions about productivity techniques
- Share your workflow with the community

---

**Remember:** Lockin is a tool. The real work is building the habit of deep, focused work. Use Lockin to make that easier, not to obsess over numbers.

**Focus well.** 🔒
