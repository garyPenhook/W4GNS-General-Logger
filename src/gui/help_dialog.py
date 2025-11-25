"""
Comprehensive Help System for W4GNS General Logger

Provides detailed help documentation with navigation and search.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

from src.gui.help_content import HelpContent


class HelpDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("W4GNS General Logger - Help")
        self.dialog.geometry("1000x700")
        self.dialog.transient(parent)

        # Don't grab focus - allow user to use app while reading help
        # self.dialog.grab_set()

        # Center the dialog
        self.center_window(parent)

        # Create UI
        self.create_widgets()

        # Show welcome page by default
        self.show_topic("welcome")

    def center_window(self, parent):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Create the help interface"""
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Create paned window for navigation and content
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill='both', expand=True)

        # LEFT PANE - Navigation
        nav_frame = ttk.Frame(paned, width=250)
        paned.add(nav_frame, weight=0)

        # Search box
        search_frame = ttk.Frame(nav_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_topics)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Topics tree
        tree_frame = ttk.Frame(nav_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')

        self.topics_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,
                                       show='tree', selectmode='browse')
        self.topics_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.config(command=self.topics_tree.yview)

        # Bind selection
        self.topics_tree.bind('<<TreeviewSelect>>', self.on_topic_select)

        # Populate topics
        self.populate_topics()

        # RIGHT PANE - Content
        content_frame = ttk.Frame(paned)
        paned.add(content_frame, weight=1)

        # Content text widget
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)

        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side='right', fill='y')

        self.content_text = tk.Text(text_frame, wrap=tk.WORD,
                                   yscrollcommand=text_scroll.set,
                                   font=('', 10), padx=15, pady=10)
        self.content_text.pack(side='left', fill='both', expand=True)
        text_scroll.config(command=self.content_text.yview)

        # Configure tags for formatting
        self.content_text.tag_config('title', font=('', 18, 'bold'), spacing3=10)
        self.content_text.tag_config('heading', font=('', 14, 'bold'), spacing1=15, spacing3=5)
        self.content_text.tag_config('subheading', font=('', 12, 'bold'), spacing1=10, spacing3=5)
        self.content_text.tag_config('bold', font=('', 10, 'bold'))
        self.content_text.tag_config('italic', font=('', 10, 'italic'))
        self.content_text.tag_config('code', font=('Courier', 9), background='#f0f0f0')
        self.content_text.tag_config('link', foreground='blue', underline=True)
        self.content_text.tag_config('bullet', lmargin1=30, lmargin2=45)
        self.content_text.tag_config('numbered', lmargin1=30, lmargin2=45)

        # Make links clickable
        self.content_text.tag_bind('link', '<Button-1>', self.on_link_click)
        self.content_text.tag_bind('link', '<Enter>', lambda e: self.content_text.config(cursor='hand2'))
        self.content_text.tag_bind('link', '<Leave>', lambda e: self.content_text.config(cursor=''))

        # Bottom button frame
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side='right')

    def populate_topics(self):
        """Populate the topics tree"""
        # Define help structure
        topics = {
            'welcome': 'Welcome',
            'getting_started': {
                'name': 'Getting Started',
                'children': {
                    'installation': 'Installation',
                    'first_time_setup': 'First Time Setup',
                    'quick_start': 'Quick Start Guide'
                }
            },
            'logging': {
                'name': 'Contact Logging',
                'children': {
                    'log_qso': 'Logging a QSO',
                    'fields': 'QSO Fields Explained',
                    'auto_lookup': 'Auto-Lookup Features',
                    'duplicate_detection': 'Duplicate Detection',
                    'keyboard_shortcuts': 'Keyboard Shortcuts'
                }
            },
            'contests': {
                'name': 'SKCC Contests',
                'children': {
                    'contest_overview': 'Contest Overview',
                    'wes_contest': 'WES - Weekend Sprintathon',
                    'sks_contest': 'SKS - Weekday Sprint',
                    'k3y_contest': 'K3Y - Straight Key Month',
                    'contest_scoring': 'Scoring and Bonuses',
                    'contest_export': 'Exporting Results'
                }
            },
            'monthly_brag': {
                'name': 'SKCC Monthly Brag',
                'children': {
                    'brag_overview': 'What is Monthly Brag?',
                    'brag_usage': 'Using the Report',
                    'brag_submission': 'Submitting Results'
                }
            },
            'dx_cluster': {
                'name': 'DX Clusters',
                'children': {
                    'cluster_connect': 'Connecting to Clusters',
                    'cluster_commands': 'Cluster Commands',
                    'cluster_spots': 'Reading DX Spots',
                    'skcc_highlighting': 'SKCC Member Highlighting'
                }
            },
            'awards': {
                'name': 'Awards Tracking',
                'children': {
                    'arrl_awards': 'ARRL Awards (WAS, DXCC, etc.)',
                    'skcc_awards': 'SKCC Awards (All 11)'
                }
            },
            'adif': {
                'name': 'ADIF Import/Export',
                'children': {
                    'adif_export': 'Exporting Logs',
                    'adif_date_range': 'Date/Time Range Export',
                    'adif_skcc': 'SKCC Contact Export',
                    'adif_import': 'Importing Logs'
                }
            },
            'qrz': {
                'name': 'QRZ.com Integration',
                'children': {
                    'qrz_setup': 'QRZ Setup',
                    'qrz_lookup': 'XML Lookups',
                    'qrz_upload': 'Logbook Upload'
                }
            },
            'space_weather': {
                'name': 'Space Weather',
                'children': {
                    'space_weather_overview': 'Understanding Space Weather',
                    'nasa_api': 'NASA API Setup',
                    'propagation': 'Propagation Forecasts'
                }
            },
            'settings': {
                'name': 'Settings & Configuration',
                'children': {
                    'station_info': 'Station Information',
                    'preferences': 'Logging Preferences',
                    'backup': 'Google Drive Backup',
                    'themes': 'Themes and Appearance'
                }
            },
            'reports': {
                'name': 'Reports',
                'children': {
                    'monthly_brag_report': 'Monthly Brag Report'
                }
            },
            'troubleshooting': {
                'name': 'Troubleshooting',
                'children': {
                    'qrz_issues': 'QRZ Issues',
                    'cluster_issues': 'DX Cluster Issues',
                    'database_issues': 'Database Issues',
                    'common_problems': 'Common Problems'
                }
            },
            'reference': {
                'name': 'Reference',
                'children': {
                    'keyboard_reference': 'Keyboard Shortcuts',
                    'field_reference': 'Field Reference',
                    'cluster_commands_ref': 'Cluster Commands'
                }
            }
        }

        # Store topic IDs for searching
        self.all_topics = {}

        # Build tree
        for key, value in topics.items():
            if isinstance(value, dict):
                parent = self.topics_tree.insert('', 'end', key, text=value['name'])
                self.all_topics[key] = value['name']
                if 'children' in value:
                    for child_key, child_name in value['children'].items():
                        self.topics_tree.insert(parent, 'end', child_key, text=child_name)
                        self.all_topics[child_key] = child_name
            else:
                self.topics_tree.insert('', 'end', key, text=value)
                self.all_topics[key] = value

    def filter_topics(self, *args):
        """Filter topics based on search"""
        search_text = self.search_var.get().lower()

        if not search_text:
            # Show all topics
            for item in self.topics_tree.get_children():
                self.show_tree_item(item)
            return

        # Hide items that don't match
        for item in self.topics_tree.get_children():
            self.filter_tree_item(item, search_text)

    def filter_tree_item(self, item, search_text):
        """Recursively filter tree items"""
        text = self.topics_tree.item(item, 'text').lower()
        children = self.topics_tree.get_children(item)

        # Check if any children match
        any_child_matches = False
        for child in children:
            if self.filter_tree_item(child, search_text):
                any_child_matches = True

        # Show if text matches or any child matches
        if search_text in text or any_child_matches:
            self.show_tree_item(item)
            return True
        else:
            self.hide_tree_item(item)
            return False

    def show_tree_item(self, item):
        """Show a tree item"""
        self.topics_tree.reattach(item, self.topics_tree.parent(item),
                                 self.topics_tree.index(item))
        # Recursively show children
        for child in self.topics_tree.get_children(item):
            self.show_tree_item(child)

    def hide_tree_item(self, item):
        """Hide a tree item"""
        self.topics_tree.detach(item)

    def on_topic_select(self, event):
        """Handle topic selection"""
        selection = self.topics_tree.selection()
        if selection:
            topic_id = selection[0]
            self.show_topic(topic_id)

    def show_topic(self, topic_id):
        """Display help content for a topic"""
        self.content_text.config(state='normal')
        self.content_text.delete('1.0', tk.END)

        # Get content based on topic_id
        content = self.get_help_content(topic_id)

        # Display content
        if content:
            for item in content:
                if isinstance(item, tuple):
                    text, *tags = item
                    self.content_text.insert(tk.END, text, tags if tags else ())
                else:
                    self.content_text.insert(tk.END, item)

        self.content_text.config(state='disabled')
        self.content_text.see('1.0')

    def on_link_click(self, event):
        """Handle link clicks"""
        # Get the tag at the click position
        index = self.content_text.index(f"@{event.x},{event.y}")
        tags = self.content_text.tag_names(index)

        # Find link tag
        for tag in tags:
            if tag.startswith('link_'):
                topic_id = tag[5:]  # Remove 'link_' prefix
                # Select in tree
                if topic_id in self.all_topics:
                    self.topics_tree.selection_set(topic_id)
                    self.topics_tree.see(topic_id)
                    self.show_topic(topic_id)
                elif tag.startswith('link_url_'):
                    url = tag[9:]  # Remove 'link_url_' prefix
                    webbrowser.open(url)
                break

    def get_help_content(self, topic_id):
        """Get help content for a specific topic"""
        return HelpContent.get_content(topic_id)
