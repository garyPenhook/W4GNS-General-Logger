"""
Helpers for locating persistent app files and bundled resources.
"""

import os
import sys


def get_app_root() -> str:
    """Return the directory that should hold persistent app files."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_bundle_root() -> str:
    """Return the directory containing bundled read-only resources."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return get_app_root()


def app_path(*parts: str) -> str:
    """Build a path under the persistent app root."""
    return os.path.join(get_app_root(), *parts)


def bundled_path(*parts: str) -> str:
    """Build a path under the bundled resource root."""
    return os.path.join(get_bundle_root(), *parts)
