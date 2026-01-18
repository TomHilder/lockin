"""Main entry point for Lockin CLI."""

import argparse
from pathlib import Path

from .cli import LockinUI, console
from .config import Config


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
  lockin break 5      # Start 5-minute break
  lockin break short  # Start short break (from config)
  lockin break long   # Start long break (from config)
  lockin stats week   # Show this week's stats
  lockin config       # Show configuration
        """
    )
    
    parser.add_argument('duration', nargs='?', type=str,
                       help='Session duration in minutes or "break"')
    parser.add_argument('break_duration', nargs='?', type=str,
                       help='Break duration in minutes, "short", or "long"')
    parser.add_argument('date', nargs='?', type=str,
                       help='Date for stats (DDMMYY for week/month, YYYY for year)')
    
    args = parser.parse_args()
    
    # Check if engine is running (by checking if state exists and is recent)
    state = ui.get_current_state()
    engine_running = state is not None
    
    if not engine_running:
        console.print("[yellow]Warning:[/yellow] Lockin engine not running")
        console.print("Start the engine with: [cyan]lockin-engine[/cyan]")
        console.print("Or install as LaunchAgent for automatic startup")
        console.print()
    
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
            console.print("[yellow]A session is already running[/yellow]")
            console.print("Quit it first with [cyan]q[/cyan] in the session view")
            return
        
        ui.queue_command('start_session', session_type='break', duration_minutes=duration)
        console.print(f"[green]Started {duration}-minute break[/green]")
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
    console.print("Attach with: [cyan]lockin[/cyan]")


if __name__ == '__main__':
    main()
