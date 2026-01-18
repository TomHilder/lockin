# Lockin Quick Reference

## Commands

### Start Sessions
```bash
lockin 30              # 30-minute work session
lockin 45              # 45-minute work session
lockin break short     # Short break (5 min)
lockin break long      # Long break (15 min)
lockin break 10        # Custom 10-minute break
```

### View & Stats
```bash
lockin                 # Dashboard or attach to session
lockin stats week      # This week
lockin stats month     # This month
lockin stats year      # This year
lockin stats week 150124  # Specific week (DDMMYY)
```

### Configuration
```bash
lockin config                          # View all
lockin config short_break_minutes 5    # Set value
lockin config reset                    # Reset all
```

## Interactive Keys

### During Work Session
| Key | Action |
|-----|--------|
| `q` | Quit session |
| `d` | Detach UI |

### Decision Window (after completion)
| Key | Action |
|-----|--------|
| `q` | End session |
| `b` | Recommended break |
| `B` | Custom break |
| `c` | Continue (bonus time) |
| `d` | Detach UI |
| Wait | Auto-continue |

### During Break
| Key | Action |
|-----|--------|
| `q` | End break |
| `s` | Switch to short |
| `l` | Switch to long |
| `d` | Detach UI |

## Session States

```
idle → running → awaiting_decision → bonus time → ended
```

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `short_break_minutes` | 5 | Short break duration |
| `long_break_minutes` | 15 | Long break duration |
| `long_break_every` | 4 | Long break frequency |
| `abandon_threshold_minutes` | 5 | Min time to log abandoned |
| `break_scrap_threshold_minutes` | 2 | Min break time to log |
| `decision_window_minutes` | 3 | Decision time after completion |

## Streak Rules

**Increments when:**
- Work session completes
- Gap < 1 hour from last session
- Same day

**Resets when:**
- Gap ≥ 1 hour between sessions
- Midnight

**NOT affected by:**
- Abandoned sessions
- Breaks
- Bonus time

## Logging Rules

**Work sessions logged if:**
- Duration ≥ 5 minutes (abandon_threshold)

**Breaks logged if:**
- Duration ≥ 2 minutes (break_scrap_threshold)

**Session marked as:**
- **completed** - Reached planned end
- **abandoned** - Quit early but above threshold
- **Not logged** - Quit before threshold

## Engine Management

### Check status
```bash
launchctl list | grep lockin
```

### Start manually
```bash
lockin-engine
```

### Restart
```bash
launchctl unload ~/Library/LaunchAgents/com.lockin.engine.plist
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist
```

### View logs
```bash
tail -f ~/.lockin/engine.log
tail -f ~/.lockin/engine.error.log
```

## Development

### Run without installation
```bash
./dev-engine.sh        # Terminal 1
source .venv/bin/activate
lockin 30              # Terminal 2
```

### Run tests
```bash
pytest tests/ -v
```

## File Locations

```
~/.lockin/
├── lockin.db           # Database
├── venv/               # Python environment
├── engine.log          # Engine stdout
└── engine.error.log    # Engine stderr

~/Library/LaunchAgents/
└── com.lockin.engine.plist  # LaunchAgent config
```

## Troubleshooting

### Session not starting
- Check engine: `launchctl list | grep lockin`
- Check logs: `tail ~/.lockin/engine.error.log`
- Restart engine

### Database issues
```bash
# Backup first!
cp ~/.lockin/lockin.db ~/.lockin/lockin.db.backup

# Reset if needed
rm ~/.lockin/lockin.db
lockin-engine  # Will recreate
```

### Complete reset
```bash
./uninstall.sh
rm -rf ~/.lockin
./install.sh
```

## Tips

1. **Use detach (`d`)** instead of closing terminal
2. **Let decision window expire** for auto-continue
3. **Check stats weekly** to track progress
4. **Adjust break timing** to your preference
5. **Use streaks** for motivation, not stress

## Common Workflows

### Pomodoro-style
```bash
lockin 25              # Work 25 min
# When done: press 'b' for break
# After break: lockin 25 again
```

### Deep work blocks
```bash
lockin 90              # 90-minute session
# Can continue into bonus time
```

### Quick breaks
```bash
lockin break 3         # Quick 3-min break
```
