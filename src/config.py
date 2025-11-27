"""
Configuration management with performance optimizations
"""

import json
import os
import tempfile
import shutil
import time
from functools import lru_cache
from threading import Lock


class Config:
    def __init__(self, config_path=None):
        # Default to config.json in the project root directory
        if config_path is None:
            # Get the directory where this script is located (src/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, "config.json")

        self.config_path = config_path
        self.data = self.load()

        # Performance optimizations
        self._lock = Lock()  # Thread-safe operations
        self._last_mtime = self._get_mtime()  # Track file modification time
        self._pending_save = False  # Debounced save flag
        self._last_save_time = 0  # Last save timestamp
        self._save_debounce_seconds = 0.5  # Wait 0.5s before writing to disk
        self._get_cache = {}  # Simple cache for get() operations

    def _get_mtime(self):
        """Get file modification time, or 0 if file doesn't exist"""
        try:
            return os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0
        except OSError:
            return 0

    def _check_reload(self):
        """Check if config file changed externally and reload if needed"""
        current_mtime = self._get_mtime()
        if current_mtime > self._last_mtime:
            with self._lock:
                self.data = self.load()
                self._last_mtime = current_mtime
                self._get_cache.clear()  # Invalidate cache

    def load(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            return self.get_defaults()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Config file is malformed JSON: {e}")
            # Backup the corrupted file
            backup_path = self.config_path + '.corrupted'
            try:
                shutil.copy2(self.config_path, backup_path)
                print(f"Corrupted config backed up to: {backup_path}")
            except Exception:
                pass
            return self.get_defaults()
        except PermissionError as e:
            print(f"ERROR: Cannot read config file (permission denied): {e}")
            return self.get_defaults()
        except IOError as e:
            print(f"ERROR: Cannot read config file: {e}")
            return self.get_defaults()
        except Exception as e:
            print(f"ERROR: Unexpected error loading config: {type(e).__name__}: {e}")
            return self.get_defaults()

    def save(self, force=False):
        """
        Save configuration to file using atomic write with debouncing

        Args:
            force: If True, bypass debouncing and save immediately
        """
        current_time = time.time()

        # Debounce: Skip save if we saved recently (unless forced)
        if not force and (current_time - self._last_save_time) < self._save_debounce_seconds:
            self._pending_save = True
            return

        with self._lock:
            try:
                # Get directory of config file
                config_dir = os.path.dirname(self.config_path) or '.'

                # Write to temporary file first
                fd, temp_path = tempfile.mkstemp(dir=config_dir, suffix='.tmp')
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as f:
                        json.dump(self.data, f, indent=2)

                    # Atomic rename (overwrites existing file)
                    shutil.move(temp_path, self.config_path)

                    # Update tracking variables
                    self._last_save_time = current_time
                    self._last_mtime = self._get_mtime()
                    self._pending_save = False

                except Exception:
                    # Clean up temp file on error
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise

            except PermissionError as e:
                print(f"ERROR: Cannot save config file (permission denied): {e}")
            except IOError as e:
                print(f"ERROR: Cannot save config file: {e}")
            except Exception as e:
                print(f"ERROR: Unexpected error saving config: {type(e).__name__}: {e}")

    def flush(self):
        """Force immediate save if there are pending changes"""
        if self._pending_save:
            self.save(force=True)

    def get_defaults(self):
        """Get default configuration"""
        return {
            "callsign": "",
            "gridsquare": "",
            "default_rst": "59",
            "default_power": "100",
            "dx_cluster": {
                "selected": "W3LPL",
                "auto_connect": False,
                "show_cw_spots": True,
                "show_ssb_spots": True,
                "show_digital_spots": True,
                "filter_band": None
            },
            "qrz": {
                "username": "",
                "password": "",
                "api_key": "",
                "auto_upload": False,
                "enable_lookup": True
            },
            "logging": {
                "auto_lookup": True,
                "warn_duplicates": True,
                "auto_time_off": True
            },
            "window": {
                "width": 1200,
                "height": 750
            },
            "google_drive": {
                "enabled": False,
                "backup_interval_hours": 24,
                "max_backups": 30,
                "include_config": True,
                "last_backup": None
            },
            "nasa": {
                "api_key": "gnvs4j1YeLecrNeI0xcGtNMBwsxy5cfabuw2EFna",
                "donki_cache_hours": 24
            }
        }

    def get(self, key, default=None):
        """Get configuration value with caching"""
        # Check if file changed externally
        self._check_reload()

        # Check cache first
        if key in self._get_cache:
            return self._get_cache[key]

        # Navigate nested dict structure
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        # Cache the result
        self._get_cache[key] = value
        return value

    def set(self, key, value):
        """Set configuration value with cache invalidation"""
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

        # Invalidate cache for this key and any parent keys
        self._invalidate_cache_for_key(key)

        # Debounced save
        self.save()

    def _invalidate_cache_for_key(self, key):
        """Invalidate cache entries that might be affected by this key"""
        # Remove exact match
        self._get_cache.pop(key, None)

        # Remove any cached keys that start with this prefix
        # (parent keys whose values might have changed)
        prefix = key.split('.')[0]
        keys_to_remove = [k for k in self._get_cache if k.startswith(prefix)]
        for k in keys_to_remove:
            self._get_cache.pop(k, None)

    # Python data model methods for dictionary-like access
    def __getitem__(self, key):
        """Enable dict-like access: config['qrz.username']"""
        result = self.get(key)
        if result is None:
            raise KeyError(f"Configuration key not found: {key}")
        return result

    def __setitem__(self, key, value):
        """Enable dict-like assignment: config['qrz.username'] = 'W4GNS'"""
        self.set(key, value)

    def __contains__(self, key):
        """Enable membership testing: 'qrz.username' in config"""
        return self.get(key) is not None

    def __len__(self):
        """Return number of top-level configuration keys"""
        return len(self.data)

    def __repr__(self):
        """Developer-friendly representation"""
        cached = len(self._get_cache)
        pending = " [pending save]" if self._pending_save else ""
        return f"<Config(path={self.config_path!r}, keys={len(self.data)}, cached={cached}{pending})>"

    def __del__(self):
        """Ensure pending saves are flushed when object is destroyed"""
        try:
            self.flush()
        except Exception:
            pass  # Avoid errors during cleanup
