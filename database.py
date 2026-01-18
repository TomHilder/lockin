"""Database layer for Lockin - SQLite persistence."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class Database:
    """SQLite database manager for Lockin."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema."""
        with self.connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,  -- 'work' or 'break'
                    state TEXT NOT NULL,  -- 'completed', 'abandoned', 'overtime'
                    start_time REAL NOT NULL,
                    end_time REAL,
                    planned_duration_minutes INTEGER NOT NULL,
                    actual_duration_minutes REAL,
                    overtime_minutes REAL DEFAULT 0,
                    created_at REAL NOT NULL DEFAULT (unixepoch('subsec'))
                );
                
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL DEFAULT (unixepoch('subsec'))
                );
                
                CREATE TABLE IF NOT EXISTS engine_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    current_state TEXT,  -- JSON serialized state
                    updated_at REAL NOT NULL DEFAULT (unixepoch('subsec'))
                );
                
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    args TEXT,  -- JSON
                    created_at REAL NOT NULL DEFAULT (unixepoch('subsec')),
                    processed INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
                    ON sessions(start_time);
                CREATE INDEX IF NOT EXISTS idx_sessions_type_state 
                    ON sessions(session_type, state);
                CREATE INDEX IF NOT EXISTS idx_commands_processed 
                    ON commands(processed, created_at);
            """)
    
    # Session methods
    
    def log_session(self, session_type: str, state: str, start_time: float,
                    end_time: float, planned_duration_minutes: int,
                    actual_duration_minutes: float, bonus_minutes: float = 0):
        """Log a completed/abandoned session."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO sessions (
                    session_type, state, start_time, end_time,
                    planned_duration_minutes, actual_duration_minutes,
                    overtime_minutes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_type, state, start_time, end_time,
                  planned_duration_minutes, actual_duration_minutes,
                  bonus_minutes))  # Pass bonus_minutes to overtime_minutes field for DB compatibility
    
    def get_sessions_by_date_range(self, start_date: datetime, 
                                   end_date: datetime) -> List[Dict[str, Any]]:
        """Get all sessions within a date range."""
        with self.connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM sessions
                WHERE start_time >= ? AND start_time < ?
                ORDER BY start_time ASC
            """, (start_date.timestamp(), end_date.timestamp()))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_last_session(self) -> Optional[Dict[str, Any]]:
        """Get the most recent session."""
        with self.connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM sessions
                ORDER BY start_time DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_todays_stats(self) -> Dict[str, Any]:
        """Get today's session statistics."""
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        with self.connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    session_type,
                    state,
                    SUM(actual_duration_minutes) as total_minutes,
                    COUNT(*) as count
                FROM sessions
                WHERE start_time >= ?
                GROUP BY session_type, state
            """, (today_start.timestamp(),))
            
            results = cursor.fetchall()
            
            stats = {
                'work_completed': 0,
                'work_abandoned': 0,
                'break_completed': 0,
                'total_work_minutes': 0,
                'total_break_minutes': 0,
                'session_count': 0
            }
            
            for row in results:
                session_type = row['session_type']
                state = row['state']
                minutes = row['total_minutes'] or 0
                count = row['count']
                
                if session_type == 'work':
                    stats['total_work_minutes'] += minutes
                    if state == 'completed':
                        stats['work_completed'] += count
                        stats['session_count'] += count
                    elif state == 'abandoned':
                        stats['work_abandoned'] += count
                elif session_type == 'break':
                    stats['total_break_minutes'] += minutes
                    if state == 'completed':
                        stats['break_completed'] += count
            
            return stats
    
    def calculate_current_streak(self) -> int:
        """Calculate current streak of completed work sessions."""
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        with self.connection() as conn:
            cursor = conn.execute("""
                SELECT end_time
                FROM sessions
                WHERE session_type = 'work' 
                  AND state = 'completed'
                  AND start_time >= ?
                ORDER BY end_time ASC
            """, (today_start.timestamp(),))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                return 0
            
            streak = 1
            for i in range(1, len(sessions)):
                prev_end = sessions[i-1]['end_time']
                curr_end = sessions[i]['end_time']
                gap_minutes = (curr_end - prev_end) / 60
                
                # Streak continues if gap < 60 minutes
                if gap_minutes < 60:
                    streak += 1
                else:
                    # Reset streak, start counting from this session
                    streak = 1
            
            return streak
    
    # Config methods
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        with self.connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['value'])
                except json.JSONDecodeError:
                    return row['value']
            return default
    
    def set_config(self, key: str, value: Any):
        """Set a config value."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO config (key, value, updated_at)
                VALUES (?, ?, unixepoch('subsec'))
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (key, json.dumps(value) if not isinstance(value, str) else value))
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all config values."""
        with self.connection() as conn:
            cursor = conn.execute("SELECT key, value FROM config")
            config = {}
            for row in cursor.fetchall():
                try:
                    config[row['key']] = json.loads(row['value'])
                except json.JSONDecodeError:
                    config[row['key']] = row['value']
            return config
    
    def reset_config(self):
        """Clear all config (will be repopulated with defaults)."""
        with self.connection() as conn:
            conn.execute("DELETE FROM config")
    
    # Engine state methods
    
    def get_engine_state(self) -> Optional[Dict[str, Any]]:
        """Get current engine state."""
        with self.connection() as conn:
            cursor = conn.execute(
                "SELECT current_state FROM engine_state WHERE id = 1"
            )
            row = cursor.fetchone()
            if row and row['current_state']:
                return json.loads(row['current_state'])
            return None
    
    def set_engine_state(self, state: Dict[str, Any]):
        """Set engine state."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO engine_state (id, current_state, updated_at)
                VALUES (1, ?, unixepoch('subsec'))
                ON CONFLICT(id) DO UPDATE SET
                    current_state = excluded.current_state,
                    updated_at = excluded.updated_at
            """, (json.dumps(state),))
    
    def clear_engine_state(self):
        """Clear engine state."""
        with self.connection() as conn:
            conn.execute("DELETE FROM engine_state WHERE id = 1")
    
    # Command queue methods
    
    def queue_command(self, command: str, args: Optional[Dict[str, Any]] = None):
        """Queue a command for the engine."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO commands (command, args)
                VALUES (?, ?)
            """, (command, json.dumps(args) if args else None))
    
    def get_pending_commands(self) -> List[Dict[str, Any]]:
        """Get all unprocessed commands."""
        with self.connection() as conn:
            cursor = conn.execute("""
                SELECT id, command, args, created_at
                FROM commands
                WHERE processed = 0
                ORDER BY created_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_command_processed(self, command_id: int):
        """Mark a command as processed."""
        with self.connection() as conn:
            conn.execute(
                "UPDATE commands SET processed = 1 WHERE id = ?",
                (command_id,)
            )
    
    def cleanup_old_commands(self, days: int = 7):
        """Delete processed commands older than specified days."""
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        with self.connection() as conn:
            conn.execute("""
                DELETE FROM commands
                WHERE processed = 1 AND created_at < ?
            """, (cutoff,))
