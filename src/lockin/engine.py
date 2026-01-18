"""Background engine for Lockin - persistent state manager and timer."""

import time
import json
import subprocess
from datetime import datetime
from enum import Enum
from typing import Dict, Any
from pathlib import Path

from .database import Database
from .config import Config


class SessionState(str, Enum):
    """Session states."""
    IDLE = "idle"
    RUNNING = "running"
    AWAITING_DECISION = "awaiting_decision"
    RUNNING_BONUS = "running_bonus"
    ENDED = "ended"


class SessionType(str, Enum):
    """Session types."""
    WORK = "work"
    BREAK = "break"


class Engine:
    """Background engine managing session state and timing."""
    
    def __init__(self, db_path: Path):
        self.db = Database(db_path)
        self.config = Config(self.db)
        self.state = self._load_state()
        self.last_midnight_check = datetime.now().date()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from database or initialize fresh."""
        saved_state = self.db.get_engine_state()
        
        # Default state
        default_state = {
            'session_state': SessionState.IDLE,
            'session_type': None,
            'start_time': None,
            'planned_end_time': None,
            'planned_duration_minutes': None,
            'decision_window_start': None,
            'last_notification': None,
        }
        
        if not saved_state:
            return default_state
        
        # Validate and sanitize loaded state
        try:
            # Validate session_state
            state_value = saved_state.get('session_state', SessionState.IDLE)
            # Check if it's a valid SessionState
            valid_states = [s.value for s in SessionState]
            if state_value not in valid_states:
                print(f"Warning: Invalid session_state '{state_value}', resetting to idle")
                saved_state['session_state'] = SessionState.IDLE
                saved_state['session_type'] = None
                saved_state['start_time'] = None
                saved_state['planned_end_time'] = None
                saved_state['planned_duration_minutes'] = None
                saved_state['decision_window_start'] = None
            
            # Validate session_type
            if saved_state.get('session_type') not in [None, SessionType.WORK, SessionType.BREAK, 'work', 'break']:
                print(f"Warning: Invalid session_type '{saved_state.get('session_type')}', resetting to idle")
                saved_state['session_state'] = SessionState.IDLE
                saved_state['session_type'] = None
            
            # Merge with defaults to ensure all fields exist
            result = default_state.copy()
            result.update(saved_state)
            return result
            
        except Exception as e:
            print(f"Warning: Error loading state: {e}, using defaults")
            return default_state
    
    def _save_state(self):
        """Persist current state to database."""
        self.db.set_engine_state(self.state)
    
    def _send_notification(self, title: str, message: str):
        """Send macOS notification."""
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ], check=False, capture_output=True)
            self.state['last_notification'] = time.time()
        except Exception:
            pass  # Notifications are non-critical
    
    def _check_midnight_reset(self):
        """Check if midnight has passed and reset streak if needed."""
        current_date = datetime.now().date()
        if current_date > self.last_midnight_check:
            self.last_midnight_check = current_date
    
    def start_session(self, session_type: str, duration_minutes: int):
        """Start a new work or break session."""
        if self.state['session_state'] not in [SessionState.IDLE, SessionState.ENDED]:
            return False, "Session already in progress"
        
        # Validate duration
        if duration_minutes <= 0:
            return False, "Duration must be positive"
        if duration_minutes > 1440:  # 24 hours
            return False, "Duration cannot exceed 24 hours (1440 minutes)"
        
        # Validate session type
        if session_type not in [SessionType.WORK, SessionType.BREAK]:
            return False, f"Invalid session type: {session_type}"
        
        now = time.time()
        planned_end = now + (duration_minutes * 60)
        
        self.state.update({
            'session_state': SessionState.RUNNING,
            'session_type': session_type,
            'start_time': now,
            'planned_end_time': planned_end,
            'planned_duration_minutes': duration_minutes,
            'decision_window_start': None,
            'last_notification': None,
        })
        
        self._save_state()
        return True, f"Started {session_type} session for {duration_minutes} minutes"
    
    def quit_session(self):
        """Quit the current session."""
        if self.state['session_state'] == SessionState.IDLE:
            return False, "No active session"
        
        now = time.time()
        start_time = self.state['start_time']
        planned_duration = self.state['planned_duration_minutes']
        actual_duration_minutes = (now - start_time) / 60
        session_type = self.state['session_type']
        current_state = self.state['session_state']
        
        # Determine if session should be logged
        should_log = False
        log_state = None
        bonus_minutes = 0
        
        if session_type == SessionType.WORK:
            threshold = self.config.abandon_threshold_minutes
            
            # If we're in bonus time or awaiting_decision, we already completed the planned time
            if current_state in [SessionState.RUNNING_BONUS, SessionState.AWAITING_DECISION]:
                should_log = True
                log_state = 'completed'
                bonus_minutes = max(0, actual_duration_minutes - planned_duration)
            elif actual_duration_minutes >= threshold:
                should_log = True
                
                # Check if we reached planned end
                if now >= self.state['planned_end_time']:
                    log_state = 'completed'
                    bonus_minutes = max(0, actual_duration_minutes - planned_duration)
                else:
                    log_state = 'abandoned'
        
        elif session_type == SessionType.BREAK:
            threshold = self.config.break_scrap_threshold_minutes
            
            # Similar logic for breaks
            if current_state in [SessionState.RUNNING_BONUS, SessionState.AWAITING_DECISION]:
                should_log = True
                log_state = 'completed'
            elif actual_duration_minutes >= threshold:
                should_log = True
                
                if now >= self.state['planned_end_time']:
                    log_state = 'completed'
                else:
                    log_state = 'ended_early'
        
        # Log if appropriate
        if should_log:
            self.db.log_session(
                session_type=session_type,
                state=log_state,
                start_time=start_time,
                end_time=now,
                planned_duration_minutes=planned_duration,
                actual_duration_minutes=actual_duration_minutes,
                bonus_minutes=bonus_minutes
            )
        
        # Reset to idle
        self.state.update({
            'session_state': SessionState.IDLE,
            'session_type': None,
            'start_time': None,
            'planned_end_time': None,
            'planned_duration_minutes': None,
            'decision_window_start': None,
        })
        
        self._save_state()
        return True, "Session ended"
    
    def continue_session(self):
        """Continue session into bonus time."""
        if self.state['session_state'] != SessionState.AWAITING_DECISION:
            return False, "Not in decision window"
        
        self.state['session_state'] = SessionState.RUNNING_BONUS
        self._save_state()
        return True, "Continuing session"
    
    def switch_break_type(self, break_type: str) -> tuple[bool, str]:
        """Switch between short and long break."""
        if self.state['session_type'] != SessionType.BREAK:
            return False, "Not in a break session"
        
        if self.state['session_state'] not in [SessionState.RUNNING, SessionState.RUNNING_BONUS]:
            return False, "Break not running"
        
        now = time.time()
        elapsed_minutes = (now - self.state['start_time']) / 60
        
        # Check switching rules
        short_duration = self.config.short_break_minutes
        long_duration = self.config.long_break_minutes
        
        if break_type == 'short':
            # Can only switch to short before short duration elapsed
            if elapsed_minutes >= short_duration:
                return False, "Too late to switch to short break"
            new_duration = short_duration
        elif break_type == 'long':
            # Can always switch to long (if not already past long duration)
            if elapsed_minutes >= long_duration:
                return False, "Long break duration already elapsed"
            new_duration = long_duration
        else:
            return False, "Invalid break type"
        
        # Update planned end time
        self.state['planned_end_time'] = self.state['start_time'] + (new_duration * 60)
        self.state['planned_duration_minutes'] = new_duration
        self._save_state()
        
        return True, f"Switched to {break_type} break"
    
    def get_recommended_break_type(self) -> str:
        """Get recommended break type based on streak."""
        streak = self.db.calculate_current_streak()
        long_break_every = self.config.long_break_every
        
        if streak > 0 and streak % long_break_every == 0:
            return 'long'
        return 'short'
    
    def tick(self):
        """Main engine tick - called periodically to check timers."""
        self._check_midnight_reset()
        self.config = Config(self.db)  # Reload config
        
        if self.state['session_state'] == SessionState.RUNNING:
            now = time.time()
            
            # Check if planned time reached
            if now >= self.state['planned_end_time']:
                # Send notification
                session_type = self.state['session_type']
                self._send_notification(
                    f"Lockin - {session_type} complete",
                    f"Your {self.state['planned_duration_minutes']} minute {session_type} session is complete!"
                )
                
                # Enter decision window
                self.state['session_state'] = SessionState.AWAITING_DECISION
                self.state['decision_window_start'] = now
                self._save_state()
        
        elif self.state['session_state'] == SessionState.AWAITING_DECISION:
            now = time.time()
            decision_window = self.config.decision_window_minutes * 60
            
            # Check if decision window expired
            if now - self.state['decision_window_start'] >= decision_window:
                # Auto-continue into bonus time
                self.state['session_state'] = SessionState.RUNNING_BONUS
                self._save_state()
        
        elif self.state['session_state'] == SessionState.RUNNING_BONUS:
            # For breaks, automatically end when long break duration reached
            if self.state['session_type'] == SessionType.BREAK:
                now = time.time()
                elapsed_minutes = (now - self.state['start_time']) / 60
                
                if elapsed_minutes >= self.config.long_break_minutes:
                    # Auto-end break
                    self.quit_session()
    
    def process_commands(self):
        """Process pending commands from CLI."""
        commands = self.db.get_pending_commands()
        
        for cmd in commands:
            command = cmd['command']
            args = json.loads(cmd['args']) if cmd['args'] else {}
            
            if command == 'start_session':
                self.start_session(args['session_type'], args['duration_minutes'])
            elif command == 'quit_session':
                self.quit_session()
            elif command == 'continue_session':
                self.continue_session()
            elif command == 'switch_break':
                self.switch_break_type(args['break_type'])
            
            self.db.mark_command_processed(cmd['id'])
    
    def run(self):
        """Main engine loop."""
        print("Lockin engine started")
        
        while True:
            try:
                self.tick()
                self.process_commands()
                time.sleep(1)  # Tick every second
            except KeyboardInterrupt:
                print("\nLockin engine stopped")
                break
            except Exception as e:
                print(f"Engine error: {e}")
                time.sleep(5)  # Back off on errors
