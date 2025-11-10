"""
Theme Manager for W4GNS Logger
Provides light and dark color schemes
"""

import tkinter as tk
from tkinter import ttk


# Color schemes
THEMES = {
    'light': {
        'bg': '#f0f0f0',
        'fg': '#000000',
        'select_bg': '#0078d7',
        'select_fg': '#ffffff',
        'entry_bg': '#ffffff',
        'entry_fg': '#000000',
        'button_bg': '#e1e1e1',
        'frame_bg': '#f0f0f0',
        'label_bg': '#f0f0f0',
        'text_bg': '#ffffff',
        'text_fg': '#000000',
        'border': '#cccccc',
        'highlight': '#0078d7',
        'console_bg': '#ffffff',
        'console_fg': '#000000',
        # Semantic colors
        'success': '#008000',      # Green for success/achieved
        'error': '#c00000',        # Red for errors/not achieved
        'warning': '#ff8c00',      # Orange for warnings
        'info': '#0078d7',         # Blue for info
        'muted': '#808080',        # Gray for muted/disabled text
        'spot_highlight': '#fff3cd'  # Light amber for DX spot highlighting
    },
    'dark': {
        'bg': '#2b2b2b',
        'fg': '#e0e0e0',
        'select_bg': '#0d47a1',
        'select_fg': '#ffffff',
        'entry_bg': '#3c3f41',
        'entry_fg': '#e0e0e0',
        'button_bg': '#3c3f41',
        'frame_bg': '#2b2b2b',
        'label_bg': '#2b2b2b',
        'text_bg': '#1e1e1e',
        'text_fg': '#e0e0e0',
        'border': '#555555',
        'highlight': '#1565c0',
        'console_bg': '#1e1e1e',
        'console_fg': '#a9b7c6',
        # Semantic colors - adjusted for dark mode readability
        'success': '#4caf50',      # Lighter green for dark bg
        'error': '#ef5350',        # Lighter red for dark bg
        'warning': '#ffa726',      # Lighter orange for dark bg
        'info': '#42a5f5',         # Lighter blue for dark bg
        'muted': '#9e9e9e',        # Lighter gray for dark bg
        'spot_highlight': '#5d4a00'  # Dark amber for DX spot highlighting (good contrast with light text)
    }
}


class ThemeManager:
    """Manages application theming"""

    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.current_theme = config.get('theme', 'light')

    def apply_theme(self, theme_name='light'):
        """Apply a theme to the application"""
        if theme_name not in THEMES:
            theme_name = 'light'

        theme = THEMES[theme_name]
        self.current_theme = theme_name

        # Configure ttk style
        style = ttk.Style(self.root)

        # Try to use 'clam' or 'alt' theme as base (more customizable)
        try:
            style.theme_use('clam')
        except tk.TclError:
            try:
                style.theme_use('alt')
            except tk.TclError:
                # Theme not available, use default
                print("Warning: 'clam' and 'alt' themes not available, using default")

        # Configure standard ttk widgets
        style.configure('.',
                       background=theme['bg'],
                       foreground=theme['fg'],
                       fieldbackground=theme['entry_bg'],
                       bordercolor=theme['border'],
                       insertcolor=theme['fg'])

        style.configure('TFrame',
                       background=theme['frame_bg'])

        style.configure('TLabel',
                       background=theme['label_bg'],
                       foreground=theme['fg'])

        style.configure('TLabelframe',
                       background=theme['frame_bg'],
                       foreground=theme['fg'])

        style.configure('TLabelframe.Label',
                       background=theme['frame_bg'],
                       foreground=theme['fg'])

        style.configure('TButton',
                       background=theme['button_bg'],
                       foreground=theme['fg'],
                       bordercolor=theme['border'],
                       lightcolor=theme['button_bg'],
                       darkcolor=theme['button_bg'])

        style.map('TButton',
                 background=[('active', theme['highlight']),
                           ('pressed', theme['highlight'])])

        style.configure('TEntry',
                       fieldbackground=theme['entry_bg'],
                       foreground=theme['entry_fg'],
                       bordercolor=theme['border'],
                       insertcolor=theme['fg'])

        style.configure('TCombobox',
                       fieldbackground=theme['entry_bg'],
                       background=theme['entry_bg'],
                       foreground=theme['entry_fg'],
                       bordercolor=theme['border'],
                       arrowcolor=theme['fg'],
                       insertcolor=theme['fg'])

        style.map('TCombobox',
                 fieldbackground=[('readonly', theme['entry_bg'])],
                 selectbackground=[('readonly', theme['entry_bg'])],
                 selectforeground=[('readonly', theme['entry_fg'])])

        style.configure('TCheckbutton',
                       background=theme['bg'],
                       foreground=theme['fg'])

        style.configure('TNotebook',
                       background=theme['bg'],
                       bordercolor=theme['border'])

        style.configure('TNotebook.Tab',
                       background=theme['button_bg'],
                       foreground=theme['fg'])

        style.map('TNotebook.Tab',
                 background=[('selected', theme['highlight'])],
                 foreground=[('selected', theme['select_fg'])])

        # Treeview styling
        style.configure('Treeview',
                       background=theme['text_bg'],
                       foreground=theme['text_fg'],
                       fieldbackground=theme['text_bg'],
                       bordercolor=theme['border'])

        style.configure('Treeview.Heading',
                       background=theme['button_bg'],
                       foreground=theme['fg'],
                       bordercolor=theme['border'])

        style.map('Treeview',
                 background=[('selected', theme['select_bg'])],
                 foreground=[('selected', theme['select_fg'])])

        # Configure root window
        self.root.configure(bg=theme['bg'])

        # Update all widgets recursively
        self._update_widgets(self.root, theme)

        # Save theme preference
        self.config.set('theme', theme_name)

    def _update_widgets(self, widget, theme):
        """Recursively update all widgets"""
        # Update widget-specific colors for non-ttk widgets
        widget_class = widget.winfo_class()

        if widget_class == 'Text':
            try:
                widget.configure(
                    bg=theme['console_bg'],
                    fg=theme['console_fg'],
                    insertbackground=theme['fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg']
                )
            except tk.TclError:
                pass

        elif widget_class == 'Listbox':
            try:
                widget.configure(
                    bg=theme['text_bg'],
                    fg=theme['text_fg'],
                    selectbackground=theme['select_bg'],
                    selectforeground=theme['select_fg']
                )
            except tk.TclError:
                pass

        elif widget_class == 'Menu':
            try:
                widget.configure(
                    bg=theme['bg'],
                    fg=theme['fg'],
                    activebackground=theme['highlight'],
                    activeforeground=theme['select_fg']
                )
            except tk.TclError:
                pass

        # Recursively update children
        for child in widget.winfo_children():
            self._update_widgets(child, theme)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        return new_theme

    def get_current_theme(self):
        """Get the current theme name"""
        return self.current_theme

    def get_color(self, color_name):
        """
        Get a theme-aware color value.

        Args:
            color_name: Name of the color (e.g., 'success', 'error', 'warning', 'info', 'muted')

        Returns:
            Hex color string appropriate for current theme
        """
        theme = THEMES.get(self.current_theme, THEMES['light'])
        return theme.get(color_name, theme['fg'])


def get_theme_colors(theme_name='light'):
    """Get color dictionary for a theme"""
    return THEMES.get(theme_name, THEMES['light'])
