"""Main entry point for Lockin CLI."""

import argparse
import subprocess
import time
from pathlib import Path

from .cli import LockinUI, console
from .config import Config


def is_engine_running(db) -> bool:
    """Check if engine is running (LaunchAgent or manual)."""
    # Check LaunchAgent
    try:
        result = subprocess.run(
            ['launchctl', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'com.lockin.engine' in result.stdout:
            return True
    except Exception:
        pass

    # Check if engine_state was updated recently (manual run)
    with db.connection() as conn:
        cursor = conn.execute("SELECT updated_at FROM engine_state WHERE id = 1")
        row = cursor.fetchone()
        if row and row['updated_at']:
            return (time.time() - row['updated_at']) < 10
    return False


def get_data_dir() -> Path:
    """Get Lockin data directory."""
    data_dir = Path.home() / '.lockin'
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_db_path() -> Path:
    """Get database path."""
    return get_data_dir() / 'lockin.db'


def main():
    """Main CLI entry point."""
    db_path = get_db_path()
    ui = LockinUI(db_path)
    
    parser = argparse.ArgumentParser(
        description='Lockin - Focus session timer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lockin              # Show dashboard or attach to running session
  lockin 30           # Start 30-minute work session
  lockin work         # Start work session with default duration
  lockin break 5      # Start 5-minute break
  lockin break short  # Start short break (from config)
  lockin break long   # Start long break (from config)
  lockin quit         # End session (if past threshold)
  lockin quit --scrap # Force end session
  lockin stats week   # Stats for this week
  lockin stats month  # Stats for this month
  lockin stats year   # Stats for this year
  lockin log          # Show 10 most recent sessions
  lockin log 5 --work # Show 5 most recent work sessions
  lockin delete 1     # Delete most recent session (with confirmation)
  lockin config       # Show configuration
        """
    )
    
    parser.add_argument('duration', nargs='?', type=str,
                       help='Session duration in minutes or "break"')
    parser.add_argument('break_duration', nargs='?', type=str,
                       help='Break duration in minutes, "short", or "long"')
    parser.add_argument('date', nargs='?', type=str,
                       help='Date for stats (DDMMYY for week/month, YYYY for year)')
    parser.add_argument('--scrap', action='store_true',
                       help='Force quit session even if below minimum threshold')
    parser.add_argument('--work', action='store_true',
                       help='Filter log to work sessions only')
    parser.add_argument('--break', dest='break_only', action='store_true',
                       help='Filter log to break sessions only')

    args = parser.parse_args()

    # Check if engine is running
    state = ui.get_current_state()
    engine_running = is_engine_running(ui.db)

    if not engine_running:
        console.print("[yellow]Warning:[/yellow] Lockin engine not running")
        console.print("Start the engine with: [cyan]lockin-engine[/cyan]")
        console.print("Or install as LaunchAgent for automatic startup")
        console.print()

    # Warn if --scrap used with non-quit command
    if args.scrap and args.duration != 'quit':
        console.print("[dim]--scrap flag ignored (only applies to quit)[/dim]")

    # Warn if --work/--break used with non-log command
    if (args.work or args.break_only) and args.duration != 'log':
        console.print("[dim]--work/--break flags ignored (only apply to log)[/dim]")

    # Parse command
    
    # No arguments - show dashboard or attach
    if not args.duration:
        if state and state['session_state'] not in ['idle', 'ended']:
            ui.attach_to_session()
        else:
            ui.show_idle_dashboard()
        return
    
    # Stats command
    if args.duration == 'stats':
        period = args.break_duration or 'week'
        if period not in ['week', 'month', 'year']:
            console.print(f"[red]Invalid period: {period}[/red]")
            console.print("Valid periods: week, month, year")
            return

        ui.show_stats(period, args.date)
        return

    # Log command
    if args.duration == 'log':
        # Parse limit (default 10)
        limit = 10
        if args.break_duration:
            try:
                limit = int(args.break_duration)
                if limit < 1:
                    console.print("[red]Limit must be at least 1[/red]")
                    return
            except ValueError:
                console.print(f"[red]Invalid limit: {args.break_duration}[/red]")
                return

        # Determine filter
        session_type = None
        if args.work and args.break_only:
            console.print("[yellow]Cannot use both --work and --break[/yellow]")
            return
        elif args.work:
            session_type = 'work'
        elif args.break_only:
            session_type = 'break'

        ui.show_log(limit, session_type)
        return

    # Delete command
    if args.duration == 'delete':
        if not args.break_duration:
            console.print("[red]Usage: lockin delete <position>[/red]")
            console.print("[dim]Position corresponds to # in 'lockin log' (1 = most recent)[/dim]")
            return

        try:
            position = int(args.break_duration)
        except ValueError:
            console.print(f"[red]Invalid position: {args.break_duration}[/red]")
            console.print("[dim]Position must be a number from 'lockin log'[/dim]")
            return

        ui.delete_session(position)
        return

    # Config command
    if args.duration == 'config':
        if not args.break_duration:
            ui.show_config()
        elif args.break_duration == 'reset':
            config = Config(ui.db)
            config.reset()
            console.print("[green]Configuration reset to defaults[/green]")
        else:
            # Set config value
            if not args.date:
                console.print("[red]Usage: lockin config <key> <value>[/red]")
                return
            
            key = args.break_duration
            value = args.date
            
            try:
                config = Config(ui.db)
                config.set(key, value)
                console.print(f"[green]Set {key} = {value}[/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                console.print(f"[dim]Valid keys: {', '.join(sorted(config.get_all().keys()))}[/dim]")
        return

    # Quit command
    if args.duration == 'quit':
        if not state or state['session_state'] in ['idle', 'ended']:
            console.print("[yellow]No active session[/yellow]")
            return

        session_type = state['session_type']
        elapsed_minutes = (time.time() - state['start_time']) / 60
        config = Config(ui.db)

        # Determine threshold
        if session_type == 'work':
            threshold = config.min_work_minutes
        else:
            threshold = config.min_break_minutes

        below_threshold = elapsed_minutes < threshold

        # Check if past minimum threshold (unless --scrap)
        if below_threshold and not args.scrap:
            console.print(f"[yellow]Session only {elapsed_minutes:.1f} min old (threshold: {threshold} min)[/yellow]")
            console.print("Use [cyan]lockin quit --scrap[/cyan] to force quit")
            return

        ui.queue_command('quit_session')

        # Show appropriate message
        if below_threshold:
            console.print(f"[yellow]{session_type.capitalize()} session scrapped (not logged)[/yellow]")
        elif session_type == 'work':
            console.print(f"[green]{session_type.capitalize()} session ended early (logged)[/green]")
        else:
            console.print(f"[green]{session_type.capitalize()} session ended (logged)[/green]")
        return

    # Break command
    if args.duration == 'break':
        if not args.break_duration:
            console.print("[red]Specify break duration (minutes, 'short', or 'long')[/red]")
            return
        
        config = Config(ui.db)
        
        if args.break_duration == 'short':
            duration = config.short_break_minutes
        elif args.break_duration == 'long':
            duration = config.long_break_minutes
        else:
            try:
                duration = int(args.break_duration)
                if duration <= 0:
                    console.print("[red]Duration must be positive[/red]")
                    return
                if duration > 1440:
                    console.print("[red]Duration cannot exceed 24 hours (1440 minutes)[/red]")
                    return
            except ValueError:
                console.print(f"[red]Invalid duration: {args.break_duration}[/red]")
                return
        
        # Check if session already running
        if state and state['session_state'] not in ['idle', 'ended']:
            # Allow starting a break if work session is in decision/bonus state
            # (mirrors pressing 'b' in the interactive UI)
            if (state['session_type'] == 'work' and
                state['session_state'] in ['awaiting_decision', 'running_bonus']):
                ui.queue_command('quit_session')
                time.sleep(0.5)  # Wait for quit to process
            else:
                console.print("[yellow]A session is already running[/yellow]")
                console.print("Quit it first with [cyan]q[/cyan] in the session view")
                return

        ui.queue_command('start_session', session_type='break', duration_minutes=duration)
        console.print(f"[green]Started {duration}-minute break[/green]")
        if config.auto_attach:
            ui.attach_to_session(wait_for_session=True)
        else:
            console.print("Attach with: [cyan]lockin[/cyan]")
        return

    # Work command (default duration)
    if args.duration == 'work':
        config = Config(ui.db)
        duration = config.work_default_minutes

        # Check if session already running
        if state and state['session_state'] not in ['idle', 'ended']:
            console.print("[yellow]A session is already running[/yellow]")
            console.print("Quit it first with [cyan]q[/cyan] in the session view")
            return

        ui.queue_command('start_session', session_type='work', duration_minutes=duration)
        console.print(f"[green]Started {duration}-minute work session[/green]")
        if config.auto_attach:
            ui.attach_to_session(wait_for_session=True)
        else:
            console.print("Attach with: [cyan]lockin[/cyan]")
        return

    # Work session (numeric duration)
    try:
        duration = int(args.duration)
        if duration <= 0:
            console.print("[red]Duration must be positive[/red]")
            return
        if duration > 1440:
            console.print("[red]Duration cannot exceed 24 hours (1440 minutes)[/red]")
            return
    except ValueError:
        console.print(f"[red]Invalid duration: {args.duration}[/red]")
        parser.print_help()
        return
    
    # Check if session already running
    if state and state['session_state'] not in ['idle', 'ended']:
        console.print("[yellow]A session is already running[/yellow]")
        console.print("Quit it first with [cyan]q[/cyan] in the session view")
        return
    
    ui.queue_command('start_session', session_type='work', duration_minutes=duration)
    console.print(f"[green]Started {duration}-minute work session[/green]")
    config = Config(ui.db)
    if config.auto_attach:
        ui.attach_to_session(wait_for_session=True)
    else:
        console.print("Attach with: [cyan]lockin[/cyan]")


if __name__ == '__main__':
    main()
