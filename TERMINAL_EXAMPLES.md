# Lockin Terminal Output Examples

Visual examples of what you'll see when using Lockin.

## Table of Contents
- [First Time: Idle Dashboard](#idle-dashboard)
- [Starting a Session](#starting-a-session)
- [Active Session](#active-session)
- [Session Completion (Decision Window)](#decision-window)
- [Break Session](#break-session)
- [Statistics Views](#statistics)
- [Configuration](#configuration)
- [Error Messages](#error-messages)

---

## Idle Dashboard

When you run `lockin` with no active session:

```
┌──────────────┐
│ LOCKIN — idle│
└──────────────┘

Last session:
  Work — 30 min (completed) — today 14:23

Today:
  Focused: 2h 45m
  Breaks: 25m
  Sessions: 6

Next:
  lockin 30
  lockin break
  lockin stats
```

**First time (no sessions yet):**

```
┌──────────────┐
│ LOCKIN — idle│
└──────────────┘

No sessions yet today.

Next:
  lockin 30
  lockin break
  lockin stats
```

---

## Starting a Session

### Work Session

```bash
$ lockin 30
```

**Output:**
```
Started 30-minute work session
Attach with: lockin
```

### Break Session

```bash
$ lockin break short
```

**Output:**
```
Started 5-minute break
Attach with: lockin
```

---

## Active Session

### Work Session (Running)

When you attach with `lockin`:

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

25:14 remaining
████████████████████▍░░░░░░░░░░░░░░░░░░░

Started: 10:05
Planned: 30 min
Elapsed: 04:46

Today: 2h 45m focused · 6 sessions · streak 3

[q] quit (end early)   [d] detach
```

**Note:** If elapsed time is less than abandon threshold (default 5 min), shows `[q] quit (scrap)` instead of `[q] quit (end early)`.

**Colors:**
- Title: Cyan
- Time remaining: Green
- Progress bar: Cyan
- Stats: Dim gray
- Controls: Dim gray

### Early in Session (< 5 minutes)

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

27:30 remaining
███▌░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Started: 10:05
Planned: 30 min
Elapsed: 02:30

Today: 2h 45m focused · 6 sessions · streak 3

[q] quit (scrap)   [d] detach
```

**Shows "scrap" because session would not be logged if quit now.**

### Later in Session (More Progress)

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

05:30 remaining
████████████████████████████████░░░░░░░░

Started: 10:05
Planned: 30 min
Elapsed: 24:30

Today: 2h 45m focused · 6 sessions · streak 3

[q] quit (end early)   [d] detach
```

### Almost Complete

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

00:15 remaining
███████████████████████████████████████▌

Started: 10:05
Planned: 30 min
Elapsed: 29:45

Today: 2h 45m focused · 6 sessions · streak 3

[q] quit (end early)   [d] detach
```

---

## Decision Window

### After Session Completes (Recommending Short Break)

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

02:45 to decide
████████████████████████████████████████

Started: 10:05
Planned: 30 min
Elapsed: 30:00

Today: 3h 15m focused · 7 sessions · streak 4

[q] quit (end)   [b/B] break (short/custom)   [c] continue   [d] detach
Defaulting to continue in 2:45
```

**Colors:**
- Time to decide: Green
- Progress bar: Full cyan
- Countdown: Dim

### Recommending Long Break (After 4th Session)

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

02:30 to decide
████████████████████████████████████████

Started: 15:20
Planned: 45 min
Elapsed: 45:00

Today: 5h 30m focused · 8 sessions · streak 4

[q] quit (end)   [b/B] break (long/custom)   [c] continue   [d] detach
Defaulting to continue in 2:30
```

### Bonus time (Continued Working)

```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

+05:23 bonus time
████████████████████████████████████████

Started: 10:05
Planned: 30 min
Elapsed: 35:23

Today: 3h 20m focused · 7 sessions · streak 4

[q] quit (end)   [b/B] break (short/custom)   [d] detach
```

**Colors:**
- Bonus time: Yellow
- Progress bar: Full cyan

---

## Break Session

### Short Break (Running)

```
┌──────────────────┐
│ LOCKIN — break (short)│
└──────────────────┘

03:45 remaining
███████████████████████░░░░░░░░░░░░░░░░

Started: 11:00
Planned: 5 min
Elapsed: 01:15

Today: 3h 15m focused · 7 sessions · streak 4

[q] end break   [s] switch to short   [l] switch to long   [d] detach
```

### Long Break (Running)

```
┌──────────────────┐
│ LOCKIN — break (long)│
└──────────────────┘

12:30 remaining
████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Started: 11:30
Planned: 15 min
Elapsed: 02:30

Today: 3h 15m focused · 7 sessions · streak 4

[q] end break   [s] switch to short   [l] switch to long   [d] detach
```

### Custom Break

```
┌──────────────────┐
│ LOCKIN — break (10m)│
└──────────────────┘

07:15 remaining
████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░

Started: 14:00
Planned: 10 min
Elapsed: 02:45

Today: 4h 30m focused · 9 sessions · streak 5

[q] end break   [s] switch to short   [l] switch to long   [d] detach
```

---

## Statistics

### Weekly Stats

```bash
$ lockin stats week
```

**Output:**
```
┌─────────────────────────────────────┐
│ LOCKIN — Stats: Week of Jan 08, 2024 │
└─────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Focused (completed) │ 18h 30m│
│ Break time          │  1h 45m│
│ Completed sessions  │     37 │
└─────────────────────┴────────┘

Daily breakdown:

Mon 08    3h 30m (7 sessions)  ██████████████████
Tue 09    4h 15m (8 sessions)  ████████████████████████
Wed 10    2h 45m (6 sessions)  ██████████████
Thu 11    3h 30m (7 sessions)  ██████████████████
Fri 12    4h 30m (9 sessions)  ████████████████████████████
Sat 13     —
Sun 14     —
```

**Colors:**
- Title: Cyan
- Table borders: Cyan
- Metrics: Bold
- Bar charts: Cyan
- Days with no sessions: Dim

### Monthly Stats

```bash
$ lockin stats month
```

**Output:**
```
┌──────────────────────────┐
│ LOCKIN — Stats: January 2024│
└──────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Focused (completed) │  72h 15m│
│ Focused (abandoned) │   3h 20m│
│ Break time          │   6h 30m│
│ Completed sessions  │    145 │
│ Abandoned sessions  │      8 │
└─────────────────────┴────────┘

Weekly breakdown:

Jan 01-07     18h 45m (38 sessions)  ████████████████████████
Jan 08-14     20h 30m (42 sessions)  ███████████████████████████
Jan 15-21     16h 15m (32 sessions)  ████████████████████
Jan 22-28     16h 45m (33 sessions)  █████████████████████
```

### Yearly Stats

```bash
$ lockin stats year
```

**Output:**
```
┌─────────────────┐
│ LOCKIN — Stats: 2024│
└─────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Focused (completed) │   842h │
│ Focused (abandoned) │    38h │
│ Break time          │    76h │
│ Completed sessions  │  1,684 │
│ Abandoned sessions  │     92 │
└─────────────────────┴────────┘
```

### Empty Stats (No Sessions Yet)

```bash
$ lockin stats week
```

**Output:**
```
┌─────────────────────────────────────┐
│ LOCKIN — Stats: Week of Jan 15, 2024 │
└─────────────────────────────────────┘

No sessions in this period
```

---

## Configuration

### View All Config

```bash
$ lockin config
```

**Output:**
```
┌──────────────────────┐
│ LOCKIN — Configuration│
└──────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Setting                     ┃ Value ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ abandon_threshold_minutes   │     5 │
│ break_scrap_threshold_min.. │     2 │
│ decision_window_minutes     │     3 │
│ long_break_every            │     4 │
│ long_break_minutes          │    15 │
│ short_break_minutes         │     5 │
└─────────────────────────────┴───────┘

To change: lockin config <key> <value>
To reset: lockin config reset
```

### Change Setting

```bash
$ lockin config short_break_minutes 7
```

**Output:**
```
Set short_break_minutes = 7
```

### Reset Config

```bash
$ lockin config reset
```

**Output:**
```
Configuration reset to defaults
```

---

## Error Messages

### Invalid Duration (Zero)

```bash
$ lockin 0
```

**Output:**
```
Duration must be positive
```

**Colors:** Red

### Invalid Duration (Too Long)

```bash
$ lockin 2000
```

**Output:**
```
Duration cannot exceed 24 hours (1440 minutes)
```

**Colors:** Red

### Session Already Running

```bash
$ lockin 30
```

**Output:**
```
A session is already running
Quit it first with q in the session view
```

**Colors:** Yellow/Warning

### Engine Not Running

```bash
$ lockin 30
```

**Output:**
```
Warning: Lockin engine not running
Start the engine with: lockin-engine
Or install as LaunchAgent for automatic startup

Started 30-minute work session
Attach with: lockin
```

**Colors:** 
- Warning: Yellow
- Commands: Cyan

### Invalid Config Key

```bash
$ lockin config invalid_key 5
```

**Output:**
```
Error: Unknown configuration key: invalid_key
Valid keys: abandon_threshold_minutes, break_scrap_threshold_minutes, decision_window_minutes, long_break_every, long_break_minutes, short_break_minutes
```

**Colors:**
- Error: Red
- Valid keys: Dim

### Invalid Date Format

```bash
$ lockin stats week 999999
```

**Output:**
```
Invalid date format: 999999
Expected format: DDMMYY (e.g., 150124 for Jan 15, 2024)
```

**Colors:**
- Error: Red
- Example: Dim

### Invalid Config Value

```bash
$ lockin config short_break_minutes 10000
```

**Output:**
```
Error: short_break_minutes cannot exceed 1440 minutes (24 hours)
```

**Colors:** Red

---

## Help Text

```bash
$ lockin --help
```

**Output:**
```
usage: lockin [-h] [duration] [break_duration] [date]

Lockin - Focus session timer

positional arguments:
  duration        Session duration in minutes or "break"
  break_duration  Break duration in minutes, "short", or "long"
  date            Date for stats (DDMMYY for week/month, YYYY for year)

options:
  -h, --help      show this help message and exit

Examples:
  lockin              # Show dashboard or attach to running session
  lockin 30           # Start 30-minute work session
  lockin break 5      # Start 5-minute break
  lockin break short  # Start short break (from config)
  lockin break long   # Start long break (from config)
  lockin stats week   # Show this week's stats
  lockin config       # Show configuration
```

---

## Notifications

### Session Complete

**macOS Notification Center:**

```
┌─────────────────────────────────┐
│ Lockin - work complete          │
├─────────────────────────────────┤
│ Your 30 minute work session is  │
│ complete!                        │
└─────────────────────────────────┘
```

With sound: 🔔 System notification sound

---

## Loading/Processing States

### Attaching to Session

First frame:
```
Connecting...
```

Then immediately:
```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘
(full UI appears)
```

### No Noticeable Loading

Lockin is fast. Most operations are instant:
- Starting sessions: < 0.1s
- Viewing stats: < 0.2s
- Config changes: < 0.1s

---

## Color Scheme Summary

**Primary colors:**
- **Cyan** - Titles, borders, progress bars, accents
- **Green** - Time remaining, positive states
- **Yellow** - Bonus time, warnings
- **Red** - Errors, critical messages
- **Dim gray** - Secondary info, hints, controls

**Why cyan?**
- Professional
- Easy to read
- Distinct from typical terminal colors
- Not too aggressive (compared to bright red/green)

---

## UI Animations

### Progress Bar Updates

The progress bar smoothly advances every second:

```
00:10  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
00:09  █████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
00:08  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
00:07  ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

### Time Countdown

Updates every second with smooth transitions:

```
25:14 remaining  →  25:13 remaining  →  25:12 remaining
```

---

## Terminal Compatibility

Lockin uses **Rich library** which works with:
- ✅ Terminal.app (macOS)
- ✅ iTerm2
- ✅ VS Code integrated terminal
- ✅ tmux
- ✅ screen

**Features that work everywhere:**
- Progress bars
- Colors
- Tables
- Borders
- Unicode characters

---

## Detached vs. Attached

### Detached (Session Running in Background)

You won't see anything. The session continues silently.

Check by running:
```bash
$ lockin
```

Then you'll see the full UI.

### Attached

You see the live UI with:
- Real-time countdown
- Progress bar advancing
- Updated stats
- Interactive controls

---

## Real-Time Example Session

Here's what you'd see if you started a 5-minute session and watched it:

**00:00 - Start:**
```bash
$ lockin 5
Started 5-minute work session
Attach with: lockin

$ lockin
```

**00:01 - Just started:**
```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

04:59 remaining
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Started: 10:05
Planned: 5 min
Elapsed: 00:01

Today: 0h 0m focused · 0 sessions · streak 0

[q] quit (scrap)   [d] detach
```

**02:30 - Halfway:**
```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

02:30 remaining
████████████████████░░░░░░░░░░░░░░░░░░░░

Started: 10:05
Planned: 5 min
Elapsed: 02:30

Today: 0h 0m focused · 0 sessions · streak 0

[q] quit (end early)   [d] detach
```

**04:50 - Almost done:**
```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

00:10 remaining
███████████████████████████████████████░

Started: 10:05
Planned: 5 min
Elapsed: 04:50

Today: 0h 0m focused · 0 sessions · streak 0

[q] quit (end early)   [d] detach
```

**05:00 - Complete! (+ notification appears):**
```
┌─────────────┐
│ LOCKIN — work│
└─────────────┘

02:58 to decide
████████████████████████████████████████

Started: 10:05
Planned: 5 min
Elapsed: 05:00

Today: 0h 5m focused · 1 sessions · streak 1

[q] quit (end)   [b/B] break (short/custom)   [c] continue   [d] detach
Defaulting to continue in 2:58
```

**Press 'q' to end:**
```bash
$ lockin
(shows idle dashboard)
```

---

These examples show the actual look and feel of Lockin in a terminal. The Rich library provides beautiful, colorful output with smooth updates and professional formatting.
