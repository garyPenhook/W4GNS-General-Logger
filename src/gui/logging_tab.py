"""
Logging Tab - Main contact logging interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class LoggingTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def create_widgets(self):
        """Create the logging interface"""
        # Input frame
        input_frame = ttk.LabelFrame(self.frame, text="New Contact", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        # Row 1: Callsign, Date, Time
        row1 = ttk.Frame(input_frame)
        row1.pack(fill='x', pady=2)

        ttk.Label(row1, text="Callsign:").pack(side='left')
        self.callsign_var = tk.StringVar()
        self.callsign_entry = ttk.Entry(row1, textvariable=self.callsign_var, width=15)
        self.callsign_entry.pack(side='left', padx=5)

        # Add trace to callsign entry for auto-lookup
        self.callsign_var.trace_add('write', self.on_callsign_changed)

        ttk.Label(row1, text="Date:").pack(side='left', padx=(20, 0))
        self.date_var = tk.StringVar(value=datetime.utcnow().strftime("%Y-%m-%d"))
        ttk.Entry(row1, textvariable=self.date_var, width=12).pack(side='left', padx=5)

        ttk.Label(row1, text="Time ON:").pack(side='left', padx=(20, 0))
        self.time_on_var = tk.StringVar(value=datetime.utcnow().strftime("%H:%M"))
        ttk.Entry(row1, textvariable=self.time_on_var, width=8).pack(side='left', padx=5)

        # Row 2: Frequency, Band, Mode
        row2 = ttk.Frame(input_frame)
        row2.pack(fill='x', pady=2)

        ttk.Label(row2, text="Frequency:").pack(side='left')
        self.freq_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.freq_var, width=12).pack(side='left', padx=5)

        ttk.Label(row2, text="Band:").pack(side='left', padx=(20, 0))
        self.band_var = tk.StringVar()
        band_combo = ttk.Combobox(row2, textvariable=self.band_var, width=8)
        band_combo['values'] = ('160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m',
                                '12m', '10m', '6m', '2m', '70cm')
        band_combo.pack(side='left', padx=5)

        ttk.Label(row2, text="Mode:").pack(side='left', padx=(20, 0))
        self.mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(row2, textvariable=self.mode_var, width=10)
        mode_combo['values'] = ('SSB', 'CW', 'FT8', 'FT4', 'RTTY', 'PSK31', 'AM', 'FM')
        mode_combo.pack(side='left', padx=5)

        # Row 3: RST
        row3 = ttk.Frame(input_frame)
        row3.pack(fill='x', pady=2)

        ttk.Label(row3, text="RST Sent:").pack(side='left')
        self.rst_sent_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row3, textvariable=self.rst_sent_var, width=8).pack(side='left', padx=5)

        ttk.Label(row3, text="RST Rcvd:").pack(side='left', padx=(20, 0))
        self.rst_rcvd_var = tk.StringVar(value=self.config.get('default_rst', '59'))
        ttk.Entry(row3, textvariable=self.rst_rcvd_var, width=8).pack(side='left', padx=5)

        # Row 4: Name, QTH, Grid
        row4 = ttk.Frame(input_frame)
        row4.pack(fill='x', pady=2)

        ttk.Label(row4, text="Name:").pack(side='left')
        self.name_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.name_var, width=15).pack(side='left', padx=5)

        ttk.Label(row4, text="QTH:").pack(side='left', padx=(20, 0))
        self.qth_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.qth_var, width=20).pack(side='left', padx=5)

        ttk.Label(row4, text="Grid:").pack(side='left', padx=(20, 0))
        self.grid_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.grid_var, width=10).pack(side='left', padx=5)

        # Row 5: SKCC Number
        row5 = ttk.Frame(input_frame)
        row5.pack(fill='x', pady=2)

        ttk.Label(row5, text="SKCC #:").pack(side='left')
        self.skcc_number_var = tk.StringVar()
        ttk.Entry(row5, textvariable=self.skcc_number_var, width=15).pack(side='left', padx=5)

        self.skcc_status_label = ttk.Label(row5, text="", foreground='gray', font=('', 9, 'italic'))
        self.skcc_status_label.pack(side='left', padx=10)

        # Row 6: Notes
        row6 = ttk.Frame(input_frame)
        row6.pack(fill='x', pady=2)

        ttk.Label(row6, text="Notes:").pack(side='left')
        self.notes_var = tk.StringVar()
        ttk.Entry(row6, textvariable=self.notes_var, width=60).pack(side='left', padx=5, fill='x', expand=True)

        # Button row
        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill='x', pady=5)

        ttk.Button(btn_row, text="Log Contact", command=self.log_contact).pack(side='left', padx=5)
        ttk.Button(btn_row, text="Clear", command=self.clear_form).pack(side='left')

        # Log display frame
        log_frame = ttk.LabelFrame(self.frame, text="Contact Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for contacts
        columns = ('Callsign', 'Date', 'Time', 'Freq', 'Mode', 'RST', 'Name', 'QTH')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        self.log_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Load existing contacts
        self.refresh_log()

    def on_callsign_changed(self, *args):
        """
        Callback when callsign entry changes.
        Automatically looks up and fills in SKCC number from previous contacts.
        """
        callsign = self.callsign_var.get().strip().upper()

        if len(callsign) < 3:
            # Clear SKCC field and status if callsign too short
            self.skcc_number_var.set('')
            self.skcc_status_label.config(text='')
            return

        # Lookup SKCC number from previous contacts
        skcc_number = self.lookup_skcc_number(callsign)

        if skcc_number:
            self.skcc_number_var.set(skcc_number)
            self.skcc_status_label.config(text='(from previous contact)', foreground='green')
        else:
            # Only clear if user hasn't manually entered a number
            if not self.skcc_number_var.get():
                self.skcc_status_label.config(text='(no previous SKCC #)', foreground='gray')

    def lookup_skcc_number(self, callsign):
        """
        Look up SKCC number from previous contacts in database.

        Args:
            callsign: Callsign to search for

        Returns:
            SKCC number if found, None otherwise
        """
        if not callsign:
            return None

        try:
            # Get all contacts for this callsign
            cursor = self.database.conn.cursor()
            cursor.execute('''
                SELECT skcc_number
                FROM contacts
                WHERE UPPER(callsign) = ?
                  AND skcc_number IS NOT NULL
                  AND skcc_number != ''
                ORDER BY date DESC, time_on DESC
                LIMIT 1
            ''', (callsign.upper(),))

            result = cursor.fetchone()
            if result and result[0]:
                return result[0]

        except Exception as e:
            print(f"Error looking up SKCC number: {e}")

        return None

    def log_contact(self):
        """Save contact to database"""
        callsign = self.callsign_var.get().strip().upper()
        if not callsign:
            messagebox.showwarning("Missing Data", "Callsign is required")
            return

        contact_data = {
            'callsign': callsign,
            'date': self.date_var.get(),
            'time_on': self.time_on_var.get(),
            'time_off': '',
            'frequency': self.freq_var.get(),
            'band': self.band_var.get(),
            'mode': self.mode_var.get(),
            'rst_sent': self.rst_sent_var.get(),
            'rst_rcvd': self.rst_rcvd_var.get(),
            'name': self.name_var.get(),
            'qth': self.qth_var.get(),
            'gridsquare': self.grid_var.get(),
            'notes': self.notes_var.get(),
            'skcc_number': self.skcc_number_var.get().strip()
        }

        try:
            self.database.add_contact(contact_data)
            messagebox.showinfo("Success", f"Contact with {callsign} logged!")
            self.clear_form()
            self.refresh_log()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to log contact: {str(e)}")

    def clear_form(self):
        """Clear all input fields"""
        self.callsign_var.set('')
        self.date_var.set(datetime.utcnow().strftime("%Y-%m-%d"))
        self.time_on_var.set(datetime.utcnow().strftime("%H:%M"))
        self.freq_var.set('')
        self.band_var.set('')
        self.mode_var.set('')
        self.rst_sent_var.set(self.config.get('default_rst', '59'))
        self.rst_rcvd_var.set(self.config.get('default_rst', '59'))
        self.name_var.set('')
        self.qth_var.set('')
        self.grid_var.set('')
        self.notes_var.set('')
        self.skcc_number_var.set('')
        self.skcc_status_label.config(text='')
        self.callsign_entry.focus()

    def refresh_log(self):
        """Refresh the contact log display"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Load contacts from database
        contacts = self.database.get_all_contacts(limit=100)
        for contact in contacts:
            self.log_tree.insert('', 'end', values=(
                contact['callsign'],
                contact['date'],
                contact['time_on'],
                contact['frequency'],
                contact['mode'],
                f"{contact['rst_sent']}/{contact['rst_rcvd']}",
                contact['name'],
                contact['qth']
            ))

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
