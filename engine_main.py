"""Entry point for Lockin background engine."""

import sys
from pathlib import Path

from lockin.engine import Engine


def get_db_path() -> Path:
    """Get database path."""
    data_dir = Path.home() / '.lockin'
    data_dir.mkdir(exist_ok=True)
    return data_dir / 'lockin.db'


def main():
    """Run the engine."""
    db_path = get_db_path()
    engine = Engine(db_path)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nEngine stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()
