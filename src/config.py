"""
Configuration management
"""

import json
import os


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.data = self.load()

    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.get_defaults()
        return self.get_defaults()

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_defaults(self):
        """Get default configuration"""
        return {
            "callsign": "",
            "gridsquare": "",
            "default_rst": "59",
            "dx_cluster": {
                "selected": "W3LPL",
                "auto_connect": False,
                "show_cw_spots": True,
                "show_ssb_spots": True,
                "show_digital_spots": True,
                "filter_band": None
            },
            "window": {
                "width": 1000,
                "height": 700
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
