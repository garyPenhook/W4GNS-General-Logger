"""
Contacts Tab - View and manage logged contacts
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

from src.qrz import QRZSession
from src.skcc_roster import SKCCRosterManager


class ContactsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.all_contacts = []  # Store all contacts for filtering
        self.is_loading = False
        self.qrz_session = None
        self.is_looking_up = False
        self.skcc_roster = SKCCRosterManager()
        self.create_widgets()

    def create_widgets(self):
        """Create the contacts log interface"""

        # Search/Filter frame
        search_frame = ttk.LabelFrame(self.frame, text="Search Contacts", padding=10)
        search_frame.pack(fill='x', padx=10, pady=5)

        # Row 1: Callsign, Lookup, Prefix, Country, State
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill='x', pady=2)

        # Callsign search
        ttk.Label(search_row1, text="Callsign:", width=10).pack(side='left', padx=2)
        self.callsign_search_var = tk.StringVar()
        self.callsign_search_var.trace('w', lambda *args: self.apply_search())
        callsign_entry = ttk.Entry(search_row1, textvariable=self.callsign_search_var, width=12)
        callsign_entry.pack(side='left', padx=2)
        callsign_entry.bind('<Return>', lambda e: self.lookup_callsign())
        callsign_entry.bind('<Tab>', lambda e: (self.lookup_callsign(), 'break')[1])

        # Lookup button
        self.lookup_btn = ttk.Button(search_row1, text="Lookup", command=self.lookup_callsign, width=7)
        self.lookup_btn.pack(side='left', padx=2)

        # Prefix search
        ttk.Label(search_row1, text="Prefix:", width=6).pack(side='left', padx=2)
        self.prefix_search_var = tk.StringVar()
        self.prefix_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row1, textvariable=self.prefix_search_var, width=8).pack(side='left', padx=2)

        # Country search
        ttk.Label(search_row1, text="Country:", width=8).pack(side='left', padx=2)
        self.country_search_var = tk.StringVar()
        self.country_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row1, textvariable=self.country_search_var, width=15).pack(side='left', padx=2)

        # State search
        ttk.Label(search_row1, text="State:", width=6).pack(side='left', padx=2)
        self.state_search_var = tk.StringVar()
        self.state_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row1, textvariable=self.state_search_var, width=8).pack(side='left', padx=2)

        # Continent search
        ttk.Label(search_row1, text="Continent:", width=10).pack(side='left', padx=2)
        self.continent_search_var = tk.StringVar()
        self.continent_search_var.trace('w', lambda *args: self.apply_search())
        continent_values = ['', 'AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA']
        ttk.Combobox(search_row1, textvariable=self.continent_search_var, values=continent_values, width=5, state='readonly').pack(side='left', padx=2)

        # Row 2: Band, Mode, Date range
        search_row2 = ttk.Frame(search_frame)
        search_row2.pack(fill='x', pady=2)

        # Band search
        ttk.Label(search_row2, text="Band:", width=10).pack(side='left', padx=2)
        self.band_search_var = tk.StringVar()
        self.band_search_var.trace('w', lambda *args: self.apply_search())
        band_values = ['', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '2m', '70cm']
        ttk.Combobox(search_row2, textvariable=self.band_search_var, values=band_values, width=8, state='readonly').pack(side='left', padx=2)

        # Mode search
        ttk.Label(search_row2, text="Mode:", width=6).pack(side='left', padx=2)
        self.mode_search_var = tk.StringVar()
        self.mode_search_var.trace('w', lambda *args: self.apply_search())
        mode_values = ['', 'CW', 'SSB', 'AM', 'FM', 'FT8', 'FT4', 'RTTY', 'PSK31', 'JS8']
        ttk.Combobox(search_row2, textvariable=self.mode_search_var, values=mode_values, width=8, state='readonly').pack(side='left', padx=2)

        # Date From
        ttk.Label(search_row2, text="From:", width=6).pack(side='left', padx=2)
        self.date_from_var = tk.StringVar()
        self.date_from_var.trace('w', lambda *args: self.apply_search())
        date_from_entry = ttk.Entry(search_row2, textvariable=self.date_from_var, width=10)
        date_from_entry.pack(side='left', padx=2)
        date_from_entry.insert(0, 'YYYY-MM-DD')
        date_from_entry.config(foreground='gray')
        date_from_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(date_from_entry, self.date_from_var, 'YYYY-MM-DD'))
        date_from_entry.bind('<FocusOut>', lambda e: self._set_placeholder(date_from_entry, self.date_from_var, 'YYYY-MM-DD'))

        # Date To
        ttk.Label(search_row2, text="To:", width=4).pack(side='left', padx=2)
        self.date_to_var = tk.StringVar()
        self.date_to_var.trace('w', lambda *args: self.apply_search())
        date_to_entry = ttk.Entry(search_row2, textvariable=self.date_to_var, width=10)
        date_to_entry.pack(side='left', padx=2)
        date_to_entry.insert(0, 'YYYY-MM-DD')
        date_to_entry.config(foreground='gray')
        date_to_entry.bind('<FocusIn>', lambda e: self._clear_placeholder(date_to_entry, self.date_to_var, 'YYYY-MM-DD'))
        date_to_entry.bind('<FocusOut>', lambda e: self._set_placeholder(date_to_entry, self.date_to_var, 'YYYY-MM-DD'))

        # CQ Zone
        ttk.Label(search_row2, text="CQ Zone:", width=8).pack(side='left', padx=2)
        self.cq_zone_var = tk.StringVar()
        self.cq_zone_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row2, textvariable=self.cq_zone_var, width=4).pack(side='left', padx=2)

        # ITU Zone
        ttk.Label(search_row2, text="ITU Zone:", width=9).pack(side='left', padx=2)
        self.itu_zone_var = tk.StringVar()
        self.itu_zone_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row2, textvariable=self.itu_zone_var, width=4).pack(side='left', padx=2)

        # Row 3: DXCC, POTA, SOTA, SKCC, QRP
        search_row3 = ttk.Frame(search_frame)
        search_row3.pack(fill='x', pady=2)

        # DXCC entity
        ttk.Label(search_row3, text="DXCC:", width=10).pack(side='left', padx=2)
        self.dxcc_search_var = tk.StringVar()
        self.dxcc_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row3, textvariable=self.dxcc_search_var, width=10).pack(side='left', padx=2)

        # POTA reference
        ttk.Label(search_row3, text="POTA:", width=6).pack(side='left', padx=2)
        self.pota_search_var = tk.StringVar()
        self.pota_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row3, textvariable=self.pota_search_var, width=10).pack(side='left', padx=2)

        # SOTA reference
        ttk.Label(search_row3, text="SOTA:", width=6).pack(side='left', padx=2)
        self.sota_search_var = tk.StringVar()
        self.sota_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row3, textvariable=self.sota_search_var, width=10).pack(side='left', padx=2)

        # SKCC number
        ttk.Label(search_row3, text="SKCC#:", width=7).pack(side='left', padx=2)
        self.skcc_search_var = tk.StringVar()
        self.skcc_search_var.trace('w', lambda *args: self.apply_search())
        ttk.Entry(search_row3, textvariable=self.skcc_search_var, width=8).pack(side='left', padx=2)

        # QRP checkbox (5W or less)
        self.qrp_var = tk.BooleanVar()
        self.qrp_var.trace('w', lambda *args: self.apply_search())
        ttk.Checkbutton(search_row3, text="QRP (≤5W)", variable=self.qrp_var).pack(side='left', padx=10)

        # Search button
        ttk.Button(search_row3, text="Search", command=self.apply_search).pack(side='left', padx=5)

        # Clear search button
        ttk.Button(search_row3, text="Clear", command=self.clear_search).pack(side='left', padx=5)

        # Loading indicator
        self.loading_label = ttk.Label(search_row3, text="", foreground='blue', font=('', 9))
        self.loading_label.pack(side='left', padx=5)

        # Results count label
        self.results_label = ttk.Label(search_row3, text="", font=('', 9))
        self.results_label.pack(side='left', padx=5)

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

        # Delay loading contacts until main loop is running
        self.parent.after(100, self.refresh_log)

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

            # Schedule UI update on main thread (main loop is guaranteed to be running)
            self.parent.after(0, lambda: self._update_contacts_display(contacts_list))
        except Exception as e:
            # Handle errors gracefully
            self.parent.after(0, lambda: self._load_error(str(e)))

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
        """Apply search filters and update display using database query"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Get search criteria
        callsign_search = self.callsign_search_var.get().strip().upper()
        prefix_search = self.prefix_search_var.get().strip().upper()
        country_search = self.country_search_var.get().strip().upper()
        state_search = self.state_search_var.get().strip().upper()
        continent_search = self.continent_search_var.get().strip().upper()
        band_search = self.band_search_var.get().strip().upper()
        mode_search = self.mode_search_var.get().strip().upper()
        date_from = self.date_from_var.get().strip()
        date_to = self.date_to_var.get().strip()
        # Ignore placeholder text
        if date_from == 'YYYY-MM-DD':
            date_from = ''
        if date_to == 'YYYY-MM-DD':
            date_to = ''
        cq_zone_search = self.cq_zone_var.get().strip()
        itu_zone_search = self.itu_zone_var.get().strip()
        dxcc_search = self.dxcc_search_var.get().strip().upper()
        pota_search = self.pota_search_var.get().strip().upper()
        sota_search = self.sota_search_var.get().strip().upper()
        skcc_search = self.skcc_search_var.get().strip().upper()
        qrp_only = self.qrp_var.get()

        # Build SQL query with filters
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []

        if callsign_search:
            query += " AND UPPER(callsign) LIKE ?"
            params.append(f"%{callsign_search}%")

        if prefix_search:
            query += " AND UPPER(callsign) LIKE ?"
            params.append(f"{prefix_search}%")

        if country_search:
            query += " AND UPPER(country) LIKE ?"
            params.append(f"%{country_search}%")

        if state_search:
            query += " AND UPPER(state) LIKE ?"
            params.append(f"%{state_search}%")

        if continent_search:
            query += " AND UPPER(continent) = ?"
            params.append(continent_search)

        if band_search:
            query += " AND UPPER(band) = ?"
            params.append(band_search)

        if mode_search:
            query += " AND UPPER(mode) = ?"
            params.append(mode_search)

        if date_from:
            query += " AND date >= ?"
            params.append(date_from)

        if date_to:
            query += " AND date <= ?"
            params.append(date_to)

        if cq_zone_search:
            query += " AND cq_zone = ?"
            params.append(cq_zone_search)

        if itu_zone_search:
            query += " AND itu_zone = ?"
            params.append(itu_zone_search)

        if dxcc_search:
            query += " AND (UPPER(dxcc_entity) LIKE ? OR UPPER(dxcc) LIKE ?)"
            params.append(f"%{dxcc_search}%")
            params.append(f"%{dxcc_search}%")

        if pota_search:
            query += " AND UPPER(pota) LIKE ?"
            params.append(f"%{pota_search}%")

        if sota_search:
            query += " AND UPPER(sota) LIKE ?"
            params.append(f"%{sota_search}%")

        if skcc_search:
            query += " AND UPPER(skcc_number) LIKE ?"
            params.append(f"%{skcc_search}%")

        if qrp_only:
            query += " AND (CAST(REPLACE(REPLACE(power, 'W', ''), ' ', '') AS REAL) <= 5 OR CAST(power_watts AS REAL) <= 5)"

        query += " ORDER BY date DESC, time_on DESC"

        # Execute query
        try:
            cursor = self.database.conn.cursor()
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            filtered_contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            self.loading_label.config(text=f"Query error: {str(e)}", foreground='red')
            filtered_contacts = []

        # Store for double-click handler
        self.all_contacts = filtered_contacts

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
        shown = len(filtered_contacts)
        has_filter = any([callsign_search, prefix_search, country_search, state_search,
                        continent_search, band_search, mode_search, date_from, date_to,
                        cq_zone_search, itu_zone_search, dxcc_search, pota_search,
                        sota_search, skcc_search, qrp_only])
        if has_filter:
            # Get total count from database
            try:
                cursor = self.database.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM contacts")
                total = cursor.fetchone()[0]
            except:
                total = shown
            self.results_label.config(text=f"Showing {shown} of {total} contacts")
        else:
            self.results_label.config(text=f"Total: {shown} contacts")

    def clear_search(self):
        """Clear all search filters"""
        self.callsign_search_var.set('')
        self.prefix_search_var.set('')
        self.country_search_var.set('')
        self.state_search_var.set('')
        self.continent_search_var.set('')
        self.band_search_var.set('')
        self.mode_search_var.set('')
        self.date_from_var.set('')
        self.date_to_var.set('')
        self.cq_zone_var.set('')
        self.itu_zone_var.set('')
        self.dxcc_search_var.set('')
        self.pota_search_var.set('')
        self.sota_search_var.set('')
        self.skcc_search_var.set('')
        self.qrp_var.set(False)
        # apply_search() will be called automatically via trace

    def _clear_placeholder(self, entry, var, placeholder):
        """Clear placeholder text when entry gains focus"""
        if var.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(foreground='black')

    def _set_placeholder(self, entry, var, placeholder):
        """Set placeholder text when entry loses focus and is empty"""
        if not var.get():
            entry.insert(0, placeholder)
            entry.config(foreground='gray')

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

    def lookup_callsign(self):
        """Lookup callsign using QRZ"""
        if self.is_looking_up:
            return

        callsign = self.callsign_search_var.get().strip().upper()
        if not callsign:
            return

        self.is_looking_up = True
        original_text = self.lookup_btn['text']
        self.lookup_btn.config(text="...", state='disabled')

        threading.Thread(
            target=self._lookup_background,
            args=(callsign, original_text),
            daemon=True
        ).start()

    def _lookup_background(self, callsign, original_button_text):
        """Background thread for callsign lookup"""
        try:
            qrz_data = None
            skcc_number = None

            # Try QRZ lookup
            if self.config.get('qrz.enable_lookup', False):
                qrz_user = self.config.get('qrz.username')
                qrz_pass = self.config.get('qrz.password')

                if qrz_user and qrz_pass:
                    if not self.qrz_session:
                        self.qrz_session = QRZSession(qrz_user, qrz_pass)

                    try:
                        qrz_data = self.qrz_session.lookup_callsign(callsign)
                    except:
                        pass

            # Look up SKCC number
            try:
                member_info = self.skcc_roster.lookup_member(callsign)
                if member_info and member_info.get('skcc_number'):
                    skcc_number = member_info['skcc_number']
            except:
                pass

            if not skcc_number:
                try:
                    cursor = self.database.conn.cursor()
                    cursor.execute('''
                        SELECT skcc_number FROM contacts
                        WHERE callsign = ? AND skcc_number IS NOT NULL AND skcc_number != ''
                        ORDER BY date DESC LIMIT 1
                    ''', (callsign.upper(),))
                    result = cursor.fetchone()
                    if result:
                        skcc_number = result[0]
                except:
                    pass

            self.frame.after(0, lambda: self._show_lookup_results(
                callsign, original_button_text, qrz_data, skcc_number
            ))

        except Exception as e:
            self.frame.after(0, lambda: self._lookup_done(original_button_text))

    def _show_lookup_results(self, callsign, original_button_text, qrz_data, skcc_number):
        """Show lookup results in a dialog"""
        self._lookup_done(original_button_text)

        # Build info text
        info = f"Callsign: {callsign}\n\n"

        if qrz_data:
            if 'first_name' in qrz_data or 'name' in qrz_data:
                name = f"{qrz_data.get('first_name', '')} {qrz_data.get('name', '')}".strip()
                info += f"Name: {name}\n"
            if 'addr2' in qrz_data:
                info += f"City: {qrz_data['addr2']}\n"
            if 'state' in qrz_data:
                info += f"State: {qrz_data['state']}\n"
            if 'country' in qrz_data:
                info += f"Country: {qrz_data['country']}\n"
            if 'gridsquare' in qrz_data:
                info += f"Grid: {qrz_data['gridsquare']}\n"

        if skcc_number:
            info += f"\nSKCC #: {skcc_number}"
            if 'S' in skcc_number.upper():
                info += " (Senator)"
            elif 'T' in skcc_number.upper():
                info += " (Tribune)"
            elif 'C' in skcc_number.upper():
                info += " (Centurion)"

        if not qrz_data and not skcc_number:
            info += "No information found"

        messagebox.showinfo(f"Lookup: {callsign}", info)

    def _lookup_done(self, original_button_text):
        """Reset lookup state"""
        self.lookup_btn.config(text=original_button_text, state='normal')
        self.is_looking_up = False

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
