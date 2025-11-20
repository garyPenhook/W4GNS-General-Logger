"""
Contest Logging Tab for SKCC WES and K3Y events
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timezone
import threading

from src.theme_colors import get_muted_color, get_info_color


class ContestTab:
    def __init__(self, notebook, database, config):
        self.notebook = notebook
        self.database = database
        self.config = config

        # Contest state
        self.contest_active = False
        self.contest_type = 'WES'
        self.contest_start = None
        self.contest_end = None

        # Bonus point values (change monthly - check SKCC website)
        self.bonus_c = config.get('contest.bonus_c', 5)
        self.bonus_t = config.get('contest.bonus_t', 10)
        self.bonus_s = config.get('contest.bonus_s', 15)
        self.bonus_kcc = config.get('contest.bonus_kcc', 25)

        # Scoring data
        self.qso_points = 0
        self.multipliers = set()  # States/provinces/countries
        self.centurions = set()  # Callsigns with C bonus
        self.tribunes = set()  # Callsigns with T bonus
        self.senators = set()  # Callsigns with S bonus
        self.ks1kcc_bands = set()  # Bands worked KS1KCC
        self.worked_stations = {}  # {callsign: set of bands}
        self.contest_qsos = []  # List of QSOs in current contest

        self.frame = ttk.Frame(notebook)
        self.create_widgets()

    def get_frame(self):
        return self.frame

    def create_widgets(self):
        """Create the contest logging interface"""
        # Main container with two columns
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        # LEFT COLUMN - Entry and controls
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side='left', fill='both', expand=True)

        # Contest Control Frame
        control_frame = ttk.LabelFrame(left_frame, text="Contest Control", padding=10)
        control_frame.pack(fill='x', pady=5)

        # Contest type selection
        type_row = ttk.Frame(control_frame)
        type_row.pack(fill='x', pady=2)

        ttk.Label(type_row, text="Contest:", width=10).pack(side='left')
        self.contest_type_var = tk.StringVar(value='WES')
        contest_combo = ttk.Combobox(type_row, textvariable=self.contest_type_var,
                                     width=20, state='readonly')
        contest_combo['values'] = ('WES - Weekend Sprintathon', 'K3Y - Straight Key Month')
        contest_combo.pack(side='left', padx=5)

        # Start/Stop buttons
        btn_row = ttk.Frame(control_frame)
        btn_row.pack(fill='x', pady=5)

        self.start_btn = ttk.Button(btn_row, text="Start Contest",
                                    command=self.start_contest, width=15)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(btn_row, text="End Contest",
                                   command=self.end_contest, width=15, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        # Contest status
        self.status_label = ttk.Label(control_frame, text="No contest active",
                                      font=('', 10, 'italic'),
                                      foreground=get_muted_color(self.config))
        self.status_label.pack(pady=5)

        # Bonus Configuration Frame (values change monthly)
        bonus_frame = ttk.LabelFrame(left_frame, text="Bonus Points (Update Monthly)", padding=5)
        bonus_frame.pack(fill='x', pady=5)

        bonus_row1 = ttk.Frame(bonus_frame)
        bonus_row1.pack(fill='x', pady=2)

        ttk.Label(bonus_row1, text="C:", width=3).pack(side='left')
        self.bonus_c_var = tk.StringVar(value=str(self.bonus_c))
        ttk.Entry(bonus_row1, textvariable=self.bonus_c_var, width=4).pack(side='left', padx=2)

        ttk.Label(bonus_row1, text="T:", width=3).pack(side='left', padx=(10, 0))
        self.bonus_t_var = tk.StringVar(value=str(self.bonus_t))
        ttk.Entry(bonus_row1, textvariable=self.bonus_t_var, width=4).pack(side='left', padx=2)

        ttk.Label(bonus_row1, text="S:", width=3).pack(side='left', padx=(10, 0))
        self.bonus_s_var = tk.StringVar(value=str(self.bonus_s))
        ttk.Entry(bonus_row1, textvariable=self.bonus_s_var, width=4).pack(side='left', padx=2)

        ttk.Label(bonus_row1, text="KS1KCC:", width=8).pack(side='left', padx=(10, 0))
        self.bonus_kcc_var = tk.StringVar(value=str(self.bonus_kcc))
        ttk.Entry(bonus_row1, textvariable=self.bonus_kcc_var, width=4).pack(side='left', padx=2)

        ttk.Button(bonus_row1, text="Save", command=self.save_bonus_values, width=6).pack(side='left', padx=(10, 0))

        ttk.Label(bonus_frame, text="Check skccgroup.com/operating_activities/weekend_sprintathon for current values",
                  font=('', 8), foreground=get_muted_color(self.config)).pack(pady=2)

        # QSO Entry Frame
        entry_frame = ttk.LabelFrame(left_frame, text="Log QSO", padding=10)
        entry_frame.pack(fill='x', pady=5)

        # Row 1: Callsign
        row1 = ttk.Frame(entry_frame)
        row1.pack(fill='x', pady=2)

        ttk.Label(row1, text="Callsign:", width=10).pack(side='left')
        self.callsign_var = tk.StringVar()
        self.callsign_entry = ttk.Entry(row1, textvariable=self.callsign_var,
                                        width=15, font=('', 14, 'bold'))
        self.callsign_entry.pack(side='left', padx=5)
        self.callsign_entry.bind('<Return>', lambda e: self.rst_sent_entry.focus())
        self.callsign_entry.bind('<KeyRelease>', self.on_callsign_change)

        # Duplicate warning label
        self.dupe_label = ttk.Label(row1, text="", foreground='red', font=('', 10, 'bold'))
        self.dupe_label.pack(side='left', padx=10)

        # Row 2: RST Sent/Rcvd
        row2 = ttk.Frame(entry_frame)
        row2.pack(fill='x', pady=2)

        ttk.Label(row2, text="RST Sent:", width=10).pack(side='left')
        self.rst_sent_var = tk.StringVar(value='599')
        self.rst_sent_entry = ttk.Entry(row2, textvariable=self.rst_sent_var, width=6)
        self.rst_sent_entry.pack(side='left', padx=5)
        self.rst_sent_entry.bind('<Return>', lambda e: self.rst_rcvd_entry.focus())

        ttk.Label(row2, text="RST Rcvd:", width=10).pack(side='left', padx=(20, 0))
        self.rst_rcvd_var = tk.StringVar(value='599')
        self.rst_rcvd_entry = ttk.Entry(row2, textvariable=self.rst_rcvd_var, width=6)
        self.rst_rcvd_entry.pack(side='left', padx=5)
        self.rst_rcvd_entry.bind('<Return>', lambda e: self.name_entry.focus())

        # Row 3: Name and QTH (exchange)
        row3 = ttk.Frame(entry_frame)
        row3.pack(fill='x', pady=2)

        ttk.Label(row3, text="Name:", width=10).pack(side='left')
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(row3, textvariable=self.name_var, width=15)
        self.name_entry.pack(side='left', padx=5)
        self.name_entry.bind('<Return>', lambda e: self.qth_entry.focus())

        ttk.Label(row3, text="QTH:", width=10).pack(side='left', padx=(20, 0))
        self.qth_var = tk.StringVar()
        self.qth_entry = ttk.Entry(row3, textvariable=self.qth_var, width=10)
        self.qth_entry.pack(side='left', padx=5)
        self.qth_entry.bind('<Return>', lambda e: self.skcc_entry.focus())

        # Row 4: SKCC Number
        row4 = ttk.Frame(entry_frame)
        row4.pack(fill='x', pady=2)

        ttk.Label(row4, text="SKCC #:", width=10).pack(side='left')
        self.skcc_var = tk.StringVar()
        self.skcc_entry = ttk.Entry(row4, textvariable=self.skcc_var, width=12)
        self.skcc_entry.pack(side='left', padx=5)
        self.skcc_entry.bind('<Return>', lambda e: self.log_qso())

        # SKCC status display
        self.skcc_status = ttk.Label(row4, text="", font=('', 9))
        self.skcc_status.pack(side='left', padx=10)

        # Row 5: Frequency and Band
        row5 = ttk.Frame(entry_frame)
        row5.pack(fill='x', pady=2)

        ttk.Label(row5, text="Frequency:", width=10).pack(side='left')
        self.freq_var = tk.StringVar()
        self.freq_entry = ttk.Entry(row5, textvariable=self.freq_var, width=12)
        self.freq_entry.pack(side='left', padx=5)

        ttk.Label(row5, text="Band:", width=10).pack(side='left', padx=(20, 0))
        self.band_var = tk.StringVar(value='40m')
        band_combo = ttk.Combobox(row5, textvariable=self.band_var, width=8, state='readonly')
        band_combo['values'] = ('160m', '80m', '40m', '20m', '15m', '10m')
        band_combo.pack(side='left', padx=5)

        # Log button
        btn_frame = ttk.Frame(entry_frame)
        btn_frame.pack(fill='x', pady=10)

        self.log_btn = ttk.Button(btn_frame, text="Log QSO (Enter)",
                                  command=self.log_qso, state='disabled')
        self.log_btn.pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side='left', padx=5)

        # RIGHT COLUMN - Scoring
        right_frame = ttk.Frame(main_container, width=300)
        right_frame.pack(side='right', fill='both', padx=(10, 0))
        right_frame.pack_propagate(False)

        # Score Display
        score_frame = ttk.LabelFrame(right_frame, text="Score", padding=10)
        score_frame.pack(fill='x', pady=5)

        # Total score (big display)
        self.total_score_var = tk.StringVar(value="0")
        ttk.Label(score_frame, textvariable=self.total_score_var,
                  font=('', 32, 'bold')).pack(pady=5)

        # Score breakdown
        breakdown_frame = ttk.Frame(score_frame)
        breakdown_frame.pack(fill='x')

        # QSO Points
        qso_row = ttk.Frame(breakdown_frame)
        qso_row.pack(fill='x', pady=1)
        ttk.Label(qso_row, text="QSO Points:").pack(side='left')
        self.qso_points_var = tk.StringVar(value="0")
        ttk.Label(qso_row, textvariable=self.qso_points_var).pack(side='right')

        # Multipliers
        mult_row = ttk.Frame(breakdown_frame)
        mult_row.pack(fill='x', pady=1)
        ttk.Label(mult_row, text="Multipliers:").pack(side='left')
        self.mult_var = tk.StringVar(value="0")
        ttk.Label(mult_row, textvariable=self.mult_var).pack(side='right')

        # C/T/S Bonus
        bonus_row = ttk.Frame(breakdown_frame)
        bonus_row.pack(fill='x', pady=1)
        ttk.Label(bonus_row, text="C/T/S Bonus:").pack(side='left')
        self.bonus_var = tk.StringVar(value="0")
        ttk.Label(bonus_row, textvariable=self.bonus_var).pack(side='right')

        # KS1KCC Bonus
        kcc_row = ttk.Frame(breakdown_frame)
        kcc_row.pack(fill='x', pady=1)
        ttk.Label(kcc_row, text="KS1KCC Bonus:").pack(side='left')
        self.kcc_var = tk.StringVar(value="0")
        ttk.Label(kcc_row, textvariable=self.kcc_var).pack(side='right')

        # Rate display
        rate_frame = ttk.LabelFrame(right_frame, text="Rate", padding=10)
        rate_frame.pack(fill='x', pady=5)

        rate_row = ttk.Frame(rate_frame)
        rate_row.pack(fill='x')
        ttk.Label(rate_row, text="QSOs/Hour:").pack(side='left')
        self.rate_var = tk.StringVar(value="0")
        ttk.Label(rate_row, textvariable=self.rate_var, font=('', 12, 'bold')).pack(side='right')

        qso_count_row = ttk.Frame(rate_frame)
        qso_count_row.pack(fill='x')
        ttk.Label(qso_count_row, text="Total QSOs:").pack(side='left')
        self.qso_count_var = tk.StringVar(value="0")
        ttk.Label(qso_count_row, textvariable=self.qso_count_var).pack(side='right')

        # Export button
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(fill='x', pady=10)

        ttk.Button(export_frame, text="Export for SKCC",
                   command=self.export_for_skcc).pack(fill='x')

        # Contest Log (bottom)
        log_frame = ttk.LabelFrame(self.frame, text="Contest Log", padding=5)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview for contest log
        columns = ('Time', 'Callsign', 'RST S', 'RST R', 'Name', 'QTH', 'SKCC', 'Band', 'Pts', 'Mult')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=8)

        # Configure columns
        self.log_tree.heading('Time', text='Time')
        self.log_tree.heading('Callsign', text='Callsign')
        self.log_tree.heading('RST S', text='RST S')
        self.log_tree.heading('RST R', text='RST R')
        self.log_tree.heading('Name', text='Name')
        self.log_tree.heading('QTH', text='QTH')
        self.log_tree.heading('SKCC', text='SKCC')
        self.log_tree.heading('Band', text='Band')
        self.log_tree.heading('Pts', text='Pts')
        self.log_tree.heading('Mult', text='Mult')

        self.log_tree.column('Time', width=60)
        self.log_tree.column('Callsign', width=100)
        self.log_tree.column('RST S', width=50)
        self.log_tree.column('RST R', width=50)
        self.log_tree.column('Name', width=80)
        self.log_tree.column('QTH', width=60)
        self.log_tree.column('SKCC', width=80)
        self.log_tree.column('Band', width=50)
        self.log_tree.column('Pts', width=40)
        self.log_tree.column('Mult', width=50)

        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        self.log_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind keyboard shortcuts
        self.frame.bind_all('<Control-Return>', lambda e: self.log_qso() if self.contest_active else None)

    def start_contest(self):
        """Start a new contest session"""
        # Confirm if there's existing data
        if self.contest_qsos:
            if not messagebox.askyesno("Start New Contest",
                    "This will clear the current contest data. Continue?"):
                return

        # Reset all data
        self.reset_contest_data()

        # Set contest active
        self.contest_active = True
        self.contest_type = self.contest_type_var.get().split(' - ')[0]
        self.contest_start = datetime.now(timezone.utc)

        # Update UI
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.log_btn.config(state='normal')
        self.status_label.config(
            text=f"{self.contest_type} started at {self.contest_start.strftime('%H:%M')} UTC",
            foreground=get_info_color(self.config)
        )

        # Focus on callsign entry
        self.callsign_entry.focus()

        # Start rate update timer
        self.update_rate()

    def save_bonus_values(self):
        """Save bonus point values to config"""
        try:
            self.bonus_c = int(self.bonus_c_var.get())
            self.bonus_t = int(self.bonus_t_var.get())
            self.bonus_s = int(self.bonus_s_var.get())
            self.bonus_kcc = int(self.bonus_kcc_var.get())

            self.config.set('contest.bonus_c', self.bonus_c)
            self.config.set('contest.bonus_t', self.bonus_t)
            self.config.set('contest.bonus_s', self.bonus_s)
            self.config.set('contest.bonus_kcc', self.bonus_kcc)

            # Recalculate score with new values
            self.update_score_display()

            messagebox.showinfo("Saved", "Bonus values saved")
        except ValueError:
            messagebox.showerror("Error", "Invalid bonus value - must be numbers")

    def end_contest(self):
        """End the current contest session"""
        if not messagebox.askyesno("End Contest",
                f"End the {self.contest_type} session?\n\n"
                f"Total QSOs: {len(self.contest_qsos)}\n"
                f"Final Score: {self.total_score_var.get()}"):
            return

        self.contest_active = False
        self.contest_end = datetime.now(timezone.utc)

        # Update UI
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.log_btn.config(state='disabled')

        duration = self.contest_end - self.contest_start
        hours = duration.total_seconds() / 3600
        self.status_label.config(
            text=f"{self.contest_type} ended - {len(self.contest_qsos)} QSOs in {hours:.1f} hours",
            foreground=get_muted_color(self.config)
        )

    def reset_contest_data(self):
        """Reset all contest tracking data"""
        self.qso_points = 0
        self.multipliers = set()
        self.centurions = set()
        self.tribunes = set()
        self.senators = set()
        self.ks1kcc_bands = set()
        self.worked_stations = {}
        self.contest_qsos = []

        # Clear log display
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        # Reset score display
        self.update_score_display()

    def on_callsign_change(self, event=None):
        """Handle callsign entry changes"""
        callsign = self.callsign_var.get().strip().upper()
        band = self.band_var.get()

        # Check for duplicate
        if callsign in self.worked_stations:
            worked_bands = self.worked_stations[callsign]
            if band in worked_bands:
                self.dupe_label.config(text=f"DUPE on {band}!")
            else:
                self.dupe_label.config(text=f"Worked: {', '.join(sorted(worked_bands))}")
        else:
            self.dupe_label.config(text="")

    def log_qso(self):
        """Log a QSO to the contest"""
        if not self.contest_active:
            return

        callsign = self.callsign_var.get().strip().upper()
        if not callsign:
            messagebox.showwarning("Missing Data", "Callsign is required")
            self.callsign_entry.focus()
            return

        band = self.band_var.get()

        # Check for exact duplicate (same callsign + band)
        if callsign in self.worked_stations and band in self.worked_stations[callsign]:
            if not messagebox.askyesno("Duplicate QSO",
                    f"{callsign} already worked on {band}.\nLog anyway?"):
                return

        # Get current UTC time
        now = datetime.now(timezone.utc)
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%Y-%m-%d")

        # Get exchange data
        rst_sent = self.rst_sent_var.get().strip() or '599'
        rst_rcvd = self.rst_rcvd_var.get().strip() or '599'
        name = self.name_var.get().strip()
        qth = self.qth_var.get().strip().upper()
        skcc = self.skcc_var.get().strip().upper()
        freq = self.freq_var.get().strip()

        # Calculate points for this QSO
        qso_pts = 1
        mult_new = ""

        # Track station by band
        if callsign not in self.worked_stations:
            self.worked_stations[callsign] = set()
        self.worked_stations[callsign].add(band)

        # Check for new multiplier (state/province/country)
        if qth and qth not in self.multipliers:
            self.multipliers.add(qth)
            mult_new = "NEW"

        # Check for C/T/S bonus
        bonus_pts = 0
        if skcc:
            # Extract just the number part for tracking
            skcc_num = ''.join(c for c in skcc if c.isdigit())

            if 'S' in skcc and skcc_num not in self.senators:
                self.senators.add(skcc_num)
                bonus_pts = self.bonus_s
            elif 'T' in skcc and skcc_num not in self.tribunes:
                self.tribunes.add(skcc_num)
                bonus_pts = self.bonus_t
            elif 'C' in skcc and skcc_num not in self.centurions:
                self.centurions.add(skcc_num)
                bonus_pts = self.bonus_c

        # Check for KS1KCC bonus
        if callsign == 'KS1KCC' and band not in self.ks1kcc_bands:
            self.ks1kcc_bands.add(band)
            bonus_pts += self.bonus_kcc

        # Update QSO points
        self.qso_points += qso_pts

        # Store QSO data
        qso_data = {
            'callsign': callsign,
            'date': date_str,
            'time': time_str,
            'rst_sent': rst_sent,
            'rst_rcvd': rst_rcvd,
            'name': name,
            'qth': qth,
            'skcc': skcc,
            'band': band,
            'frequency': freq,
            'points': qso_pts,
            'bonus': bonus_pts,
            'mult_new': mult_new
        }
        self.contest_qsos.append(qso_data)

        # Add to log display
        self.log_tree.insert('', 0, values=(
            time_str, callsign, rst_sent, rst_rcvd, name, qth, skcc, band,
            qso_pts + bonus_pts, mult_new
        ))

        # Also save to main database
        self.save_to_database(qso_data)

        # Update score display
        self.update_score_display()

        # Clear form for next QSO
        self.clear_form()
        self.callsign_entry.focus()

    def save_to_database(self, qso_data):
        """Save the QSO to the main database"""
        try:
            contact = {
                'callsign': qso_data['callsign'],
                'date': qso_data['date'],
                'time_on': qso_data['time'].replace(':', ''),
                'time_off': qso_data['time'].replace(':', ''),
                'frequency': qso_data['frequency'],
                'band': qso_data['band'],
                'mode': 'CW',
                'rst_sent': qso_data['rst_sent'],
                'rst_rcvd': qso_data['rst_rcvd'],
                'name': qso_data['name'],
                'qth': qso_data['qth'],
                'skcc_number': qso_data['skcc'],
                'comment': f"{self.contest_type} Contest",
                'power': self.config.get('default_power', '100'),
            }

            self.database.add_contact(contact)
        except Exception as e:
            print(f"Error saving contest QSO to database: {e}")

    def update_score_display(self):
        """Update all score displays"""
        # Calculate bonuses using configurable values
        c_bonus = len(self.centurions) * self.bonus_c
        t_bonus = len(self.tribunes) * self.bonus_t
        s_bonus = len(self.senators) * self.bonus_s
        kcc_bonus = len(self.ks1kcc_bands) * self.bonus_kcc
        total_bonus = c_bonus + t_bonus + s_bonus + kcc_bonus

        # Calculate total: (QSO points × Multipliers) + Bonuses
        mult_count = len(self.multipliers)
        if mult_count == 0:
            mult_count = 1  # Avoid zero multiplier

        total = (self.qso_points * mult_count) + total_bonus

        # Update displays
        self.total_score_var.set(str(total))
        self.qso_points_var.set(str(self.qso_points))
        self.mult_var.set(str(len(self.multipliers)))
        self.bonus_var.set(str(c_bonus + t_bonus + s_bonus))
        self.kcc_var.set(str(kcc_bonus))
        self.qso_count_var.set(str(len(self.contest_qsos)))

    def update_rate(self):
        """Update the QSO rate display"""
        if not self.contest_active:
            return

        # Calculate rate based on last hour
        now = datetime.now(timezone.utc)
        one_hour_ago = now.timestamp() - 3600

        recent_qsos = 0
        for qso in self.contest_qsos:
            qso_time = datetime.strptime(f"{qso['date']} {qso['time']}", "%Y-%m-%d %H:%M")
            qso_time = qso_time.replace(tzinfo=timezone.utc)
            if qso_time.timestamp() > one_hour_ago:
                recent_qsos += 1

        self.rate_var.set(str(recent_qsos))

        # Schedule next update
        if self.contest_active:
            self.frame.after(60000, self.update_rate)  # Update every minute

    def clear_form(self):
        """Clear the entry form"""
        self.callsign_var.set('')
        self.name_var.set('')
        self.qth_var.set('')
        self.skcc_var.set('')
        self.rst_sent_var.set('599')
        self.rst_rcvd_var.set('599')
        self.dupe_label.config(text='')
        self.skcc_status.config(text='')

    def export_for_skcc(self):
        """Export contest log for SKCC submission"""
        if not self.contest_qsos:
            messagebox.showwarning("No Data", "No QSOs to export")
            return

        # Get user info
        my_call = self.config.get('callsign', 'N0CALL')
        my_skcc = self.config.get('skcc_number', '')
        my_name = self.config.get('operator_name', '')

        # Build filename
        date_str = datetime.now().strftime("%Y%m%d")
        default_filename = f"{my_call}_{self.contest_type}_{date_str}.txt"

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Contest Log"
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                # Header
                f.write(f"SKCC {self.contest_type} Log\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(f"Callsign: {my_call}\n")
                if my_skcc:
                    f.write(f"SKCC #: {my_skcc}\n")
                if my_name:
                    f.write(f"Name: {my_name}\n")
                f.write(f"\nContest: {self.contest_type}\n")
                if self.contest_start:
                    f.write(f"Start: {self.contest_start.strftime('%Y-%m-%d %H:%M')} UTC\n")
                if self.contest_end:
                    f.write(f"End: {self.contest_end.strftime('%Y-%m-%d %H:%M')} UTC\n")
                f.write(f"\n{'=' * 50}\n\n")

                # Score summary
                mult_count = len(self.multipliers) if self.multipliers else 1
                c_bonus = len(self.centurions) * self.bonus_c
                t_bonus = len(self.tribunes) * self.bonus_t
                s_bonus = len(self.senators) * self.bonus_s
                kcc_bonus = len(self.ks1kcc_bands) * self.bonus_kcc
                total = (self.qso_points * mult_count) + c_bonus + t_bonus + s_bonus + kcc_bonus

                f.write("SCORE SUMMARY\n")
                f.write(f"QSO Points: {self.qso_points}\n")
                f.write(f"Multipliers: {len(self.multipliers)}\n")
                f.write(f"Centurions: {len(self.centurions)} (×{self.bonus_c} = {c_bonus})\n")
                f.write(f"Tribunes: {len(self.tribunes)} (×{self.bonus_t} = {t_bonus})\n")
                f.write(f"Senators: {len(self.senators)} (×{self.bonus_s} = {s_bonus})\n")
                f.write(f"KS1KCC Bands: {len(self.ks1kcc_bands)} (×{self.bonus_kcc} = {kcc_bonus})\n")
                f.write(f"\nTOTAL SCORE: {total}\n")
                f.write(f"Formula: ({self.qso_points} × {mult_count}) + {c_bonus + t_bonus + s_bonus + kcc_bonus}\n")
                f.write(f"\n{'=' * 50}\n\n")

                # Multiplier list
                f.write("MULTIPLIERS\n")
                f.write(', '.join(sorted(self.multipliers)) + "\n")
                f.write(f"\n{'=' * 50}\n\n")

                # QSO Log
                f.write("QSO LOG\n")
                f.write(f"{'Date':<12} {'Time':<6} {'Call':<12} {'RST':<8} {'Name':<12} {'QTH':<8} {'SKCC':<12} {'Band':<6}\n")
                f.write("-" * 80 + "\n")

                for qso in self.contest_qsos:
                    f.write(f"{qso['date']:<12} {qso['time']:<6} {qso['callsign']:<12} "
                           f"{qso['rst_sent']}/{qso['rst_rcvd']:<4} {qso['name']:<12} "
                           f"{qso['qth']:<8} {qso['skcc']:<12} {qso['band']:<6}\n")

            messagebox.showinfo("Export Complete",
                f"Exported {len(self.contest_qsos)} QSOs to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting log:\n{str(e)}")
