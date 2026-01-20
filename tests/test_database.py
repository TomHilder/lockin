"""Tests for Lockin database layer."""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from lockin.database import Database
from lockin.config import Config


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = Path(f.name)

    db = Database(db_path)
    yield db

    # Cleanup
    db_path.unlink()


def test_database_initialization(temp_db):
    """Test that database initializes correctly."""
    # Should be able to get config
    config = Config(temp_db)
    assert config.short_break_minutes == 5
    assert config.long_break_minutes == 15


def test_session_logging(temp_db):
    """Test logging sessions."""
    now = datetime.now().timestamp()

    temp_db.log_session(
        session_type="work",
        state="completed",
        start_time=now - 1800,  # 30 minutes ago
        end_time=now,
        planned_duration_minutes=30,
        actual_duration_minutes=30,
    )

    last_session = temp_db.get_last_session()
    assert last_session is not None
    assert last_session["session_type"] == "work"
    assert last_session["state"] == "completed"


def test_streak_calculation(temp_db):
    """Test streak calculation."""
    now = datetime.now()
    base_time = now.timestamp()

    # Log 3 sessions with < 1 hour gaps
    for i in range(3):
        start = base_time + (i * 1800)  # 30 min apart
        end = start + 1500  # 25 min duration

        temp_db.log_session(
            session_type="work",
            state="completed",
            start_time=start,
            end_time=end,
            planned_duration_minutes=25,
            actual_duration_minutes=25,
        )

    streak = temp_db.calculate_current_streak()
    assert streak == 3


def test_todays_stats(temp_db):
    """Test today's statistics."""
    now = datetime.now().timestamp()

    # Log a work session
    temp_db.log_session(
        session_type="work",
        state="completed",
        start_time=now - 1800,
        end_time=now,
        planned_duration_minutes=30,
        actual_duration_minutes=30,
    )

    stats = temp_db.get_todays_stats()
    assert stats["total_work_minutes"] == 30
    assert stats["session_count"] == 1


def test_config_management(temp_db):
    """Test configuration management."""
    config = Config(temp_db)

    # Test getting default
    assert config.short_break_minutes == 5

    # Test setting
    config.set("short_break_minutes", 10)
    assert config.get("short_break_minutes") == 10

    # Test reset
    config.reset()
    assert config.short_break_minutes == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
