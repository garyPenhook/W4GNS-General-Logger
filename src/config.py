"""
Configuration management
"""

import json
import os
import tempfile
import shutil


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

    def save(self):
        """Save configuration to file using atomic write"""
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
        """Get configuration value"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self.save()
