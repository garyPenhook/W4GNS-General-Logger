"""
Theme-aware color utility for GUI widgets

This module provides functions to get theme-appropriate colors
that work in both light and dark modes.
"""

from src.theme import THEMES


def get_semantic_color(color_name, config=None):
    """
    Get a semantic color that adapts to the current theme.

    Args:
        color_name: One of 'success', 'error', 'warning', 'info', 'muted'
        config: Config object to determine current theme (optional)

    Returns:
        Hex color string appropriate for the current theme
    """
    # Determine current theme
    if config:
        theme_name = config.get('theme', 'dark')  # Default to dark since user wants dark mode
    else:
        theme_name = 'dark'  # Safe default

    theme = THEMES.get(theme_name, THEMES['dark'])

    # Return the semantic color or fall back to foreground color
    return theme.get(color_name, theme['fg'])


# Convenience functions for common colors
def get_success_color(config=None):
    """Get theme-appropriate green for success/achieved states"""
    return get_semantic_color('success', config)


def get_error_color(config=None):
    """Get theme-appropriate red for error/failed states"""
    return get_semantic_color('error', config)


def get_warning_color(config=None):
    """Get theme-appropriate orange for warning states"""
    return get_semantic_color('warning', config)


def get_info_color(config=None):
    """Get theme-appropriate blue for info states"""
    return get_semantic_color('info', config)


def get_muted_color(config=None):
    """Get theme-appropriate gray for muted/secondary text"""
    return get_semantic_color('muted', config)
