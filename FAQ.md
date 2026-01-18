# Lockin FAQ

Frequently Asked Questions about Lockin.

## General

### What is Lockin?

Lockin is a terminal-based focus timer for macOS that runs persistently in the background. Unlike browser-based timers, your sessions survive terminal closures, system sleep, and accidental quits.

### Why use Lockin over other timers?

**Lockin is better if you:**
- Work primarily in the terminal
- Need sessions that survive browser refreshes
- Want persistent background operation
- Value privacy (no cloud, no accounts)
- Prefer keyboard-driven interfaces

**Other timers might be better if you:**
- Work mainly in a browser
- Want mobile sync
- Need team features
- Want gamification

### Is Lockin free?

Yes, Lockin is free and open source (MIT License).

### Does Lockin work offline?

Yes, completely. Lockin requires no internet connection.

## Installation & Setup

### What are the system requirements?

- macOS (tested on 10.15+)
- Python 3.9 or later
- ~10 MB disk space

### Can I install Lockin without admin rights?

Yes, installation is entirely in your home directory (`~/.lockin`).

### Does Lockin interfere with other Python projects?

No, Lockin uses its own dedicated virtual environment at `~/.lockin/venv`. Your project venvs (including uv) are unaffected.

### Can I install Lockin on multiple machines?

Yes, but each installation is independent. No sync between machines.

### How do I update Lockin?

```bash
cd lockin
git pull
./install.sh  # Reinstalls with latest code
```

Your data (sessions, config) is preserved.

## Usage

### Can I have multiple sessions running?

No, Lockin enforces one global session at a time. This prevents confusion and maintains focus.

### What happens if I close my terminal during a session?

Nothing! The session continues in the background. Reopen any terminal and run `lockin` to reattach.

### Can I pause a session?

Not directly. The philosophy is to commit to focus blocks. However, you can:
- Quit early (if needed)
- Start a new session when ready

### What if my computer goes to sleep?

Time doesn't advance while asleep. If you start a 30-minute session and your laptop sleeps for 2 hours, you'll still have the same time remaining when you wake it.

### Can I extend a session mid-way?

When a session completes, you enter a "decision window" where you can:
- Continue into bonus time (unlimited)
- Start a break
- End the session

There's no way to extend before completion, but you can always go into bonus time after.

### How accurate is the timing?

Very accurate. The engine ticks every second using Unix timestamps. Accuracy is within 1 second.

### What's the maximum session length?

1440 minutes (24 hours).

### What's the minimum session length?

1 minute.

## Breaks

### Are breaks mandatory?

No, breaks are recommended but optional. After a session completes, you choose whether to take a break.

### What's the difference between short and long breaks?

**Short breaks** (default: 5 min):
- Recommended after most sessions
- Quick mental reset
- Stand up, hydrate, look away from screen

**Long breaks** (default: 15 min):
- Recommended every 4th session
- Substantial rest
- Walk around, eat, genuine relaxation

Both are configurable:
```bash
lockin config short_break_minutes 7
lockin config long_break_minutes 20
```

### Can I change break type during a break?

Yes, with rules:
- Before short duration ends: Switch to short or long
- After short duration ends: Can only switch to long
- After long duration ends: Break auto-ends

### Do breaks count toward my streak?

No, breaks don't affect streaks. Streaks only count work sessions.

### Can I skip the recommended break?

Yes, pressing `q` at the decision window ends the session without starting a break.

## Statistics & Tracking

### What does "streak" mean?

Your streak is the count of consecutive completed work sessions where:
- Each session is completed (not abandoned)
- Gap between sessions < 60 minutes
- Within the same day

Streak resets at midnight.

### What's the difference between "completed" and "abandoned" sessions?

**Completed:** Reached planned duration (or went into bonus time)
**Abandoned:** Quit early, but ran for at least `abandon_threshold_minutes` (default: 5)

Sessions shorter than the threshold aren't logged at all (considered "scrapped").

### Why don't I see short sessions in my stats?

Sessions must run for at least `abandon_threshold_minutes` (default: 5) to be logged. This prevents accidental starts from cluttering your history.

