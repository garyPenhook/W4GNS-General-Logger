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
        self.all_contacts = []  # Store all contacts for filtering
        self.create_widgets()

    def create_widgets(self):
        """Create the contacts log interface"""

        # Search/Filter frame
        search_frame = ttk.LabelFrame(self.frame, text="Search Contacts", padding=10)
        search_frame.pack(fill='x', padx=10, pady=5)

        # Search controls row
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill='x', pady=2)

        # Callsign search
        ttk.Label(search_row, text="Callsign:", width=10).pack(side='left', padx=2)
        self.callsign_search_var = tk.StringVar()
        self.callsign_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row, textvariable=self.callsign_search_var, width=15).pack(side='left', padx=5)

        # Prefix search
        ttk.Label(search_row, text="Prefix:", width=8).pack(side='left', padx=2)
        self.prefix_search_var = tk.StringVar()
        self.prefix_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row, textvariable=self.prefix_search_var, width=10).pack(side='left', padx=5)

        # Country search
        ttk.Label(search_row, text="Country:", width=8).pack(side='left', padx=2)
        self.country_search_var = tk.StringVar()
        self.country_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row, textvariable=self.country_search_var, width=20).pack(side='left', padx=5)

        # Clear search button
        ttk.Button(search_row, text="Clear Search", command=self.clear_search).pack(side='left', padx=10)

        # Results count label
        self.results_label = ttk.Label(search_row, text="", font=('', 9))
        self.results_label.pack(side='left', padx=10)

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
        """Refresh the contact log display - load all contacts"""
        # Get all contacts (no limit)
        contacts = self.database.get_all_contacts(limit=999999)
        self.all_contacts = list(contacts)

        # Apply current search filters
        self.apply_search()

    def apply_search(self):
        """Apply search filters and update display"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Get search criteria
        callsign_search = self.callsign_search_var.get().strip().upper()
        prefix_search = self.prefix_search_var.get().strip().upper()
        country_search = self.country_search_var.get().strip().upper()

        # Filter contacts
        filtered_contacts = []
        for contact in self.all_contacts:
            callsign = contact.get('callsign', '').upper()
            country = contact.get('country', '').upper()

            # Callsign filter (partial match)
            if callsign_search and callsign_search not in callsign:
                continue

            # Prefix filter (starts with)
            if prefix_search and not callsign.startswith(prefix_search):
                continue

            # Country filter (partial match)
            if country_search and country_search not in country:
                continue

            filtered_contacts.append(contact)

        # Add filtered contacts to treeview (most recent first)
        for contact in filtered_contacts:
            self.log_tree.insert('', 'end', values=(
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

        # Update results label
        total = len(self.all_contacts)
        shown = len(filtered_contacts)
        if callsign_search or prefix_search or country_search:
            self.results_label.config(text=f"Showing {shown} of {total} contacts")
        else:
            self.results_label.config(text=f"Total: {total} contacts")

    def clear_search(self):
        """Clear all search filters"""
        self.callsign_search_var.set('')
        self.prefix_search_var.set('')
        self.country_search_var.set('')
        # apply_search() will be called automatically via trace

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
