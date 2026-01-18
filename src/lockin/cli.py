"""CLI client with Rich terminal UI for Lockin."""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .database import Database
from .config import Config
from .engine import SessionState, SessionType


console = Console()


def format_duration(minutes: float) -> str:
    """Format duration in minutes to human readable."""
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def format_time_remaining(seconds: float) -> str:
    """Format seconds remaining as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


class LockinUI:
    """Terminal UI manager for Lockin."""
    
    def __init__(self, db_path: Path):
        self.db = Database(db_path)
        self.config = Config(self.db)
    
    def get_current_state(self) -> Optional[dict]:
        """Get current engine state."""
        return self.db.get_engine_state()
    
    def queue_command(self, command: str, **kwargs):
        """Queue a command for the engine."""
        self.db.queue_command(command, kwargs if kwargs else None)
    
    def show_idle_dashboard(self):
        """Display idle dashboard."""
        console.clear()
        
        # Header
        console.print(Panel.fit(
            "[bold cyan]LOCKIN[/bold cyan] — idle",
            border_style="cyan"
        ))
        console.print()
        
        # Last session info
        last_session = self.db.get_last_session()
        if last_session:
            session_type = last_session['session_type'].capitalize()
            duration = int(last_session['actual_duration_minutes'])
            state = last_session['state']
            end_time = datetime.fromtimestamp(last_session['end_time'])
            
            # Determine if it was today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            time_str = "today " + end_time.strftime("%H:%M") if end_time >= today_start else end_time.strftime("%Y-%m-%d %H:%M")
            
            console.print("[bold]Last session:[/bold]")
            console.print(f"  {session_type} — {duration} min ({state}) — {time_str}")
            console.print()
        
        # Today's stats
        stats = self.db.get_todays_stats()
        streak = self.db.calculate_current_streak()
        
        console.print("[bold]Today:[/bold]")
        console.print(f"  Focused: {format_duration(stats['total_work_minutes'])}")
        console.print(f"  Breaks: {format_duration(stats['total_break_minutes'])}")
        console.print(f"  Sessions: {stats['session_count']}")
        console.print(f"  Streak: {streak}")
        console.print()
        
        # Next steps
        console.print("[bold]Next:[/bold]")
        console.print("  [cyan]lockin 30[/cyan]")
        console.print("  [cyan]lockin break[/cyan]")
        console.print("  [cyan]lockin stats[/cyan]")
    
    def show_running_session(self, state: dict, interactive: bool = True):
        """Display running session UI."""
        console.clear()
        
        session_type = state['session_type']
        start_time = state['start_time']
        planned_end = state['planned_end_time']
        planned_duration = state['planned_duration_minutes']
        session_state = state['session_state']
        
        now = time.time()
        elapsed = now - start_time
        
        # Calculate time remaining
        if session_state == SessionState.RUNNING:
            remaining = max(0, planned_end - now)
            time_label = "remaining"
        elif session_state == SessionState.AWAITING_DECISION:
            decision_start = state['decision_window_start']
            decision_window = self.config.decision_window_minutes * 60
            remaining = max(0, decision_window - (now - decision_start))
            time_label = "to decide"
        else:  # RUNNING_BONUS
            remaining = now - planned_end
            time_label = "bonus time"
        
        # Header
        type_display = session_type
        if session_type == SessionType.BREAK:
            # Determine if short or long break
            if planned_duration == self.config.short_break_minutes:
                type_display = "break (short)"
            elif planned_duration == self.config.long_break_minutes:
                type_display = "break (long)"
            else:
                type_display = f"break ({planned_duration}m)"
        
        console.print(Panel.fit(
            f"[bold cyan]LOCKIN[/bold cyan] — {type_display}",
            border_style="cyan"
        ))
        console.print()
        
        # Time remaining
        if session_state in [SessionState.RUNNING, SessionState.AWAITING_DECISION]:
            time_str = format_time_remaining(remaining)
            console.print(f"[bold green]{time_str}[/bold green] {time_label}", justify="center")
        else:
            time_str = format_time_remaining(remaining)
            console.print(f"[bold yellow]+{time_str}[/bold yellow] {time_label}", justify="center")
        
        # Progress bar
        if session_state == SessionState.RUNNING:
            progress_pct = min(100, (elapsed / (planned_duration * 60)) * 100)
        elif session_state == SessionState.AWAITING_DECISION:
            decision_elapsed = now - state['decision_window_start']
            decision_window = self.config.decision_window_minutes * 60
            progress_pct = 100 - min(100, (decision_elapsed / decision_window) * 100)
        else:
            progress_pct = 100
        
        bar_length = 40
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "▌" * (1 if progress_pct % (100/bar_length) > 0 and filled < bar_length else 0)
        console.print(f"[cyan]{bar}[/cyan]")
        console.print()
        
        # Session details
        start_dt = datetime.fromtimestamp(start_time)
        console.print(f"[dim]Started: {start_dt.strftime('%H:%M')}[/dim]")
        console.print(f"[dim]Planned: {planned_duration} min[/dim]")
        console.print(f"[dim]Elapsed: {format_time_remaining(elapsed)}[/dim]")
        console.print()
        
        # Today's stats
        stats = self.db.get_todays_stats()
        streak = self.db.calculate_current_streak()
        console.print(
            f"[dim]Today: {format_duration(stats['total_work_minutes'])} focused · "
            f"{stats['session_count']} sessions · streak {streak}[/dim]"
        )
        console.print()
        
        # Controls
        if interactive:
            if session_state == SessionState.AWAITING_DECISION:
                self._show_decision_controls(state)
            elif session_state == SessionState.RUNNING:
                if session_type == SessionType.WORK:
                    # Show "scrap" if below abandon threshold, "end early" if above
                    abandon_threshold_minutes = self.config.abandon_threshold_minutes
                    elapsed_minutes = elapsed / 60
                    if elapsed_minutes < abandon_threshold_minutes:
                        console.print("[dim]\\[q] quit (scrap)   \\[d] detach[/dim]")
                    else:
                        console.print("[dim]\\[q] quit (end early)   \\[d] detach[/dim]")
                else:  # Break
                    console.print("[dim]\\[q] end break   \\[s] switch to short   \\[l] switch to long   \\[d] detach[/dim]")
            elif session_state == SessionState.RUNNING_BONUS:
                if session_type == SessionType.WORK:
                    console.print("[dim]\\[q] quit (end)   \\[b/B] break (short/custom)   \\[d] detach[/dim]")
                else:
                    console.print("[dim]\\[q] end break   \\[d] detach[/dim]")
            console.print()  # Extra newline before cursor

    def _prompt_custom_break_duration(self, old_settings) -> Optional[int]:
        """Prompt user for custom break duration. Returns duration in minutes or None if cancelled."""
        import termios

        # Restore terminal to normal mode for input
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

        try:
            console.print("\n[cyan]Enter break duration in minutes (or press Enter to cancel):[/cyan] ", end="")
            user_input = input().strip()

            if not user_input:
                return None

            try:
                duration = int(user_input)
                if duration < 1:
                    console.print("[red]Duration must be at least 1 minute[/red]")
                    time.sleep(1)
                    return None
                if duration > 1440:
                    console.print("[red]Duration cannot exceed 1440 minutes (24 hours)[/red]")
                    time.sleep(1)
                    return None
                return duration
            except ValueError:
                console.print("[red]Invalid number[/red]")
                time.sleep(1)
                return None
        finally:
            # Return to raw mode
            import tty
            tty.setcbreak(sys.stdin.fileno())

    def _show_decision_controls(self, state: dict):
        """Show decision window controls."""
        session_type = state['session_type']
        
        if session_type == SessionType.WORK:
            streak = self.db.calculate_current_streak()
            long_break_every = self.config.long_break_every
            
            if streak > 0 and streak % long_break_every == 0:
                break_label = "long"
            else:
                break_label = "short"
            
            console.print(f"[dim]\\[q] quit (end)   \\[b/B] break ({break_label}/custom)   \\[c] continue   \\[d] detach[/dim]")
            
            # Show countdown
            now = time.time()
            decision_start = state['decision_window_start']
            decision_window = self.config.decision_window_minutes * 60
            remaining = max(0, decision_window - (now - decision_start))
            console.print(f"[dim]Defaulting to continue in {format_time_remaining(remaining)}[/dim]")
        else:
            console.print("[dim]\\[q] end break   \\[d] detach[/dim]")

    def attach_to_session(self):
        """Attach to running session with live updates."""
        import select
        import termios
        import tty
        
        # Set terminal to raw mode for immediate key detection
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            while True:
                state = self.get_current_state()
                
                if not state or state['session_state'] in [SessionState.IDLE, SessionState.ENDED]:
                    console.print("\n[yellow]Session ended[/yellow]")
                    break
                
                self.show_running_session(state, interactive=True)
                
                # Check for keyboard input (non-blocking)
                if select.select([sys.stdin], [], [], 1)[0]:
                    raw_key = sys.stdin.read(1)
                    key = raw_key.lower()

                    session_state = state['session_state']
                    session_type = state['session_type']

                    if key == 'q':
                        self.queue_command('quit_session')
                        time.sleep(0.5)  # Wait for processing
                        break
                    elif key == 'd':
                        console.print("\n[dim]Detached. Session continues in background.[/dim]")
                        break
                    elif key == 'c' and session_state == SessionState.AWAITING_DECISION:
                        self.queue_command('continue_session')
                    elif raw_key == 'B' and session_state in [SessionState.AWAITING_DECISION, SessionState.RUNNING_BONUS]:
                        # Custom break duration - prompt user
                        if session_type == SessionType.WORK:
                            duration = self._prompt_custom_break_duration(old_settings)
                            if duration:
                                self.queue_command('quit_session')
                                time.sleep(0.5)
                                self.queue_command('start_session',
                                                 session_type='break',
                                                 duration_minutes=duration)
                    elif key == 'b' and session_state in [SessionState.AWAITING_DECISION, SessionState.RUNNING_BONUS]:
                        # Start recommended break
                        if session_type == SessionType.WORK:
                            self.queue_command('quit_session')
                            time.sleep(0.5)

                            # Determine break type
                            streak = self.db.calculate_current_streak()
                            if streak % self.config.long_break_every == 0:
                                duration = self.config.long_break_minutes
                            else:
                                duration = self.config.short_break_minutes

                            self.queue_command('start_session',
                                             session_type='break',
                                             duration_minutes=duration)
                    elif key == 's' and session_type == SessionType.BREAK:
                        self.queue_command('switch_break', break_type='short')
                    elif key == 'l' and session_type == SessionType.BREAK:
                        self.queue_command('switch_break', break_type='long')
                
                time.sleep(1)  # Update every second
        
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def show_stats(self, period: str, date_arg: Optional[str] = None):
        """Display statistics for a period."""
        console.clear()
        
        # Parse date and determine range
        today = datetime.now()
        
        try:
            if period == 'week':
                if date_arg:
                    # Parse DDMMYY
                    try:
                        ref_date = datetime.strptime(date_arg, '%d%m%y')
                    except ValueError:
                        console.print(f"[red]Invalid date format: {date_arg}[/red]")
                        console.print("[dim]Expected format: DDMMYY (e.g., 150124 for Jan 15, 2024)[/dim]")
                        return
                else:
                    ref_date = today
                
                # Get week start (Monday)
                start_date = ref_date - timedelta(days=ref_date.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
                title = f"Week of {start_date.strftime('%b %d, %Y')}"
            
            elif period == 'month':
                if date_arg:
                    try:
                        ref_date = datetime.strptime(date_arg, '%d%m%y')
                    except ValueError:
                        console.print(f"[red]Invalid date format: {date_arg}[/red]")
                        console.print("[dim]Expected format: DDMMYY (e.g., 150124 for Jan 15, 2024)[/dim]")
                        return
                else:
                    ref_date = today
                
                start_date = ref_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # Get next month
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1)
                title = start_date.strftime('%B %Y')
            
            elif period == 'year':
                if date_arg:
                    try:
                        year = int(date_arg)
                        if year < 1900 or year > 9999:
                            raise ValueError("Year out of range")
                    except ValueError:
                        console.print(f"[red]Invalid year: {date_arg}[/red]")
                        console.print("[dim]Expected format: YYYY (e.g., 2024)[/dim]")
                        return
                else:
                    year = today.year
                
                start_date = datetime(year, 1, 1)
                end_date = datetime(year + 1, 1, 1)
                title = str(year)
            
            else:
                console.print("[red]Invalid period[/red]")
                console.print("[dim]Valid periods: week, month, year[/dim]")
                return
                
        except Exception as e:
            console.print(f"[red]Error parsing date: {e}[/red]")
            return
        
        # Get sessions
        sessions = self.db.get_sessions_by_date_range(start_date, end_date)
        
        # Header
        console.print(Panel.fit(
            f"[bold cyan]LOCKIN[/bold cyan] — Stats: {title}",
            border_style="cyan"
        ))
        console.print()
        
        if not sessions:
            console.print("[dim]No sessions in this period[/dim]")
            return
        
        # Calculate statistics
        total_work_completed = 0
        total_work_abandoned = 0
        total_break = 0
        
        completed_sessions = 0
        abandoned_sessions = 0
        
        for session in sessions:
            duration = session['actual_duration_minutes'] or 0
            
            if session['session_type'] == 'work':
                if session['state'] == 'completed':
                    total_work_completed += duration
                    completed_sessions += 1
                elif session['state'] == 'abandoned':
                    total_work_abandoned += duration
                    abandoned_sessions += 1
            elif session['session_type'] == 'break':
                total_break += duration
        
        # Summary table
        table = Table(show_header=True, box=box.ROUNDED, border_style="cyan")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        
        table.add_row("Focused (completed)", f"[green]{format_duration(total_work_completed)}[/green]")
        if total_work_abandoned > 0:
            table.add_row("Focused (abandoned)", f"[yellow]{format_duration(total_work_abandoned)}[/yellow]")
        table.add_row("Break time", format_duration(total_break))
        table.add_row("Completed sessions", f"[green]{completed_sessions}[/green]")
        if abandoned_sessions > 0:
            table.add_row("Abandoned sessions", f"[yellow]{abandoned_sessions}[/yellow]")
        
        console.print(table)
        console.print()
        
        # Breakdown for week/month
        if period == 'week':
            console.print("[bold]Daily breakdown:[/bold]")
            console.print()
            
            # Group by day
            daily_stats = {}
            current = start_date
            
            while current < end_date:
                day_key = current.strftime('%Y-%m-%d')
                daily_stats[day_key] = {'work': 0, 'sessions': 0}
                current += timedelta(days=1)
            
            for session in sessions:
                if session['session_type'] == 'work' and session['state'] == 'completed':
                    day_key = datetime.fromtimestamp(session['start_time']).strftime('%Y-%m-%d')
                    if day_key in daily_stats:
                        daily_stats[day_key]['work'] += session['actual_duration_minutes']
                        daily_stats[day_key]['sessions'] += 1
            
            # Display bar chart
            max_minutes = max(120, max([d['work'] for d in daily_stats.values()])) if daily_stats else 120
            
            for day_key in sorted(daily_stats.keys()):
                stats = daily_stats[day_key]
                day_dt = datetime.strptime(day_key, '%Y-%m-%d')
                day_label = day_dt.strftime('%a %d')
                
                minutes = stats['work']
                sessions = stats['sessions']
                
                # Create bar
                if max_minutes > 0:
                    bar_length = int((minutes / max_minutes) * 30)
                    bar = "█" * bar_length
                else:
                    bar = ""
                
                if minutes > 0:
                    console.print(f"{day_label:10} {format_duration(minutes):>7} ({sessions} sessions)  [cyan]{bar}[/cyan]")
                else:
                    console.print(f"{day_label:10} [dim]—[/dim]")
        
        elif period == 'month':
            console.print("[bold]Weekly breakdown:[/bold]")
            console.print()
            
            # Group by week (Monday start)
            weekly_stats = {}
            current = start_date
            
            while current < end_date:
                # Get Monday of this week
                week_start = current - timedelta(days=current.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                if week_key not in weekly_stats:
                    weekly_stats[week_key] = {'work': 0, 'sessions': 0}
                current += timedelta(days=1)
            
            for session in sessions:
                if session['session_type'] == 'work' and session['state'] == 'completed':
                    session_date = datetime.fromtimestamp(session['start_time'])
                    week_start = session_date - timedelta(days=session_date.weekday())
                    week_key = week_start.strftime('%Y-%m-%d')
                    if week_key in weekly_stats:
                        weekly_stats[week_key]['work'] += session['actual_duration_minutes']
                        weekly_stats[week_key]['sessions'] += 1
            
            # Display bar chart
            max_minutes = max(120, max([d['work'] for d in weekly_stats.values()])) if weekly_stats else 120
            
            for week_key in sorted(weekly_stats.keys()):
                stats = weekly_stats[week_key]
                week_dt = datetime.strptime(week_key, '%Y-%m-%d')
                week_end = week_dt + timedelta(days=6)
                week_label = f"{week_dt.strftime('%b %d')}-{week_end.strftime('%d')}"
                
                minutes = stats['work']
                sessions = stats['sessions']
                
                # Create bar
                if max_minutes > 0:
                    bar_length = int((minutes / max_minutes) * 30)
                    bar = "█" * bar_length
                else:
                    bar = ""
                
                if minutes > 0:
                    console.print(f"{week_label:12} {format_duration(minutes):>7} ({sessions:>2} sessions)  [cyan]{bar}[/cyan]")
                else:
                    console.print(f"{week_label:12} [dim]—[/dim]")
    
    def show_config(self):
        """Display current configuration."""
        console.clear()
        
        console.print(Panel.fit(
            "[bold cyan]LOCKIN[/bold cyan] — Configuration",
            border_style="cyan"
        ))
        console.print()
        
        config = self.config.get_all()
        
        table = Table(show_header=True, box=box.ROUNDED, border_style="cyan")
        table.add_column("Setting", style="bold")
        table.add_column("Value", justify="right")
        
        for key in sorted(config.keys()):
            value = config[key]
            table.add_row(key, str(value))
        
        console.print(table)
        console.print()
        console.print("[dim]To change: lockin config <key> <value>[/dim]")
        console.print("[dim]To reset: lockin config reset[/dim]")
