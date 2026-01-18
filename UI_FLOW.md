# Lockin UI Flow

Visual overview of the main screens and transitions.

## Main Screens

```
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│   IDLE DASHBOARD    │──────▶│   RUNNING SESSION   │──────▶│  DECISION WINDOW    │
└─────────────────────┘       └─────────────────────┘       └─────────────────────┘
                                                                      │
                                                                      ├──▶ quit → IDLE
                                                                      ├──▶ break → BREAK
                                                                      └──▶ continue → BONUS TIME


┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│    BREAK SESSION    │       │      BONUS TIME       │       │    STATISTICS       │
└─────────────────────┘       └─────────────────────┘       └─────────────────────┘
```

## Screen Details

### 1. Idle Dashboard
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

**Triggers:**
- Launch `lockin` with no active session
- After ending a session

---

### 2. Running Session
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

**Updates every second:**
- Time remaining counts down
- Progress bar advances
- Elapsed time increases

---

### 3. Decision Window
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

**Triggers:**
- Automatically when session reaches planned end
- Shows for 3 minutes (configurable)

**Auto-advances to bonus time if no choice made**

---

### 4. Bonus time
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

**Continues indefinitely until you quit**

---

### 5. Break Session
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

**Can switch between short/long (with time restrictions)**

---

### 6. Statistics
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

Mon 08     ██████████████████ 3h 30m (7 sessions)
Tue 09     ████████████████████████ 4h 15m (8 sessions)
Wed 10     ██████████████ 2h 45m (6 sessions)
...
```

**Available views:**
- `lockin stats week`
- `lockin stats month`
- `lockin stats year`

---

## Complete User Flow Example

### Starting a Session

```
$ lockin 30
Started 30-minute work session
Attach with: lockin
```

### Watching It Run

```
$ lockin

┌─────────────┐
│ LOCKIN — work│     ← RUNNING
└─────────────┘

25:14 remaining
████████████████████▍░░░░
```

*...time passes...*

```
┌─────────────┐
│ LOCKIN — work│     ← STILL RUNNING
└─────────────┘

00:15 remaining
███████████████████████████████████████▌
```

*...session completes...*

```
┌─────────────┐
│ LOCKIN — work│     ← DECISION WINDOW
└─────────────┘

02:58 to decide
████████████████████████████████████████

[q] quit (end)   [b/B] break (short/custom)   [c] continue   [d] detach
```

### Taking a Break

Press `b`:

```
┌──────────────────┐
│ LOCKIN — break (short)│     ← BREAK
└──────────────────┘

04:52 remaining
███░░░░░░░░░░░░░░
```

### Checking Progress

```
$ lockin stats week

┌─────────────────────────────────────┐
│ LOCKIN — Stats: Week of Jan 08, 2024 │
└─────────────────────────────────────┘

...stats display...
```

---

## State Transitions

```
              start
    ┌──────────────────────────┐
    │                          │
    ▼                          │
┌────────┐                     │
│  IDLE  │◀────────────────────┤
└────────┘                     │
    │                          │
    │ start session            │
    ▼                          │
┌──────────┐                   │
│ RUNNING  │                   │
└──────────┘                   │
    │                          │
    │ time expires             │
    ▼                          │
┌──────────────────┐           │
│ AWAITING_DECISION│           │
└──────────────────┘           │
    │    │    │                │
    │    │    └─continue──┐    │
    │    │                │    │
    │    └─break─────────▶│    │
    │                     │    │
    └─quit──────────────▶ │    │
                          │    │
                          ▼    │
                      ┌──────────┐
                      │ BONUS TIME │
                      └──────────┘
                          │
                          │ quit
                          │
                          └──────┘
```

---

## Keyboard Controls Summary

### Global (Any Screen)
- `d` - Detach (session continues in background)

### Running Session
- `q` - Quit early (may not log if too short)

### Decision Window
- `q` - End session
- `b` - Take recommended break
- `B` - Specify custom break duration
- `c` - Continue into bonus time
- `[wait]` - Auto-continues after 3 minutes

### Bonus time
- `q` - End session
- `b` - Take recommended break
- `B` - Specify custom break

### Break
- `q` - End break early
- `s` - Switch to short break
- `l` - Switch to long break

---

## Visual Indicators

### Colors

**Green** 🟢
- Time remaining (during session)
- Positive states

**Cyan** 🔵
- Titles, borders
- Progress bars
- Accents

**Yellow** 🟡
- Bonus time
- Warnings

**Red** 🔴
- Errors
- Critical messages

**Gray** ⚪
- Secondary info
- Hints
- Controls

### Progress Bars

**Empty:**
```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

**10% Complete:**
```
████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

**50% Complete:**
```
████████████████████░░░░░░░░░░░░░░░░░░░
```

**90% Complete:**
```
████████████████████████████████████░░░░
```

**100% Complete:**
```
████████████████████████████████████████
```

### Symbols

- `█` - Filled progress
- `▌` - Half-filled (current position)
- `░` - Empty progress
- `—` - No data (in stats)

---

## Multi-Terminal Behavior

### Terminal 1: Start Session
```
$ lockin 30
Started 30-minute work session
```

### Terminal 2: Attach to Same Session
```
$ lockin

┌─────────────┐
│ LOCKIN — work│
└─────────────┘

29:45 remaining
```

**Both terminals show the same session state.**

### Terminal 1: Close Terminal

*Session continues in background*

### Terminal 3: New Terminal, Attach
```
$ lockin

┌─────────────┐
│ LOCKIN — work│
└─────────────┘

25:30 remaining
```

**Session is still running, picks up where it was.**

---

## Notification Appearance

When session completes, macOS notification appears:

```
╔═══════════════════════════════╗
║ Lockin - work complete        ║
╠═══════════════════════════════╣
║ Your 30 minute work session   ║
║ is complete!                  ║
╚═══════════════════════════════╝
      🔔 [System sound]
```

Clicking notification doesn't do anything (information only).

---

## Real-Time Updates

The UI refreshes every ~1 second:

```
Frame 1 (T=0s):    25:14 remaining
Frame 2 (T=1s):    25:13 remaining
Frame 3 (T=2s):    25:12 remaining
```

Progress bar smoothly advances:
```
Frame 1:  ████████████████████▍░░░░░░░░░░░
Frame 2:  ████████████████████▌░░░░░░░░░░░
Frame 3:  ████████████████████▋░░░░░░░░░░░
```

---

This gives you a complete visual understanding of what using Lockin looks like in the terminal!
