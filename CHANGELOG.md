# Changelog

All notable changes to Lockin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI with pytest and ruff linting
- GitHub issue templates (bug report, feature request)

## [1.0.0] - 2026-01-20

Initial release.

### Added
- Work sessions with configurable duration (1-1440 minutes)
- Break sessions (short/long/custom duration)
- Persistent background engine via macOS LaunchAgent
- Session survives terminal close, crashes, SSH disconnects
- Decision window after work sessions (quit/continue/break)
- Overtime/bonus time tracking for extended sessions
- macOS notifications when sessions complete
- Statistics view (week/month/year)
- Session log with delete capability
- Streak tracking with long break recommendations
- 11 configuration options with validation
- Rich terminal UI with progress bar and live updates
- Detach/reattach to running sessions

### Configuration Options
- `short_break_minutes` - Short break duration (default: 5)
- `long_break_minutes` - Long break duration (default: 15)
- `long_break_every` - Sessions before long break (default: 4)
- `work_default_minutes` - Default work duration (default: 25)
- `min_work_minutes` - Minimum to log work session (default: 5)
- `min_break_minutes` - Minimum to log break (default: 2)
- `work_decision_minutes` - Decision window duration (default: 3)
- `auto_attach` - Auto-attach after starting session (default: false)
- `work_overtime_enabled` - Allow overtime after work (default: true)
- `work_overtime_max_minutes` - Max overtime before auto-end (default: 60)
- `break_overtime_contributes` - Count break overtime in log (default: false)

### CLI Commands
- `lockin <minutes>` - Start work session
- `lockin work` - Start work with default duration
- `lockin break <short|long|minutes>` - Start break
- `lockin quit [--scrap]` - End session
- `lockin stats <week|month|year>` - View statistics
- `lockin log [limit] [--work|--break]` - View session log
- `lockin delete <position>` - Delete logged session
- `lockin config [key] [value]` - View/set configuration

### Interactive Controls
- `q` - Quit session
- `d` - Detach (session continues in background)
- `b` - Take recommended break (after work)
- `B` - Custom break duration (after work)
- `c` - Continue into overtime (after work)
- `s` - Switch to short break (during break)
- `l` - Switch to long break (during break)
- `w` - End break and start work session

[Unreleased]: https://github.com/TomHilder/lockin/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/TomHilder/lockin/releases/tag/v1.0.0
