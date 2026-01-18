# Getting Started with Lockin

The fastest way to start using Lockin.

## Install (30 seconds)

```bash
cd lockin
./install.sh
source ~/.zshrc  # or ~/.bashrc
```

## Use (Right Now)

```bash
# Start a 25-minute focus session
lockin 25

# See live progress
lockin
```

**That's it.** You're focusing.

**→ Want to see what it looks like?** Check out [TERMINAL_EXAMPLES.md](TERMINAL_EXAMPLES.md)

## Key Controls

While in a session:

- **`d`** - Detach (session continues in background)
- **`q`** - Quit session

After session completes:

- **`b`** - Take a break
- **`q`** - End session
- **`c`** - Keep working (bonus time)

## Daily Commands

```bash
lockin 30              # 30-minute work session
lockin break short     # Short break
lockin stats week      # See your progress
lockin config          # View settings
```

## What Happens During a Session?

```
1. Session starts → Timer counts down
2. Time's up → Notification appears
3. You choose → Break / Continue / End
4. Stats updated → Progress tracked
```

## Your First Day

**Morning:**
```bash
lockin 25       # First session
# Press 'b' for break when done
lockin 25       # Second session
```

**Afternoon:**
```bash
lockin stats    # Check progress
lockin 45       # Longer session
```

**Evening:**
```bash
lockin stats week    # Review your day
```

## Common Questions

**Q: What if I close my terminal?**  
A: Session continues. Reopen terminal and run `lockin` to reconnect.

**Q: Can I change session length?**  
A: After starting, no. But you can go into "bonus time" after completion.

**Q: Where's my data?**  
A: `~/.lockin/lockin.db` - All your sessions are there.

## Customize

```bash
# View all settings
lockin config

# Change break durations
lockin config short_break_minutes 5
lockin config long_break_minutes 15

# Reset to defaults
lockin config reset
```

## Problems?

```bash
# Check if engine is running
launchctl list | grep lockin

# If not, load it
launchctl load ~/Library/LaunchAgents/com.lockin.engine.plist

# See logs
tail ~/.lockin/engine.log
```

Still stuck? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Next Steps

- **[README.md](README.md)** - Full documentation
- **[USER_GUIDE.md](USER_GUIDE.md)** - Advanced features
- **[QUICKSTART.md](QUICKSTART.md)** - Command reference

## Philosophy

Lockin is about **committed focus time**. 

- No pausing (commit to the duration)
- No multitasking (one session at a time)
- No distractions (that's the point)

**Start small.** Two 25-minute sessions is better than an abandoned 2-hour block.

**Use breaks.** They're not optional. Your brain needs them.

**Track progress.** Use stats to find your optimal session length and frequency.

## Pro Tips

1. **Start with 25 minutes** - Build the habit first
2. **Actually take breaks** - Stand up, move, look away from screen
3. **Check stats weekly** - Adjust based on data
4. **Experiment** - Find what works for you
5. **Be consistent** - Daily sessions beat occasional marathons

## Remember

Lockin is a tool, not a goal. The goal is **focused, quality work**.

Use Lockin to:
- ✅ Build the focus habit
- ✅ Track your focused time
- ✅ Find your optimal rhythm

Don't use Lockin to:
- ❌ Obsess over numbers
- ❌ Stress about streaks
- ❌ Compete with others

---

**You're ready.** Start your first session:

```bash
lockin 25
```

**Focus well.** 🔒
