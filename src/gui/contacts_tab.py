"""
Contacts Tab - View and manage logged contacts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime


class ContactsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.all_contacts = []  # Store all contacts for filtering
        self.is_loading = False
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

        # Loading indicator
        self.loading_label = ttk.Label(search_row, text="", foreground='blue', font=('', 9))
        self.loading_label.pack(side='left', padx=10)

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

        # Bind double-click to open contact details
        self.log_tree.bind('<Double-Button-1>', self.on_contact_double_click)

        # Load existing contacts
        self.refresh_log()

    def refresh_log(self):
        """Refresh the contact log display - load all contacts"""
        # Prevent multiple simultaneous loads
        if self.is_loading:
            return

        self.is_loading = True
        self.loading_label.config(text="Loading contacts...")

        # Run query in background thread
        threading.Thread(target=self._load_contacts_background, daemon=True).start()

    def _load_contacts_background(self):
        """Background thread for loading contacts"""
        try:
            # Perform the database query off the UI thread
            contacts = self.database.get_all_contacts(limit=999999)
            contacts_list = list(contacts)

            # Schedule UI update on main thread
            try:
                self.parent.after(0, lambda: self._update_contacts_display(contacts_list))
            except RuntimeError:
                # Main loop not started yet, call directly
                self._update_contacts_display(contacts_list)
        except Exception as e:
            # Handle errors gracefully
            try:
                self.parent.after(0, lambda: self._load_error(str(e)))
            except RuntimeError:
                # Main loop not started yet, call directly
                self._load_error(str(e))

    def _update_contacts_display(self, contacts_list):
        """Update UI with loaded contacts (runs on main thread)"""
        self.all_contacts = contacts_list
        self.loading_label.config(text="")
        self.is_loading = False

        # Apply current search filters
        self.apply_search()

    def _load_error(self, error_msg):
        """Handle load errors (runs on main thread)"""
        self.loading_label.config(text=f"Error: {error_msg}", foreground='red')
        self.is_loading = False

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
            # Store contact ID in the item tags for later retrieval
            item_id = self.log_tree.insert('', 'end', values=(
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
            # Store the full contact data and ID as tags
            self.log_tree.item(item_id, tags=(str(contact.get('id', '')),))

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

    def on_contact_double_click(self, event):
        """Handle double-click on a contact to open detail view"""
        selection = self.log_tree.selection()
        if not selection:
            return

        # Get the contact ID from the item's tags
        item = selection[0]
        tags = self.log_tree.item(item, 'tags')
        if not tags:
            return

        contact_id = int(tags[0])

        # Find the full contact data
        contact = None
        for c in self.all_contacts:
            if c.get('id') == contact_id:
                contact = c
                break

        if contact:
            self.show_contact_detail(contact)

    def show_contact_detail(self, contact):
        """Show contact detail dialog for viewing, editing, and deleting"""
        # Get the root window
        root = self.parent.winfo_toplevel()

        dialog = tk.Toplevel(root)
        dialog.title(f"Contact Details - {contact.get('callsign', 'Unknown')}")
        dialog.geometry("700x800")
        dialog.transient(root)

        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(header_frame, text=f"Contact with {contact.get('callsign', 'Unknown')}",
                 font=('', 14, 'bold')).pack(anchor='w')
        ttk.Label(header_frame, text=f"Logged on {contact.get('date', '')} at {contact.get('time_on', '')} UTC",
                 font=('', 10)).pack(anchor='w')

        # Store entry variables
        vars_dict = {}

        # Basic Information
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Information", padding=10)
        basic_frame.pack(fill='x', padx=10, pady=5)

        fields = [
            ('callsign', 'Callsign'),
            ('date', 'Date (YYYY-MM-DD)'),
            ('time_on', 'Time ON (UTC)'),
            ('time_off', 'Time OFF (UTC)'),
            ('frequency', 'Frequency (MHz)'),
            ('band', 'Band'),
            ('mode', 'Mode'),
            ('rst_sent', 'RST Sent'),
            ('rst_rcvd', 'RST Received'),
            ('power', 'Power (W)'),
        ]

        for field, label in fields:
            row = ttk.Frame(basic_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=f"{label}:", width=20).pack(side='left')
            var = tk.StringVar(value=contact.get(field, ''))
            vars_dict[field] = var
            ttk.Entry(row, textvariable=var, width=40).pack(side='left', padx=5)

        # Station Information
        station_frame = ttk.LabelFrame(scrollable_frame, text="Station Information", padding=10)
        station_frame.pack(fill='x', padx=10, pady=5)

        station_fields = [
            ('name', 'Name'),
            ('qth', 'QTH'),
            ('gridsquare', 'Grid Square'),
            ('county', 'County'),
            ('state', 'State'),
            ('country', 'Country'),
            ('continent', 'Continent'),
            ('cq_zone', 'CQ Zone'),
            ('itu_zone', 'ITU Zone'),
        ]

        for field, label in station_fields:
            row = ttk.Frame(station_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=f"{label}:", width=20).pack(side='left')
            var = tk.StringVar(value=contact.get(field, ''))
            vars_dict[field] = var
            ttk.Entry(row, textvariable=var, width=40).pack(side='left', padx=5)

        # Special Fields
        special_frame = ttk.LabelFrame(scrollable_frame, text="Special Fields", padding=10)
        special_frame.pack(fill='x', padx=10, pady=5)

        special_fields = [
            ('iota', 'IOTA'),
            ('sota', 'SOTA'),
            ('pota', 'POTA'),
            ('my_gridsquare', 'My Grid Square'),
        ]

        for field, label in special_fields:
            row = ttk.Frame(special_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=f"{label}:", width=20).pack(side='left')
            var = tk.StringVar(value=contact.get(field, ''))
            vars_dict[field] = var
            ttk.Entry(row, textvariable=var, width=40).pack(side='left', padx=5)

        # SKCC Fields
        skcc_frame = ttk.LabelFrame(scrollable_frame, text="SKCC Information", padding=10)
        skcc_frame.pack(fill='x', padx=10, pady=5)

        skcc_fields = [
            ('skcc_number', 'SKCC Number'),
            ('my_skcc_number', 'My SKCC Number'),
            ('key_type', 'Key Type'),
            ('duration_minutes', 'Duration (minutes)'),
        ]

        for field, label in skcc_fields:
            row = ttk.Frame(skcc_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=f"{label}:", width=20).pack(side='left')
            var = tk.StringVar(value=contact.get(field, ''))
            vars_dict[field] = var
            ttk.Entry(row, textvariable=var, width=40).pack(side='left', padx=5)

        # Notes
        notes_frame = ttk.LabelFrame(scrollable_frame, text="Notes", padding=10)
        notes_frame.pack(fill='x', padx=10, pady=5)

        notes_text = tk.Text(notes_frame, height=4, width=60)
        notes_text.pack(fill='x')
        notes_text.insert('1.0', contact.get('notes', ''))

        # Button frame
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=15)

        def save_changes():
            """Save the edited contact"""
            try:
                # Collect all the data
                updated_contact = {}
                for field, var in vars_dict.items():
                    value = var.get().strip()
                    updated_contact[field] = value if value else None

                # Add notes
                updated_contact['notes'] = notes_text.get('1.0', 'end-1c').strip()

                # Update in database
                self.database.update_contact(contact['id'], updated_contact)

                messagebox.showinfo("Success", f"Contact with {contact.get('callsign')} updated successfully!")
                dialog.destroy()

                # Refresh the contacts list
                self.refresh_log()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update contact: {str(e)}")

        def delete_contact():
            """Delete this contact"""
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete the contact with {contact.get('callsign')}?\n\n"
                f"Date: {contact.get('date')} {contact.get('time_on')} UTC\n\n"
                "This action cannot be undone.",
                icon='warning'
            )

            if confirm:
                try:
                    self.database.delete_contact(contact['id'])
                    messagebox.showinfo("Success", f"Contact with {contact.get('callsign')} deleted successfully!")
                    dialog.destroy()

                    # Refresh the contacts list
                    self.refresh_log()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete contact: {str(e)}")

        ttk.Button(button_frame, text="Save Changes", command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Contact", command=delete_contact).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side='right', padx=5)

        # Wait for window to be visible before grabbing focus
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.focus_set()

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
