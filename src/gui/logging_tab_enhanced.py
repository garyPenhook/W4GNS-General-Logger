"""
Enhanced Logging Tab - Log4OM-style contact logging interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.dxcc import lookup_dxcc
from src.qrz import QRZSession, upload_to_qrz_logbook


class EnhancedLoggingTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.qrz_session = None
        self.create_widgets()

        # Set up callsign lookup callback
        self.callsign_entry.bind('<FocusOut>', self.on_callsign_changed)
        self.callsign_entry.bind('<Return>', lambda e: self.freq_entry.focus())

        # Set up frequency/band correlation
        self.freq_entry.bind('<FocusOut>', self.on_frequency_changed)

        # Focus on callsign field
        self.callsign_entry.focus()

    def create_widgets(self):
        """Create the enhanced logging interface"""

        # Top section - QSO Entry
        entry_frame = ttk.LabelFrame(self.frame, text="New Contact", padding=10)
        entry_frame.pack(fill='x', padx=10, pady=5)

        # Row 1: Callsign, Frequency, Mode
        row1 = ttk.Frame(entry_frame)
        row1.pack(fill='x', pady=2)

        ttk.Label(row1, text="Callsign:", width=12, anchor='e').pack(side='left')
        self.callsign_var = tk.StringVar()
        self.callsign_entry = ttk.Entry(row1, textvariable=self.callsign_var, width=15, font=('', 12, 'bold'))
        self.callsign_entry.pack(side='left', padx=5)

        self.lookup_btn = ttk.Button(row1, text="Lookup", command=self.lookup_callsign, width=8)
        self.lookup_btn.pack(side='left', padx=2)

        ttk.Label(row1, text="Frequency:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.freq_var = tk.StringVar()
        self.freq_entry = ttk.Entry(row1, textvariable=self.freq_var, width=12)
        self.freq_entry.pack(side='left', padx=5)

        ttk.Label(row1, text="Band:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.band_var = tk.StringVar()
        band_combo = ttk.Combobox(row1, textvariable=self.band_var, width=8, state='readonly')
        band_combo['values'] = ('160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '6m', '2m', '70cm')
        band_combo.pack(side='left', padx=5)

        ttk.Label(row1, text="Mode:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(row1, textvariable=self.mode_var, width=10)
        mode_combo['values'] = ('SSB', 'CW', 'FT8', 'FT4', 'RTTY', 'PSK31', 'PSK63',
                               'MFSK', 'JT65', 'JT9', 'AM', 'FM', 'DATA')
        mode_combo.pack(side='left', padx=5)

        # Row 2: Date, Time ON, Time OFF, Power, RST
        row2 = ttk.Frame(entry_frame)
        row2.pack(fill='x', pady=2)

        ttk.Label(row2, text="Date:", width=12, anchor='e').pack(side='left')
        self.date_var = tk.StringVar(value=datetime.utcnow().strftime("%Y-%m-%d"))
        ttk.Entry(row2, textvariable=self.date_var, width=12).pack(side='left', padx=5)

        ttk.Label(row2, text="Time ON:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.time_on_var = tk.StringVar(value=datetime.utcnow().strftime("%H:%M"))
        ttk.Entry(row2, textvariable=self.time_on_var, width=8).pack(side='left', padx=5)

        ttk.Label(row2, text="Time OFF:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.time_off_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.time_off_var, width=8).pack(side='left', padx=5)

        ttk.Label(row2, text="Power:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.power_var = tk.StringVar(value=self.config.get('default_power', '100'))
        ttk.Entry(row2, textvariable=self.power_var, width=8).pack(side='left', padx=5)
        ttk.Label(row2, text="W").pack(side='left')

        ttk.Label(row2, text="RST Sent:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.rst_sent_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row2, textvariable=self.rst_sent_var, width=6).pack(side='left', padx=5)

        ttk.Label(row2, text="RST Rcvd:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.rst_rcvd_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row2, textvariable=self.rst_rcvd_var, width=6).pack(side='left', padx=5)

        # Row 3: Name, QTH, Grid
        row3 = ttk.Frame(entry_frame)
        row3.pack(fill='x', pady=2)

        ttk.Label(row3, text="Name:", width=12, anchor='e').pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.name_var, width=20).pack(side='left', padx=5)

        ttk.Label(row3, text="QTH:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.qth_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.qth_var, width=25).pack(side='left', padx=5)

        ttk.Label(row3, text="Grid:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.grid_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.grid_var, width=10).pack(side='left', padx=5)

        # Row 4: Country, State, County
        row4 = ttk.Frame(entry_frame)
        row4.pack(fill='x', pady=2)

        ttk.Label(row4, text="Country:", width=12, anchor='e').pack(side='left')
        self.country_var = tk.StringVar()
        self.country_entry = ttk.Entry(row4, textvariable=self.country_var, width=20, state='readonly')
        self.country_entry.pack(side='left', padx=5)

        ttk.Label(row4, text="State:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.state_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.state_var, width=8).pack(side='left', padx=5)

        ttk.Label(row4, text="County:", width=8, anchor='e').pack(side='left', padx=(10, 0))
        self.county_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.county_var, width=20).pack(side='left', padx=5)

        # Row 5: Continent, CQ Zone, ITU Zone
        row5 = ttk.Frame(entry_frame)
        row5.pack(fill='x', pady=2)

        ttk.Label(row5, text="Continent:", width=12, anchor='e').pack(side='left')
        self.continent_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.continent_var, width=8, state='readonly').pack(side='left', padx=5)

        ttk.Label(row5, text="CQ Zone:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.cq_zone_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.cq_zone_var, width=6).pack(side='left', padx=5)

        ttk.Label(row5, text="ITU Zone:", width=10, anchor='e').pack(side='left', padx=(10, 0))
        self.itu_zone_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.itu_zone_var, width=6).pack(side='left', padx=5)

        ttk.Label(row5, text="IOTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.iota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.iota_var, width=12).pack(side='left', padx=5)

        ttk.Label(row5, text="SOTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.sota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.sota_var, width=12).pack(side='left', padx=5)

        ttk.Label(row5, text="POTA:", width=6, anchor='e').pack(side='left', padx=(10, 0))
        self.pota_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.pota_var, width=12).pack(side='left', padx=5)

        # Row 6: Notes/Comments
        row6 = ttk.Frame(entry_frame)
        row6.pack(fill='x', pady=2)

        ttk.Label(row6, text="Notes:", width=12, anchor='e').pack(side='left')
        self.notes_var = tk.StringVar()
        ttk.Entry(row6, textvariable=self.notes_var, width=80).pack(side='left', padx=5, fill='x', expand=True)

        # Button row
        btn_row = ttk.Frame(entry_frame)
        btn_row.pack(fill='x', pady=10)

        self.log_btn = ttk.Button(btn_row, text="Log Contact (Enter)", command=self.log_contact,
                                  style='Accent.TButton')
        self.log_btn.pack(side='left', padx=5)

        ttk.Button(btn_row, text="Clear (Esc)", command=self.clear_form).pack(side='left', padx=5)

        if self.config.get('qrz.api_key'):
            self.qrz_upload_btn = ttk.Button(btn_row, text="Upload to QRZ",
                                            command=self.upload_to_qrz, state='disabled')
            self.qrz_upload_btn.pack(side='left', padx=5)

        self.dupe_label = ttk.Label(btn_row, text="", foreground="red", font=('', 10, 'bold'))
        self.dupe_label.pack(side='left', padx=20)

        # Keyboard shortcuts
        self.frame.bind_all('<Control-Return>', lambda e: self.log_contact())
        self.frame.bind_all('<Escape>', lambda e: self.clear_form())

        # Log display frame
        log_frame = ttk.LabelFrame(self.frame, text="Contact Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for contacts
        columns = ('Call', 'Date', 'Time', 'Freq', 'Mode', 'RST', 'Name', 'Country', 'Grid')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=12)

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

    def on_callsign_changed(self, event=None):
        """Handle callsign field change - auto lookup if enabled"""
        callsign = self.callsign_var.get().strip().upper()

        if not callsign:
            return

        self.callsign_var.set(callsign)

        # Check for duplicates if enabled
        if self.config.get('logging.warn_duplicates', True):
            self.check_duplicate()

        # Auto-lookup if enabled
        if self.config.get('logging.auto_lookup', True):
            self.lookup_callsign(auto=True)

    def check_duplicate(self):
        """Check if this is a duplicate contact"""
        callsign = self.callsign_var.get().strip().upper()
        band = self.band_var.get()
        mode = self.mode_var.get()
        date = self.date_var.get()

        if not all([callsign, band, mode, date]):
            self.dupe_label.config(text="")
            return

        dupe = self.database.check_duplicate(callsign, band, mode, date)

        if dupe:
            self.dupe_label.config(text=f"⚠️ DUPLICATE - Worked on {dupe['time_on']}")
        else:
            self.dupe_label.config(text="")

    def on_frequency_changed(self, event=None):
        """Auto-select band when frequency is entered"""
        try:
            freq_str = self.freq_var.get().strip()
            if not freq_str:
                return

            freq = float(freq_str)

            # Map frequency to band
            if 1.8 <= freq < 2.0:
                self.band_var.set('160m')
            elif 3.5 <= freq < 4.0:
                self.band_var.set('80m')
            elif 5.0 <= freq < 5.5:
                self.band_var.set('60m')
            elif 7.0 <= freq < 7.3:
                self.band_var.set('40m')
            elif 10.1 <= freq < 10.15:
                self.band_var.set('30m')
            elif 14.0 <= freq < 14.35:
                self.band_var.set('20m')
            elif 18.068 <= freq < 18.168:
                self.band_var.set('17m')
            elif 21.0 <= freq < 21.45:
                self.band_var.set('15m')
            elif 24.89 <= freq < 24.99:
                self.band_var.set('12m')
            elif 28.0 <= freq < 29.7:
                self.band_var.set('10m')
            elif 50.0 <= freq < 54.0:
                self.band_var.set('6m')
            elif 144.0 <= freq < 148.0:
                self.band_var.set('2m')
            elif 420.0 <= freq < 450.0:
                self.band_var.set('70cm')

            # Check for duplicates after band is set
            if self.config.get('logging.warn_duplicates', True):
                self.check_duplicate()

        except ValueError:
            pass

    def lookup_callsign(self, auto=False):
        """Lookup callsign using QRZ and DXCC"""
        callsign = self.callsign_var.get().strip().upper()

        if not callsign:
            if not auto:
                messagebox.showwarning("Missing Callsign", "Please enter a callsign")
            return

        # First try DXCC lookup (always available)
        dxcc_info = lookup_dxcc(callsign)
        if dxcc_info:
            self.country_var.set(dxcc_info['country'])
            self.continent_var.set(dxcc_info['continent'])
            self.cq_zone_var.set(str(dxcc_info['cq_zone']))
            self.itu_zone_var.set(str(dxcc_info['itu_zone']))

        # Then try QRZ lookup if enabled and configured
        if not self.config.get('qrz.enable_lookup', False):
            return

        qrz_user = self.config.get('qrz.username')
        qrz_pass = self.config.get('qrz.password')

        if not qrz_user or not qrz_pass:
            if not auto:
                # Provide specific feedback about what's missing
                missing_items = []
                if not qrz_user:
                    missing_items.append("Username")
                if not qrz_pass:
                    missing_items.append("Password")

                missing_text = " and ".join(missing_items)
                messagebox.showinfo("QRZ Not Configured",
                                   f"QRZ {missing_text} not configured.\n\n"
                                   "Please go to Settings tab and enter your QRZ credentials,\n"
                                   "then click 'Save Settings' to enable lookups.\n\n"
                                   "Note: QRZ XML lookups require a separate XML Data subscription.")
            return

        # Create session if needed
        if not self.qrz_session:
            self.qrz_session = QRZSession(qrz_user, qrz_pass)

        # Lookup callsign
        try:
            data = self.qrz_session.lookup_callsign(callsign)

            if data:
                # Populate fields from QRZ data
                if 'name' in data and data['name']:
                    # Combine first and last name
                    name = data.get('first_name', '') + ' ' + data.get('name', '')
                    self.name_var.set(name.strip())

                if 'gridsquare' in data:
                    self.grid_var.set(data['gridsquare'])

                if 'state' in data:
                    self.state_var.set(data['state'])

                if 'county' in data:
                    self.county_var.set(data['county'])

                # QRZ data overrides DXCC for zones if available
                if 'cq_zone' in data:
                    self.cq_zone_var.set(data['cq_zone'])

                if 'itu_zone' in data:
                    self.itu_zone_var.set(data['itu_zone'])

                if not auto:
                    messagebox.showinfo("Lookup Successful", f"Found {callsign} on QRZ")
            else:
                if not auto:
                    messagebox.showinfo("Not Found", f"{callsign} not found on QRZ")

        except Exception as e:
            if not auto:
                messagebox.showerror("Lookup Error", f"Error looking up callsign: {str(e)}")

    def log_contact(self):
        """Save contact to database"""
        callsign = self.callsign_var.get().strip().upper()
        if not callsign:
            messagebox.showwarning("Missing Data", "Callsign is required")
            self.callsign_entry.focus()
            return

        # Auto-fill time off if enabled
        if self.config.get('logging.auto_time_off', True) and not self.time_off_var.get():
            self.time_off_var.set(datetime.utcnow().strftime("%H:%M"))

        contact_data = {
            'callsign': callsign,
            'date': self.date_var.get(),
            'time_on': self.time_on_var.get(),
            'time_off': self.time_off_var.get(),
            'frequency': self.freq_var.get(),
            'band': self.band_var.get(),
            'mode': self.mode_var.get(),
            'rst_sent': self.rst_sent_var.get(),
            'rst_rcvd': self.rst_rcvd_var.get(),
            'power': self.power_var.get(),
            'name': self.name_var.get(),
            'qth': self.qth_var.get(),
            'gridsquare': self.grid_var.get(),
            'county': self.county_var.get(),
            'state': self.state_var.get(),
            'country': self.country_var.get(),
            'continent': self.continent_var.get(),
            'cq_zone': self.cq_zone_var.get(),
            'itu_zone': self.itu_zone_var.get(),
            'iota': self.iota_var.get(),
            'sota': self.sota_var.get(),
            'pota': self.pota_var.get(),
            'my_gridsquare': self.config.get('gridsquare', ''),
            'notes': self.notes_var.get()
        }

        try:
            contact_id = self.database.add_contact(contact_data)

            # Auto-upload to QRZ if enabled
            if self.config.get('qrz.auto_upload', False):
                self.upload_to_qrz(contact_data)
            else:
                messagebox.showinfo("Success", f"Contact with {callsign} logged!")

            self.clear_form()
            self.refresh_log()

            # Enable manual QRZ upload button if configured
            if hasattr(self, 'qrz_upload_btn'):
                self.qrz_upload_btn.config(state='normal')
                self.last_contact_data = contact_data

        except Exception as e:
            messagebox.showerror("Error", f"Failed to log contact: {str(e)}")

    def upload_to_qrz(self, contact_data=None):
        """Upload contact to QRZ Logbook"""
        api_key = self.config.get('qrz.api_key')

        if not api_key:
            messagebox.showwarning("QRZ Not Configured",
                                 "QRZ API Key not configured.\n\n"
                                 "Please go to Settings tab and enter your QRZ API key,\n"
                                 "then click 'Save Settings' to enable QRZ Logbook uploads.\n\n"
                                 "Get your API key from: https://www.qrz.com/page/current_spec.html")
            return

        if contact_data is None:
            contact_data = getattr(self, 'last_contact_data', None)

        if not contact_data:
            messagebox.showwarning("No Contact", "No contact to upload")
            return

        try:
            success, message = upload_to_qrz_logbook(api_key, contact_data)

            if success:
                messagebox.showinfo("QRZ Upload Successful", message)
                if hasattr(self, 'qrz_upload_btn'):
                    self.qrz_upload_btn.config(state='disabled')
            else:
                messagebox.showerror("QRZ Upload Failed", message)

        except Exception as e:
            messagebox.showerror("Upload Error", f"Error uploading to QRZ: {str(e)}")

    def clear_form(self):
        """Clear all input fields"""
        self.callsign_var.set('')
        self.date_var.set(datetime.utcnow().strftime("%Y-%m-%d"))
        self.time_on_var.set(datetime.utcnow().strftime("%H:%M"))
        self.time_off_var.set('')
        self.freq_var.set('')
        self.band_var.set('')
        self.mode_var.set('')
        self.rst_sent_var.set(self.config.get('default_rst', '59'))
        self.rst_rcvd_var.set(self.config.get('default_rst', '59'))
        self.power_var.set(self.config.get('default_power', '100'))
        self.name_var.set('')
        self.qth_var.set('')
        self.grid_var.set('')
        self.county_var.set('')
        self.state_var.set('')
        self.country_var.set('')
        self.continent_var.set('')
        self.cq_zone_var.set('')
        self.itu_zone_var.set('')
        self.iota_var.set('')
        self.sota_var.set('')
        self.pota_var.set('')
        self.notes_var.set('')
        self.dupe_label.config(text='')
        self.callsign_entry.focus()

        if hasattr(self, 'qrz_upload_btn'):
            self.qrz_upload_btn.config(state='disabled')

    def refresh_log(self):
        """Refresh the contact log display"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Load contacts from database
        contacts = self.database.get_all_contacts(limit=100)
        for contact in contacts:
            # Convert sqlite3.Row to dict to safely access optional fields
            contact_dict = dict(contact)
            self.log_tree.insert('', 'end', values=(
                contact_dict.get('callsign', ''),
                contact_dict.get('date', ''),
                contact_dict.get('time_on', ''),
                contact_dict.get('frequency', ''),
                contact_dict.get('mode', ''),
                f"{contact_dict.get('rst_sent', '')}/{contact_dict.get('rst_rcvd', '')}",
                contact_dict.get('name', ''),
                contact_dict.get('country', ''),
                contact_dict.get('gridsquare', '')
            ))

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
