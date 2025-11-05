"""
Contacts Tab - View and manage logged contacts
"""

import tkinter as tk
from tkinter import ttk


class ContactsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Create the contacts log interface"""

        # Log display frame
        log_frame = ttk.LabelFrame(self.frame, text="Contact Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for contacts
        columns = ('Call', 'Date', 'Time', 'Freq', 'Mode', 'RST', 'Name', 'Country', 'Grid')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=20)

        for col in columns:
            self.log_tree.heading(col, text=col)

        self.log_tree.column('Call', width=100)
        self.log_tree.column('Date', width=90)
        self.log_tree.column('Time', width=60)
        self.log_tree.column('Freq', width=80)
        self.log_tree.column('Mode', width=60)
        self.log_tree.column('RST', width=70)
        self.log_tree.column('Name', width=120)
        self.log_tree.column('Country', width=150)
        self.log_tree.column('Grid', width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        self.log_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Load existing contacts
        self.refresh_log()

    def refresh_log(self):
        """Refresh the contact log display"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Get recent contacts
        contacts = self.database.get_all_contacts(limit=100)

        # Add to treeview
        for contact in contacts:
            self.log_tree.insert('', 0, values=(
                contact.get('callsign', ''),
                contact.get('date', ''),
                contact.get('time_on', ''),
                contact.get('frequency', ''),
                contact.get('mode', ''),
                f"{contact.get('rst_sent', '')}/{contact.get('rst_rcvd', '')}",
                contact.get('name', ''),
                contact.get('country', ''),
                contact.get('gridsquare', '')
            ))

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