To log shorter sessions:
```bash
lockin config abandon_threshold_minutes 1
```

### How far back does history go?

Forever. All sessions are stored in SQLite. Database size grows slowly (~7 MB per 10 years at 10 sessions/day).

### Can I export my data?

Yes:
```bash
sqlite3 -header -csv ~/.lockin/lockin.db \
  "SELECT * FROM sessions" > sessions.csv
```

### Can I see stats for custom date ranges?

Currently, stats are for:
- Week (Monday-Sunday)
- Month (1st-last day)
- Year (Jan-Dec)

Custom ranges require manual database queries:
```bash
sqlite3 ~/.lockin/lockin.db <<EOF
SELECT 
    datetime(start_time, 'unixepoch', 'localtime') as start,
    actual_duration_minutes,
    state
FROM sessions
WHERE start_time BETWEEN <timestamp1> AND <timestamp2>;
EOF
```

## Privacy & Data

### Where is my data stored?

Everything is in `~/.lockin/`:
```
~/.lockin/
├── lockin.db          # All sessions, config, state
├── engine.log         # Engine activity log
└── engine.error.log   # Error log
```

### Does Lockin send data anywhere?

No. Lockin makes no network requests. All data stays on your machine.

### Can other users on my machine see my Lockin data?

By default, yes. The database has permissions `644` (user read/write, others read).

To restrict:
```bash
chmod 600 ~/.lockin/lockin.db
```

### How do I backup my data?

```bash
# Simple backup
cp ~/.lockin/lockin.db ~/Dropbox/lockin-backup-$(date +%Y%m%d).db

# Or use Time Machine (backs up entire ~/.lockin directory)
```

### How do I delete my data?

```bash
./uninstall.sh  # Asks if you want to delete data

# Or manually
rm -rf ~/.lockin
```

## Configuration

### How do I change settings?

```bash
lockin config                       # View all
lockin config <key> <value>        # Change one
lockin config reset                # Reset all to defaults
```

### What settings are available?

| Setting | Default | Description |
|---------|---------|-------------|
| short_break_minutes | 5 | Short break duration |
| long_break_minutes | 15 | Long break duration |
| long_break_every | 4 | Long break frequency |
| abandon_threshold_minutes | 5 | Min time to log abandoned sessions |
| break_scrap_threshold_minutes | 2 | Min break time to log |
| decision_window_minutes | 3 | Time to decide after completion |

### Can I use Lockin for Pomodoro Technique?

Yes! Pomodoro is 25/5/15 (work/short break/long break):

```bash
lockin config short_break_minutes 5
lockin config long_break_minutes 15
lockin config long_break_every 4

# Then just use:
lockin 25
# Press 'b' for breaks
```

### Can I customize the UI colors?

Not yet, but the code uses Rich library which supports theming. PRs welcome!

## Technical

### What programming language is Lockin written in?

Python 3.9+ using:
- Rich (terminal UI)
- SQLite (database)
- macOS LaunchAgent (background service)

### Why is it macOS only?

The notification system and background service (LaunchAgent) are macOS-specific. Linux/Windows support could be added with:
- Linux: systemd + notify-send
- Windows: Task Scheduler + Windows notifications

### How much RAM does Lockin use?

~10-20 MB for the engine process. Negligible CPU usage (~0.1%).

### Does Lockin affect battery life?

Negligibly. The engine ticks once per second but does minimal work.

### Can I run Lockin in a Docker container?

Not practically. Lockin needs:
- macOS notification system
- LaunchAgent for background persistence
- Terminal UI rendering

### Is Lockin open source?

Yes, MIT License. See [LICENSE](LICENSE).

### Can I contribute?

Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### What's the architecture?

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## Troubleshooting

### Engine not starting?

