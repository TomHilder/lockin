# Changelog

All notable changes to Lockin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-01-16

### Fixed
**Documentation Error**
- Fixed lifecycle diagram that incorrectly showed quitting could lead to bonus time/bonus time
- Added explicit clarification: "Quitting is always final"
- Corrected state transition diagram to match actual code behavior

### Changed
**Terminology Improvements**
- Renamed "bonus time/bonus time" to "bonus time" throughout (kinder, more positive language)
- `SessionState.RUNNING_BONUS_TIME` → `SessionState.RUNNING_BONUS`
- `bonus_minutes_minutes` variable → `bonus_minutes`
- UI now shows "+05:23 bonus time" instead of "+05:23 bonus time"
- All documentation updated with new terminology

### Improved
**UI Enhancements**
- Smart quit message: Shows `[q] quit (scrap)` vs `[q] quit (end early)` based on whether session will be logged
- Monthly statistics now show weekly breakdown instead of daily (more digestible)
- Numbers now appear before progress bars for better readability
- Cleaner stat formatting with right-aligned columns

### Technical
- Database schema unchanged (backward compatible)
- Parameter names updated but DB field stays `bonus_minutes_minutes` for compatibility
- No migrations needed
- All tests passing (5/5)

### Documentation
- Updated all terminal output examples
- Added CLARIFICATIONS.md documenting fixes
- Added UI_IMPROVEMENTS.md documenting enhancements
- Fixed all state machine diagrams

---

## [1.0.0] - 2024-01-16

### Initial Release

First stable release of Lockin - a terminal-based focus timer for macOS.

#### Features

**Core Functionality**
- Work and break sessions with customizable durations
- Persistent background engine (runs as LaunchAgent)
- Sessions survive terminal closures and system sleep
- Beautiful terminal UI using Rich library
- macOS desktop notifications
- Interactive keyboard controls

**Session Management**
- Complete state machine (idle → running → decision → bonus time)
- Decision window after session completion
- Automatic bonus time support
- Break switching (short ↔ long) during breaks
- Session logging with abandon threshold

**Tracking & Statistics**
- Streak tracking (consecutive completed sessions)
- Daily, weekly, monthly, and yearly statistics
- Session history with completed/abandoned states
- Bonus time tracking
- Break time tracking
- Progress visualization with bars and charts

**Configuration**
- Customizable break durations
- Configurable break frequency (long break every N sessions)
- Adjustable abandon threshold
- Decision window duration setting
- All settings persist in database

**Smart Features**
- Intelligent break recommendations (short vs. long)
- Automatic long break after configurable session count
- Command queue for reliable CLI → Engine communication
- Graceful handling of system sleep/wake
- Validation of all user inputs

#### Technical Highlights

- Pure Python implementation (3.9+)
- SQLite database for persistence
- LaunchAgent for background execution
- Rich library for beautiful terminal UI
- Comprehensive test suite
- Adversarial testing and hardening
- Input validation and error handling

#### Documentation

- Comprehensive README with examples
- Detailed user guide
- Architecture documentation
- Troubleshooting guide
- FAQ
- Contributing guidelines
- Quick reference guide

#### Installation

- Single command installation script
- Automatic LaunchAgent setup
- Dedicated Python virtual environment
- PATH configuration
- Clean uninstallation script

#### Validation

- 5/5 unit tests passing
- Adversarial testing completed
- All edge cases handled
- Input validation for all user inputs
- Database corruption protection
- Error recovery mechanisms

### Added

- `lockin <minutes>` - Start work session
- `lockin break <duration>` - Start break
- `lockin break short/long` - Predefined breaks
- `lockin stats week/month/year` - View statistics
- `lockin config` - View/modify configuration
- `lockin-engine` - Background engine process
- Interactive controls (q, d, b, c, s, l)
- Notification system integration
- Streak calculation
- Session history
- Progress bars and charts
- Dashboard view
- State persistence
- Command queue system
- Configuration validation
- Date parsing with error handling
- Duration validation (1-1440 minutes)
- Config key validation
- Session state validation
- Graceful error messages

### Security

- All SQL queries use parameterization
- Input validation on all user inputs
- No network access
- Local-only data storage
- File permissions properly set
- No telemetry or tracking

### Performance

- Efficient SQLite queries with indexes
- 1 Hz tick rate (low CPU usage)
- Minimal memory footprint (~10-20 MB)
- Fast CLI startup
- Responsive UI updates

### Known Limitations

- macOS only (uses LaunchAgent, osascript)
- Single active session (by design)
- No cloud sync (by design)
- No multi-user support
- Terminal-only interface

## [Unreleased]

### Planned Features

Ideas for future releases (no timeline):

- Linux support (systemd, notify-send)
- Windows support (Task Scheduler, Windows notifications)
- Export to CSV/JSON
- Custom notification sounds
- Status bar app (macOS menu bar)
- Do Not Disturb integration
- Calendar blocking
- Webhook support for integrations
- Custom themes/colors
- Project tagging
- Multiple simultaneous sessions (architectural change)

### Improvements Under Consideration

- Automatic database backups
- Enhanced statistics (graphs, trends)
- Session templates
- Custom affirmations/messages
- Keyboard shortcut customization
- Multi-language support
- Integration with Slack/Discord
- API for third-party integrations

## Version History

### Version Numbering

Lockin follows semantic versioning:

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backward-compatible)
- **PATCH** version: Bug fixes (backward-compatible)

### Migration Guide

#### 1.0.0 → Future Versions

When upgrading:

1. Backup your data:
   ```bash
   cp ~/.lockin/lockin.db ~/lockin-backup.db
   ```

2. Run the installation script:
   ```bash
   cd lockin
   git pull
   ./install.sh
   ```

3. Configuration and data are preserved automatically

#### Database Migrations

Future versions may include database migrations. These will be:
- Automatic on engine startup
- Backward-compatible
- Documented in release notes

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/yourusername/lockin.git
cd lockin

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# Adversarial tests
python3 final_verification.py

# Manual testing
./dev-engine.sh  # Terminal 1
lockin 1         # Terminal 2
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style
- Testing requirements

## Credits

### Dependencies

- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Python](https://www.python.org/) - Programming language
- [SQLite](https://www.sqlite.org/) - Database engine

### Inspiration

Lockin was inspired by:
- Pomodoro Technique
- Deep Work (Cal Newport)
- Terminal-first development tools
- Personal frustration with unreliable web timers

### Contributors

- Initial development: [Your Name]
- Testing and feedback: [Contributors]
- Documentation: [Contributors]

## License

Lockin is released under the MIT License. See [LICENSE](LICENSE) for details.

## Links

- **Homepage:** https://github.com/yourusername/lockin
- **Documentation:** [GitHub Wiki]
- **Issues:** https://github.com/yourusername/lockin/issues
- **Discussions:** https://github.com/yourusername/lockin/discussions

---

**Stay focused.** 🔒
