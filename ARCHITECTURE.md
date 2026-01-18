# Lockin Architecture

Technical documentation for understanding and contributing to Lockin.

## Table of Contents

1. [System Overview](#system-overview)
2. [Components](#components)
3. [Data Flow](#data-flow)
4. [State Management](#state-management)
5. [Persistence Strategy](#persistence-strategy)
6. [Design Decisions](#design-decisions)
7. [Security Considerations](#security-considerations)

## System Overview

Lockin follows a **persistent engine + ephemeral CLI** architecture:

```
┌─────────────────────────────────────────────────────┐
│                     User Layer                      │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │          CLI Process (ephemeral)           │   │
│  │  • Command parsing (argparse)              │   │
│  │  • Terminal UI (Rich)                      │   │
│  │  • Keyboard input                          │   │
│  │  • State polling (1 Hz)                    │   │
│  └──────┬─────────────────────────┬───────────┘   │
└─────────┼─────────────────────────┼───────────────┘
          │                         │
    Queue │                         │ Poll
 Commands │                         │ State
          │                         │
   ┌──────▼─────────────────────────▼──────┐
   │      SQLite Database (Shared)         │
   │  ┌──────────────────────────────────┐ │
   │  │  sessions - completed sessions   │ │
   │  │  config - user settings          │ │
   │  │  engine_state - current session  │ │
   │  │  commands - pending actions      │ │
   │  └──────────────────────────────────┘ │
   └──────┬─────────────────────────┬──────┘
          │                         │
  Process │                         │ Update
 Commands │                         │ State
          │                         │
   ┌──────▼─────────────────────────▼──────┐
   │    Engine Process (persistent)        │
   │  • LaunchAgent (runs as service)      │
   │  • State machine (tick @ 1 Hz)        │
   │  • Timer management                   │
   │  • Notification dispatch              │
   │  • Command processing                 │
   └───────────────────────────────────────┘
```

**Key principle:** SQLite is the single source of truth. No state is kept in memory that isn't persisted.

## Components

### 1. CLI Client (`cli.py`, `__main__.py`)

**Responsibilities:**
- Parse command-line arguments
- Display terminal UI using Rich
- Handle keyboard input (interactive mode)
- Queue commands to engine
- Poll engine state for display

**Lifecycle:**
```
Start → Parse args → Execute action → Exit
  ↓
  └─ If attach: Loop(poll state, render UI, handle input) → Exit
```

**Important:** CLI never modifies state directly. All state changes go through commands.

### 2. Database Layer (`database.py`)

**Responsibilities:**
- Provide clean API over SQLite
- Manage schema
- Handle transactions
- Ensure data integrity

**Tables:**

```sql
-- Historical data
sessions (
    id INTEGER PRIMARY KEY,
    session_type TEXT,
    state TEXT,
    start_time REAL,
    end_time REAL,
    planned_duration_minutes INTEGER,
    actual_duration_minutes REAL,
    bonus time_minutes REAL
)

-- User configuration
config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at REAL
)

-- Current engine state
engine_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_state TEXT,  -- JSON blob
    updated_at REAL
)

-- Command queue
commands (
    id INTEGER PRIMARY KEY,
    command TEXT,
    args TEXT,  -- JSON blob
    created_at REAL,
    processed INTEGER DEFAULT 0
)
```

**Why one row for engine_state?**  
Ensures exactly one active session. The `CHECK (id = 1)` constraint prevents multiple concurrent states.

### 3. Configuration Layer (`config.py`)

**Responsibilities:**
- Manage default values
- Validate config changes
- Provide type-safe accessors
- Enforce reasonable limits

**Pattern:**

```python
class Config:
    def get(self, key: str) -> Any:
        # Check DB → Fall back to defaults
        
    def set(self, key: str, value: Any):
        # Validate → Store to DB
        
    @property
    def short_break_minutes(self) -> int:
        return self.get('short_break_minutes')
```

**Why properties?** Type safety and IDE autocomplete.

### 4. Engine (`engine.py`)

**Responsibilities:**
- Run as persistent background process
- Implement session state machine
- Manage timers
- Send notifications
- Process commands from CLI

**Main Loop:**

```python
while True:
    tick()                    # Check timers, update state
    process_commands()        # Handle CLI commands
    sleep(1)                  # 1 Hz tick rate
```

**Tick logic:**
1. Check if session reached planned end → Enter decision window
2. Check if decision window expired → Auto-continue to bonus time
3. Check if break exceeded long duration → Auto-end
4. Handle system sleep/wake (time doesn't advance)

### 5. State Machine

Visual representation:

```
           start_session
    ┌──────────────────────────┐
    │                          │
    ▼                          │
┌────────┐                     │
│  IDLE  │                     │
└────────┘                     │
    │                          │
    │ session starts           │
    ▼                          │
┌──────────┐                   │
│ RUNNING  │                   │
└──────────┘                   │
    │                          │
    │ planned end reached      │
    ▼                          │
┌──────────────────┐           │
│ AWAITING_DECISION│           │
└──────────────────┘           │
    │          │               │
    │ continue │ quit          │
    │          │               │
    ▼          ▼               │
┌──────────┐ ┌────────┐       │
│ BONUS TIME │ │ ENDED  │───────┘
└──────────┘ └────────┘
    │
    │ quit
    ▼
┌────────┐
│ ENDED  │
└────────┘
    │
    └──────────────┐
                   │
    ┌──────────────┘
    ▼
┌────────┐
│  IDLE  │
└────────┘
```

**State transitions:**

| From | Event | To | Side Effects |
|------|-------|----|--------------| 
| IDLE | start_session | RUNNING | Create state, save to DB |
| RUNNING | time expires | AWAITING_DECISION | Send notification, start decision timer |
| AWAITING_DECISION | continue | RUNNING_BONUS TIME | Update state |
| AWAITING_DECISION | quit | ENDED | Log session, reset state |
| AWAITING_DECISION | timeout | RUNNING_BONUS TIME | Auto-continue |
| RUNNING_BONUS TIME | quit | ENDED | Log session with bonus time |
| RUNNING | quit | ENDED/IDLE | Log if > threshold, else scrap |
| ENDED | - | IDLE | Immediate (same tick) |

## Data Flow

### Starting a Session

```
 User                CLI              Database           Engine
  │                  │                   │                 │
  │  lockin 30       │                   │                 │
  ├─────────────────>│                   │                 │
  │                  │                   │                 │
  │                  │  queue_command    │                 │
  │                  ├──────────────────>│                 │
  │                  │  ("start_session",│                 │
  │                  │   {duration: 30}) │                 │
  │                  │                   │                 │
  │  "Started..."    │                   │                 │
  │<─────────────────┤                   │                 │
  │                  │                   │                 │
  │                  exit                │                 │
  │                                      │                 │
  │                                      │  get_pending    │
  │                                      │<────────────────┤
  │                                      │  [{cmd: start}] │
  │                                      ├────────────────>│
  │                                      │                 │
  │                                      │  set_state      │
  │                                      │<────────────────┤
  │                                      │  (RUNNING)      │
  │                                      │                 │
  │                                      │  mark_processed │
  │                                      │<────────────────┤
```

### Attaching to Session

```
 User                CLI              Database           Engine
  │                  │                   │                 │
  │  lockin          │                   │                 │
  ├─────────────────>│                   │                 │
  │                  │                   │                 │
  │                  │  get_state        │                 │
  │                  ├──────────────────>│                 │
  │                  │  {state: RUNNING} │                 │
  │                  │<──────────────────┤                 │
  │                  │                   │                 │
  │  ┌───────────┐   │                   │                 │
  │  │ Render UI │   │                   │                 │
  │  │  (loop)   │   │                   │                 │
  │  │           │   │  get_state (1 Hz) │                 │
  │  │           │   ├──────────────────>│                 │
  │  │           │   │                   │                 │
  │  │           │   │ Handle 'q' press  │                 │
  │  │           │   ├──────────────────>│                 │
  │  │           │   │ queue quit cmd    │                 │
  │  └───────────┘   │                   │                 │
  │                  exit                │                 │
```

## State Management

### Why Polling Instead of Push?

**Polling (what we do):**
```
CLI ──[every 1s]──> DB ──[get_state]──> Engine
```

**Advantages:**
- Simple to implement
- No network/IPC complexity
- Works with multiple CLIs naturally
- Engine doesn't need to track clients
- Terminal can close without notifying anyone

**Alternative (Push):**
```
Engine ──[socket]──> CLI
```

**Why not?**
- More complex (socket management)
- Requires client registration
- Harder to handle CLI crashes
- Terminal close requires cleanup

**Trade-off:** 1-second lag in UI updates, but this is imperceptible for a timer.

### State Persistence

Every state change:
1. Update in-memory state dict
2. Call `_save_state()` → Write to DB
3. Continue

**If engine crashes:**
1. LaunchAgent restarts it
2. Engine loads state from DB
3. Continues where it left off

**Critical:** No transient state. Everything in `engine.state` is persisted.

## Persistence Strategy

### SQLite Choice

**Why SQLite?**
- ✅ No server process
- ✅ ACID transactions
- ✅ File-based (easy backup)
- ✅ Python stdlib support
- ✅ Works great for < 1M records
- ✅ Concurrent reads + single writer

**Why not JSON files?**
- ❌ No transactions
- ❌ Race conditions on write
- ❌ Hard to query efficiently
- ❌ Manual schema management

**Why not Redis/Postgres?**
- ❌ Additional dependency
- ❌ Process to manage
- ❌ Overkill for local app

### LaunchAgent vs. Cron

**LaunchAgent** (what we use):
```xml
<key>KeepAlive</key>
<true/>
```

**Advantages:**
- Starts on login automatically
- Restarts if crashes
- Runs continuously (not periodic)
- Standard macOS pattern

**Cron alternative:**
```
* * * * * /path/to/engine
```

**Why not?**
- Runs every minute (not continuously)
- Multiple instances could conflict
- Need lock files
- Not idiomatic for macOS

## Design Decisions

### 1. Command Queue Pattern

**Instead of direct engine API:**

```python
# ❌ Direct (would require engine IPC)
engine.start_session(30)

# ✅ Queue (works via DB)
db.queue_command('start_session', {'duration': 30})
```

**Benefits:**
- Decouples CLI from engine process
- CLI can exit immediately (no waiting)
- Commands persist if engine is down
- Easy to add command history/audit

### 2. Single Global Session

**Enforced by:**
1. `engine_state` table has `CHECK (id = 1)`
2. Engine state machine rejects double-starts

**Why?**
- Prevents confusion ("which session am I in?")
- Clear mental model
- No need to manage session IDs

**Trade-off:** Can't track multiple activities simultaneously (by design).

### 3. Timestamps as Floats

```python
start_time: float  # Unix timestamp
```

**Why not datetime objects?**
- SQLite stores as REAL anyway
- Easy math (`end - start = duration`)
- No timezone issues (all UTC)

**Conversion for display:**
```python
datetime.fromtimestamp(start_time).strftime('%H:%M')
```

### 4. State as JSON Blob

```python
engine_state.current_state = '{"session_state": "running", ...}'
```

**Why JSON in TEXT field?**
- Flexible schema
- Easy to add fields
- Single row update (atomic)

**Why not normalized tables?**
- More complex queries
- Multiple writes for one state change
- State is truly atomic (all or nothing)

### 5. Rich for UI

**Why not curses/blessed?**
- Rich is higher-level
- Better colors/styling
- Progress bars built-in
- Easier to maintain

**Trade-off:** Less control over terminal, but we don't need that.

## Security Considerations

### Data Privacy

**Storage location:**
```
~/.lockin/
├── lockin.db          # All user data
├── engine.log         # Engine stdout
└── engine.error.log   # Engine stderr
```

**Permissions:**
- Database: `644` (user read/write)
- Logs: `644`
- Directory: `755`

**No network access:**
- Engine doesn't make network calls
- No telemetry
- No cloud sync
- Local only

### Input Validation

**All user inputs validated:**

```python
# Duration
if duration <= 0 or duration > 1440:
    raise ValueError()

# Config keys
if key not in DEFAULT_CONFIG:
    raise ValueError()

# Session state
if state not in valid_states:
    reset_to_idle()
```

**Why?**
- Prevent crashes
- Database corruption protection
- User error handling

### SQL Injection

**Protected by parameterization:**

```python
# ✅ Safe
cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))

# ❌ Would be unsafe (we never do this)
cursor.execute(f"SELECT * FROM sessions WHERE id = {session_id}")
```

**Additional:** User input never goes directly to SQL.

### macOS Notification Safety

**Notification content:**
- Only session type and duration
- No user data
- No sensitive info

**Example:**
```
Title: "Lockin - work complete"
Body: "Your 30 minute work session is complete!"
```

## Performance Characteristics

### Time Complexity

**Operations:**
- Start session: O(1) - single DB write
- Get state: O(1) - single row read
- Calculate streak: O(n) - where n = today's sessions
- Get stats: O(n) - where n = period's sessions
- Command queue: O(1) - indexed by processed flag

**Why O(n) for streak is fine:**
- n = sessions today (~10-50)
- Runs once per tick
- Takes microseconds

### Space Complexity

**Database growth:**
- 1 session ≈ 200 bytes
- 10 sessions/day = 2 KB/day
- 1 year = 730 KB
- 10 years = 7.3 MB

**Very manageable.** No need for cleanup/archival.

### Tick Rate

**1 Hz (once per second):**
- Fast enough for good UX
- Low CPU usage (~0.1%)
- Doesn't matter if ticks drift slightly

**Why not 10 Hz?**
- No benefit (timer granularity is seconds)
- More CPU usage

**Why not 0.1 Hz (10 seconds)?**
- Laggy UX
- Could miss rapid state changes

## Testing Strategy

### Unit Tests (`tests/test_database.py`)

**Coverage:**
- Database operations
- Config management
- Session logging
- Streak calculation

**Pattern:**
```python
def test_feature():
    db = Database(temp_path)
    # Setup
    # Action
    # Assert
```

### Integration Tests (`final_verification.py`)

**Coverage:**
- Full workflows
- State transitions
- Error handling

### Adversarial Tests

**Coverage:**
- Invalid inputs
- Edge cases
- Database corruption
- Race conditions

See `ADVERSARIAL_FINDINGS.md` for details.

## Future Considerations

### Scalability

**Current limits:**
- Single machine
- Single user
- ~10-50 sessions/day

**If we needed to scale:**
1. Multi-user: Add user_id to all tables
2. Multi-machine: Sync layer (conflicts possible)
3. High volume: Postgres migration

### Extensibility

**Easy to add:**
- New session types
- Additional stats
- Export formats
- Custom notifications

**Harder to add:**
- Multiple simultaneous sessions (architectural change)
- Sync across devices (requires conflict resolution)
- Windows/Linux support (LaunchAgent → systemd/Task Scheduler)

### Platform Support

**Current: macOS only**

**To add Linux:**
- Replace LaunchAgent with systemd
- Replace osascript with notify-send
- Test terminal rendering

**To add Windows:**
- Replace LaunchAgent with Task Scheduler
- Replace osascript with Windows notifications
- Handle path differences

**Effort:** ~2-3 days per platform

## Appendix: File Structure

```
lockin/
├── src/lockin/
│   ├── __init__.py          # Package metadata
│   ├── __main__.py          # CLI entry point
│   ├── cli.py               # Terminal UI, 420 lines
│   ├── config.py            # Config management, 70 lines
│   ├── database.py          # SQLite layer, 340 lines
│   ├── engine.py            # State machine, 270 lines
│   └── engine_main.py       # Engine entry, 30 lines
├── tests/
│   └── test_database.py     # Unit tests
├── docs/
│   ├── README.md
│   ├── USER_GUIDE.md
│   ├── ARCHITECTURE.md      # This file
│   └── TROUBLESHOOTING.md
├── pyproject.toml           # Package config
├── install.sh               # Installation script
├── uninstall.sh             # Removal script
└── com.lockin.engine.plist  # LaunchAgent template
```

**Total:** ~1,300 lines of Python + ~500 lines of docs

---

**Next Steps:**
- Read [USER_GUIDE.md](USER_GUIDE.md) for usage patterns
- Read [CONTRIBUTING.md](CONTRIBUTING.md) to add features
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