```bash
# Check status
launchctl list | grep lockin

# If not running, load it
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# See detailed troubleshooting
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

### Stats not showing?

Ensure you've completed at least one session:
```bash
sqlite3 ~/.lockin/lockin.db "SELECT COUNT(*) FROM sessions;"
```

Should return > 0.

### Notifications not appearing?

Check System Preferences → Notifications → Terminal (or iTerm2).

Ensure notifications are enabled.

### How do I reset everything?

```bash
./uninstall.sh  # Removes Lockin and optionally data
```

Or manually:
```bash
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
rm -rf ~/.lockin
rm ~/Library/LaunchAgents/com.lockin.engine.plist
```

## Workflow & Best Practices

### What session length should I use?

**It depends on your work:**

- **25 minutes:** Good for building habit, varied tasks
- **45-60 minutes:** Good for writing, coding, reading
- **90 minutes:** Good for deep technical work, learning

Experiment and use stats to find your optimal length.

### How many sessions should I aim for per day?

**Start small:**
- Week 1: 2-3 sessions/day
- Week 2-3: 4-6 sessions/day
- Week 4+: 6-8 sessions/day (if sustainable)

**Quality over quantity.** Better to do 3 focused sessions than 10 distracted ones.

### Should I use Lockin for everything?

No. Use Lockin for:
- ✅ Deep work requiring focus
- ✅ Writing, coding, reading, learning
- ✅ Creative work

Don't use for:
- ❌ Meetings (unless taking notes)
- ❌ Email (usually doesn't need timer)
- ❌ Breaks (defeats the purpose)

### How do I integrate Lockin with other tools?

**Task managers:**
- Start Todoist/Asana timer
- Start Lockin
- Both track the same time

**Calendar:**
- Block time on calendar
- Use Lockin during blocked time

**Screen recording:**
- Record screen for tutorials
- Run Lockin to track actual focused time

### Can I use Lockin for multiple projects?

Yes, but Lockin doesn't tag sessions by project. You'd need to:
- Track projects separately
- Or use external time tracking for project breakdown
- Lockin tracks total focused time only

## Comparison with Other Tools

### Lockin vs. Browser Timers (Pomofocus, etc.)

**Lockin:**
- ✅ Survives browser refresh
- ✅ Terminal-native
- ✅ Local storage
- ❌ macOS only

**Browser timers:**
- ✅ Cross-platform
- ✅ Accessible anywhere
- ❌ Lost on refresh
- ❌ Requires internet

### Lockin vs. Mobile Apps (Forest, etc.)

**Lockin:**
- ✅ At your desk (where you work)
- ✅ Keyboard-driven
- ❌ Not mobile

**Mobile apps:**
- ✅ Everywhere
- ✅ Social features
- ❌ Separate from workspace

### Lockin vs. RescueTime

**Lockin:**
- ✅ Manual, intentional tracking
- ✅ Focused sessions only
- ❌ Doesn't track all activity

**RescueTime:**
- ✅ Automatic tracking
- ✅ Complete picture
- ❌ Passive (no active focus)

### Lockin vs. Toggl

**Lockin:**
- ✅ Focus-specific
- ✅ Break recommendations
- ❌ No project tagging

**Toggl:**
- ✅ Project tracking
- ✅ Team features
- ❌ Not focus-optimized

## Future & Roadmap

### Will Lockin support Linux/Windows?

Possibly. It requires:
- systemd/Task Scheduler integration
- Alternative notification system
- Testing

No timeline yet. PRs welcome!

### Will Lockin have sync/cloud features?

Unlikely. Lockin's philosophy is:
- Local-first
- Privacy-focused
- Simple

Cloud sync adds:
- Complexity
- Privacy concerns
- Maintenance burden

If needed, manually sync the database via Dropbox/iCloud.

### Will Lockin have a GUI?

Probably not. The terminal UI is core to Lockin's identity. A GUI would:
- Increase complexity significantly
- Require different tech stack
- Change the interaction model

However, a companion status bar app might make sense.

### Can Lockin integrate with other apps?

Feature requests welcome! Ideas:
- Slack status integration
- Calendar blocking
- Do Not Disturb automation
- Webhook support

### Where can I request features?

- GitHub Issues: [Link]
- GitHub Discussions: [Link]

---

**Have a question not answered here?** Open an issue or discussion on GitHub!
