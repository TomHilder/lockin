# Lockin Troubleshooting Guide

Solutions to common problems and issues.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Engine Problems](#engine-problems)
4. [Session Issues](#session-issues)
5. [Statistics Problems](#statistics-problems)
6. [Notification Issues](#notification-issues)
7. [Database Issues](#database-issues)
8. [Advanced Debugging](#advanced-debugging)

## Quick Diagnostics

Run these commands to check system health:

```bash
# 1. Check if engine is running
launchctl list | grep lockin

# 2. Check if database exists
ls -lh ~/.lockin/lockin.db

# 3. Check recent logs
tail -20 ~/.lockin/engine.log

# 4. Check for errors
tail -20 ~/.lockin/engine.error.log

# 5. Test CLI
lockin config
```

**Healthy output:**
```
# 1. Should show: com.lockin.engine with a PID
# 2. Should show: file with size > 0
# 3. Should show: recent timestamps
# 4. Should be empty or minor warnings
# 5. Should display config table
```

## Installation Issues

### Problem: `./install.sh` fails with "Permission denied"

**Solution:**
```bash
chmod +x install.sh
./install.sh
```

### Problem: Python 3 not found

**Error:** `python3: command not found`

**Solution:**
```bash
# Install Python 3 from python.org
# Then verify:
python3 --version

# Should show: Python 3.9 or later
```

**macOS tip:** Use Homebrew
```bash
brew install python@3.11
```

### Problem: pip install fails with dependency errors

**Error:** `Could not find a version that satisfies the requirement...`

**Solution:**
```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Then reinstall
cd lockin
./install.sh
```

### Problem: LaunchAgent not loading

**Error:** `launchctl: Could not find specified service`

**Solution:**
```bash
# Check if plist exists
ls ~/Library/LaunchAgents/com.lockin.engine.plist

# If missing, reinstall
cd lockin
./install.sh

# Manually load
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# Verify
launchctl list | grep lockin
```

### Problem: `lockin` command not found after install

**Cause:** PATH not updated or shell not restarted

**Solution:**
```bash
# Check where lockin is
ls ~/.lockin/venv/bin/lockin

# Add to PATH manually
echo 'export PATH="$HOME/.lockin/venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or for bash
echo 'export PATH="$HOME/.lockin/venv/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
which lockin
```

## Engine Problems

### Problem: "Warning: Lockin engine not running"

**Diagnosis:**
```bash
launchctl list | grep lockin
```

**If shows nothing:**

```bash
# Load the LaunchAgent
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# Verify
launchctl list | grep lockin
```

**If shows but engine still not running:**

```bash
# Check error log
tail -50 ~/.lockin/engine.error.log

# Common issues:
# 1. Python path wrong in plist
# 2. Permission denied on database
# 3. Module import error
```

### Problem: Engine crashes repeatedly

**Diagnosis:**
```bash
# Check error log
cat ~/.lockin/engine.error.log
```

**Common causes:**

**1. Import error**
```
ModuleNotFoundError: No module named 'rich'
```

**Solution:**
```bash
# Reinstall dependencies
~/.lockin/venv/bin/pip install -e /path/to/lockin
```

**2. Database locked**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Kill any process holding the database
lsof ~/.lockin/lockin.db

# If shows processes, kill them
kill <PID>

# Restart engine
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

**3. Permission error**
```
PermissionError: [Errno 13] Permission denied: '/.lockin'
```

**Solution:**
```bash
# Fix permissions
chmod 755 ~/.lockin
chmod 644 ~/.lockin/lockin.db
```

### Problem: Engine seems to hang

**Symptoms:**
- Commands queued but not processed
- State not updating

**Diagnosis:**
```bash
# Check if engine process is running
ps aux | grep lockin-engine

# Check recent log activity
tail -f ~/.lockin/engine.log
# Should show activity every ~1 second
```

**Solution:**
```bash
# Restart engine
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# Or run manually to see errors
~/.lockin/venv/bin/lockin-engine
```

## Session Issues

### Problem: Session won't start

**Error:** `Session already in progress`

**Cause:** Previous session not properly ended

**Solution:**
```bash
# Check current state
lockin

# If shows running session, end it
# Press 'q' in the UI

# Or force-quit via database
sqlite3 ~/.lockin/lockin.db <<EOF
UPDATE engine_state SET current_state = 
'{"session_state": "idle", "session_type": null, "start_time": null, 
  "planned_end_time": null, "planned_duration_minutes": null, 
  "decision_window_start": null, "last_notification": null}'
WHERE id = 1;
EOF

# Restart engine
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

### Problem: Session ends immediately

**Symptoms:** Session starts then immediately completes

**Diagnosis:**
```bash
# Check logs for "Duration must be positive"
grep "Duration" ~/.lockin/engine.error.log
```

**Cause:** Invalid duration (zero or negative)

**Solution:**
```bash
# Use positive duration
lockin 30   # ✓ Valid
lockin 0    # ✗ Invalid
lockin -5   # ✗ Invalid
```

### Problem: Can't attach to running session

**Error:** Terminal shows idle when session should be running

**Diagnosis:**
```bash
# Check engine state directly
sqlite3 ~/.lockin/lockin.db "SELECT current_state FROM engine_state;"
```

**If shows null or empty:**
- Engine never started the session
- Check command queue:
```bash
sqlite3 ~/.lockin/lockin.db "SELECT * FROM commands WHERE processed = 0;"
```

**Solution:**
```bash
# Clear stale commands
sqlite3 ~/.lockin/lockin.db "DELETE FROM commands WHERE processed = 0;"

# Start fresh session
lockin 30
```

### Problem: Session stuck in "awaiting decision"

**Symptoms:** Decision window never times out

**Diagnosis:**
```bash
# Check current state
sqlite3 ~/.lockin/lockin.db "SELECT current_state FROM engine_state;" | python3 -m json.tool
```

**Solution:**
```bash
# Attach and make a decision
lockin
# Press 'c' to continue or 'q' to quit

# Or force-end via command
sqlite3 ~/.lockin/lockin.db "INSERT INTO commands (command, args) VALUES ('quit_session', null);"
```

## Statistics Problems

### Problem: Stats show zero sessions

**Diagnosis:**
```bash
# Check if any sessions logged
sqlite3 ~/.lockin/lockin.db "SELECT COUNT(*) FROM sessions;"
```

**If returns 0:**
- No sessions have been completed
- Sessions were too short (below abandon threshold)

**Solution:**
```bash
# Lower abandon threshold
lockin config abandon_threshold_minutes 2

# Or run longer sessions
lockin 10  # Make sure to complete it
```

**If returns > 0:**
- Date query might be wrong
- Check specific date:
```bash
sqlite3 ~/.lockin/lockin.db <<EOF
SELECT date(start_time, 'unixepoch', 'localtime') as date, 
       COUNT(*) as count 
FROM sessions 
GROUP BY date 
ORDER BY date DESC 
LIMIT 7;
EOF
```

### Problem: Stats show incorrect totals

**Symptoms:** Numbers don't match expectations

**Diagnosis:**
```bash
# Manual calculation
sqlite3 ~/.lockin/lockin.db <<EOF
SELECT 
    session_type,
    state,
    COUNT(*) as count,
    SUM(actual_duration_minutes) as total_minutes
FROM sessions
WHERE date(start_time, 'unixepoch', 'localtime') = date('now', 'localtime')
GROUP BY session_type, state;
EOF
```

**Common issues:**
- Abandoned sessions not counted in "completed"
- Break time counted separately
- Bonus time included in duration

**Solution:** Stats are working correctly. Understanding:
- "Focused time" = completed work sessions only
- "Breaks" = all break time
- "Sessions" = completed work sessions only

### Problem: Invalid date format error

**Error:** `Invalid date format: 320145`

**Cause:** Wrong date format or impossible date

**Solution:**
```bash
# Correct formats:
lockin stats week 150124    # DDMMYY (Jan 15, 2024)
lockin stats month 010124   # DDMMYY (January 2024)
lockin stats year 2024      # YYYY

# Common mistakes:
lockin stats week 2024      # ✗ Wrong format
lockin stats week 320145    # ✗ Day 32 doesn't exist
lockin stats month 130124   # ✗ Month 13 doesn't exist
```

## Notification Issues

### Problem: No notifications appearing

**Diagnosis:**

**1. Check System Preferences:**
```
System Preferences → Notifications → Terminal (or iTerm2)
- Ensure notifications are ON
- Check alert style
```

**2. Test notification manually:**
```bash
osascript -e 'display notification "Test" with title "Lockin Test"'
```

**If test works but Lockin doesn't:**
```bash
# Check engine is sending notifications
grep "notification" ~/.lockin/engine.log
```

**If no log entries:**
- Engine might not be reaching notification code
- Check session completes properly

### Problem: Notification appears but no sound

**Solution:**
```
System Preferences → Notifications → Terminal
- Change "Alert style" to "Alerts" or "Banners"
- Enable sound
```

### Problem: Duplicate notifications

**Cause:** Multiple engine instances running

**Diagnosis:**
```bash
ps aux | grep lockin-engine | grep -v grep
```

**If shows multiple processes:**

**Solution:**
```bash
# Kill all
pkill -f lockin-engine

# Reload (only one will start)
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

## Database Issues

### Problem: Database corrupted

**Error:** `database disk image is malformed`

**Solution:**

**1. Try to recover:**
```bash
# Backup first!
cp ~/.lockin/lockin.db ~/.lockin/lockin.db.backup

# Attempt recovery
sqlite3 ~/.lockin/lockin.db ".recover" | sqlite3 ~/.lockin/lockin_recovered.db

# If successful, replace
mv ~/.lockin/lockin.db ~/.lockin/lockin.db.corrupt
mv ~/.lockin/lockin_recovered.db ~/.lockin/lockin.db
```

**2. If recovery fails, restore from backup:**
```bash
# If you have a backup
cp ~/lockin-backup.db ~/.lockin/lockin.db

# Or start fresh (loses history)
rm ~/.lockin/lockin.db
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

### Problem: Database growing very large

**Diagnosis:**
```bash
# Check size
ls -lh ~/.lockin/lockin.db

# Check record counts
sqlite3 ~/.lockin/lockin.db <<EOF
SELECT 'sessions' as table_name, COUNT(*) as count FROM sessions
UNION ALL
SELECT 'commands', COUNT(*) FROM commands;
EOF
```

**If commands table is huge:**
```bash
# Clean up old processed commands
sqlite3 ~/.lockin/lockin.db "DELETE FROM commands WHERE processed = 1 AND created_at < strftime('%s', 'now', '-7 days');"

# Vacuum to reclaim space
sqlite3 ~/.lockin/lockin.db "VACUUM;"
```

### Problem: Can't access database

**Error:** `PermissionError` or `unable to open database file`

**Solution:**
```bash
# Check permissions
ls -l ~/.lockin/lockin.db

# Fix if needed
chmod 644 ~/.lockin/lockin.db
chown $(whoami) ~/.lockin/lockin.db

# Check directory
chmod 755 ~/.lockin
```

## Advanced Debugging

### Enable Verbose Logging

**Edit LaunchAgent:**
```bash
# Add debug output
vi ~/Library/LaunchAgents/com.lockin.engine.plist

# Change StandardOutPath to:
<key>EnvironmentVariables</key>
<dict>
    <key>PYTHONUNBUFFERED</key>
    <string>1</string>
    <key>LOCKIN_DEBUG</key>
    <string>1</string>
</dict>
```

**Reload:**
```bash
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

### Run Engine in Foreground

**See all output directly:**
```bash
# Stop LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist

# Run manually
~/.lockin/venv/bin/lockin-engine

# Press Ctrl+C to stop
# Press Ctrl+Z and `bg` to background
```

### Inspect State in Real-Time

**Terminal 1:**
```bash
# Watch state changes
watch -n 1 "sqlite3 ~/.lockin/lockin.db 'SELECT current_state FROM engine_state;' | python3 -m json.tool"
```

**Terminal 2:**
```bash
# Interact with Lockin
lockin 5
```

### Check for File Locks

**If database seems stuck:**
```bash
# See what's holding the database
lsof ~/.lockin/lockin.db

# Should show:
# lockin-engine <PID> <user> ...
```

**If shows multiple processes or unexpected ones:**
```bash
# Kill the unexpected process
kill <PID>
```

### Test Individual Components

**Test database directly:**
```bash
python3 << 'EOF'
from pathlib import Path
from lockin.database import Database

db = Database(Path.home() / '.lockin' / 'lockin.db')
print(f"Sessions: {len(db.get_sessions_by_date_range(...))}")
print(f"Config: {db.get_all_config()}")
EOF
```

**Test config:**
```bash
python3 << 'EOF'
from pathlib import Path
from lockin.database import Database
from lockin.config import Config

db = Database(Path.home() / '.lockin' / 'lockin.db')
config = Config(db)
print(f"Short break: {config.short_break_minutes}")
EOF
```

### Performance Issues

**If CLI feels slow:**

**1. Check database size:**
```bash
ls -lh ~/.lockin/lockin.db
```

**2. If > 100MB, optimize:**
```bash
sqlite3 ~/.lockin/lockin.db "VACUUM;"
sqlite3 ~/.lockin/lockin.db "ANALYZE;"
```

**3. Check query performance:**
```bash
sqlite3 ~/.lockin/lockin.db <<EOF
EXPLAIN QUERY PLAN 
SELECT * FROM sessions 
WHERE start_time >= strftime('%s', 'now', 'start of day');
EOF
```

**Should use indexes.**

## Emergency Procedures

### Complete Reset (Nuclear Option)

**When all else fails:**

```bash
# 1. Stop everything
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
pkill -f lockin

# 2. Backup data
mkdir -p ~/lockin-backup
cp -r ~/.lockin ~/lockin-backup/lockin-$(date +%Y%m%d)

# 3. Remove Lockin
rm -rf ~/.lockin
rm ~/Library/LaunchAgents/com.lockin.engine.plist

# 4. Reinstall
cd /path/to/lockin
./install.sh

# 5. Restore data (optional)
# cp ~/lockin-backup/lockin-YYYYMMDD/lockin.db ~/.lockin/
```

### Export Before Reset

**Save your history:**

```bash
# Export sessions
sqlite3 -header -csv ~/.lockin/lockin.db \
  "SELECT * FROM sessions" > ~/lockin-sessions-$(date +%Y%m%d).csv

# Export config
sqlite3 -header -csv ~/.lockin/lockin.db \
  "SELECT * FROM config" > ~/lockin-config-$(date +%Y%m%d).csv
```

## Getting Help

**Before asking for help, collect this info:**

```bash
# System info
sw_vers

# Python version
python3 --version

# Lockin installation
ls -la ~/.lockin/

# Engine status
launchctl list | grep lockin

# Recent errors
tail -50 ~/.lockin/engine.error.log

# Database check
sqlite3 ~/.lockin/lockin.db "PRAGMA integrity_check;"

# Config
lockin config
```

**Where to get help:**
- GitHub Issues: [Link to issues]
- GitHub Discussions: [Link to discussions]
- Email: support@lockin.dev

**Include:**
1. Problem description
2. What you tried
3. System info (above)
4. Relevant log excerpts

---

**Most problems have simple fixes.** Check the logs, verify the engine is running, and ensure the database is accessible. That solves 90% of issues.
