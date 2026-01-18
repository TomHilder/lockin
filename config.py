"""Configuration management for Lockin."""

from typing import Any, Dict
from pathlib import Path
from .database import Database


DEFAULT_CONFIG = {
    'short_break_minutes': 5,
    'long_break_minutes': 15,
    'long_break_every': 4,  # After every 4th completed work session
    'abandon_threshold_minutes': 5,  # Min time to count as abandoned vs scrapped
    'break_scrap_threshold_minutes': 2,  # Min break time to log
    'decision_window_minutes': 3,  # Time to decide after session completes
}


class Config:
    """Configuration manager for Lockin."""
    
    def __init__(self, db: Database):
        self.db = db
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Ensure all default config keys exist in database."""
        current_config = self.db.get_all_config()
        for key, value in DEFAULT_CONFIG.items():
            if key not in current_config:
                self.db.set_config(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        value = self.db.get_config(key)
        if value is None:
            return DEFAULT_CONFIG.get(key, default)
        return value
    
    def set(self, key: str, value: Any):
        """Set a config value."""
        # Validate key exists
        if key not in DEFAULT_CONFIG:
            raise ValueError(f"Unknown configuration key: {key}")
        
        # Validate that numeric values are positive and reasonable
        if key in DEFAULT_CONFIG and isinstance(DEFAULT_CONFIG[key], (int, float)):
            try:
                num_value = float(value)
                if num_value <= 0:
                    raise ValueError(f"{key} must be positive")
                
                # Set reasonable maximums
                if key.endswith('_minutes'):
                    if num_value > 1440:  # 24 hours
                        raise ValueError(f"{key} cannot exceed 1440 minutes (24 hours)")
                elif key.endswith('_every'):
                    if num_value > 100:
                        raise ValueError(f"{key} cannot exceed 100")
                
                if key.endswith('_every'):
                    value = int(num_value)
                else:
                    value = num_value
            except (ValueError, TypeError) as e:
                if "cannot exceed" in str(e) or "must be positive" in str(e) or "Unknown configuration" in str(e):
                    raise
                raise ValueError(f"Invalid value for {key}: {value}")
        
        self.db.set_config(key, value)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all config values (merged with defaults)."""
        config = DEFAULT_CONFIG.copy()
        config.update(self.db.get_all_config())
        return config
    
    def reset(self):
        """Reset all config to defaults."""
        self.db.reset_config()
        self._ensure_defaults()
    
    @property
    def short_break_minutes(self) -> int:
        return int(self.get('short_break_minutes'))
    
    @property
    def long_break_minutes(self) -> int:
        return int(self.get('long_break_minutes'))
    
    @property
    def long_break_every(self) -> int:
        return int(self.get('long_break_every'))
    
    @property
    def abandon_threshold_minutes(self) -> int:
        return int(self.get('abandon_threshold_minutes'))
    
    @property
    def break_scrap_threshold_minutes(self) -> int:
        return int(self.get('break_scrap_threshold_minutes'))
    
    @property
    def decision_window_minutes(self) -> int:
        return int(self.get('decision_window_minutes'))
