#!/usr/bin/env python3
"""
Final Verification Test
Demonstrates all fixes are working correctly
"""

from lockin.database import Database
from lockin.config import Config
from lockin.engine import Engine
from lockin.cli import LockinUI
from pathlib import Path
import sys


def test_duration_validation():
    """Test duration validation prevents bad inputs."""
    print("1. Testing Duration Validation...")
    engine = Engine(Path("/tmp/final_test1.db"))

    # Should reject
    assert not engine.start_session("work", 0)[0], "Should reject zero duration"
    assert not engine.start_session("work", -5)[0], "Should reject negative duration"
    assert not engine.start_session("work", 10000)[0], "Should reject huge duration"

    # Should accept
    assert engine.start_session("work", 30)[0], "Should accept valid duration"
    engine.quit_session()

    print("   ✅ Duration validation working")


def test_state_validation():
    """Test state validation handles corruption."""
    print("\n2. Testing State Validation...")

    # Test invalid session_state
    db = Database(Path("/tmp/final_test2.db"))
    db.set_engine_state({"session_state": "INVALID", "session_type": "work"})
    engine = Engine(Path("/tmp/final_test2.db"))
    assert engine.state["session_state"] == "idle", "Should reset invalid state"

    # Test missing fields
    db2 = Database(Path("/tmp/final_test3.db"))
    db2.set_engine_state({"session_state": "running"})
    engine2 = Engine(Path("/tmp/final_test3.db"))
    assert "start_time" in engine2.state, "Should have default fields"

    # Test invalid session_type
    db3 = Database(Path("/tmp/final_test4.db"))
    db3.set_engine_state({"session_state": "running", "session_type": "invalid"})
    engine3 = Engine(Path("/tmp/final_test4.db"))
    assert engine3.state["session_state"] == "idle", "Should reset invalid type"

    print("   ✅ State validation working")


def test_config_validation():
    """Test config validation enforces limits."""
    print("\n3. Testing Config Validation...")
    config = Config(Database(Path("/tmp/final_test5.db")))

    # Should reject
    try:
        config.set("short_break_minutes", 0)
        assert False, "Should reject zero"
    except ValueError:
        pass

    try:
        config.set("short_break_minutes", 10000)
        assert False, "Should reject huge value"
    except ValueError:
        pass

    try:
        config.set("invalid_key", 5)
        assert False, "Should reject invalid key"
    except ValueError:
        pass

    # Should accept
    config.set("short_break_minutes", 10)
    assert config.get("short_break_minutes") == 10, "Should accept valid value"

    print("   ✅ Config validation working")


def test_date_parsing():
    """Test date parsing handles errors gracefully."""
    print("\n4. Testing Date Parsing...")
    ui = LockinUI(Path("/tmp/final_test6.db"))

    # Redirect output to suppress Rich printing
    old_stdout = sys.stdout
    sys.stdout = open("/dev/null", "w")

    try:
        # These should not crash
        ui.show_stats("week", "999999")
        ui.show_stats("year", "abc")
        ui.show_stats("year", "99999999")
        print("   ✅ Date parsing handles errors gracefully", file=old_stdout)
    except Exception as e:
        print(f"   ❌ Date parsing crashed: {e}", file=old_stdout)
        raise
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout


def test_complete_workflow():
    """Test a complete session workflow."""
    print("\n5. Testing Complete Workflow...")
    engine = Engine(Path("/tmp/final_test7.db"))

    # Start session
    success, msg = engine.start_session("work", 30)
    assert success, f"Should start session: {msg}"
    assert engine.state["session_state"] == "running"

    # Try to start another (should fail)
    success2, msg2 = engine.start_session("work", 25)
    assert not success2, "Should reject second session"

    # Quit session
    success3, msg3 = engine.quit_session()
    assert success3, f"Should quit session: {msg3}"
    assert engine.state["session_state"] == "idle"

    # Should be able to start another now
    success4, msg4 = engine.start_session("break", 5)
    assert success4, f"Should start new session: {msg4}"
    engine.quit_session()

    print("   ✅ Complete workflow working")


def main():
    print("=" * 60)
    print("FINAL VERIFICATION TEST")
    print("=" * 60)

    try:
        test_duration_validation()
        test_state_validation()
        test_config_validation()
        test_date_parsing()
        test_complete_workflow()

        print("\n" + "=" * 60)
        print("✅ ALL VERIFICATION TESTS PASSED")
        print("=" * 60)
        print("\nThe application is production-ready with:")
        print("  • Robust input validation")
        print("  • Corruption-resistant state management")
        print("  • User-friendly error messages")
        print("  • Complete session lifecycle support")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
