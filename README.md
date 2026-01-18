# Lockin

A macOS terminal focus timer with a persistent background engine.

**Note:** This repo is mostly AI-generated and is a work in progress.

```bash
lockin 30           # Start 30-minute focus session
lockin              # Attach to running session
lockin stats week   # View weekly stats
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

## How It Works

Lockin uses a persistent background engine (macOS LaunchAgent) that keeps running even when you close your terminal. The CLI communicates with the engine through SQLite.

```
CLI ──queue command──▶ SQLite ◀──process──Engine (background)
CLI ◀──poll state───── SQLite ◀──update─── Engine
```

## Troubleshooting

```bash
# Check if engine is running
launchctl list | grep lockin

# Start engine manually
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

## License

MIT - see [LICENSE](LICENSE)
