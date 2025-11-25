"""
Monthly Brag Report Dialog

Generates a report of unique SKCC members worked during a selected month,
excluding contest contacts (WES, SKS, K3Y).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from calendar import monthrange


class MonthlyBragDialog:
    def __init__(self, parent, database, config):
        self.database = database
        self.config = config

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("SKCC Monthly Brag Report")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.center_window(parent)

        # Create UI
        self.create_widgets()

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
        """Create the dialog interface"""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Header
        header = ttk.Label(main_frame, text="SKCC Monthly Brag Report",
                          font=('', 16, 'bold'))
        header.pack(pady=(0, 10))

        # Description
        desc = ttk.Label(main_frame,
                        text="Count unique SKCC members worked during a month (excludes WES/SKS/K3Y contests)",
                        font=('', 9))
        desc.pack(pady=(0, 15))

        # Month selection frame
        select_frame = ttk.LabelFrame(main_frame, text="Select Month", padding=10)
        select_frame.pack(fill='x', pady=5)

        # Current date for defaults
        today = date.today()

        # Year selection
        year_row = ttk.Frame(select_frame)
        year_row.pack(fill='x', pady=2)
        ttk.Label(year_row, text="Year:", width=15).pack(side='left')
        self.year_var = tk.StringVar(value=str(today.year))
        year_spin = ttk.Spinbox(year_row, from_=2010, to=2050,
                               textvariable=self.year_var, width=10)
        year_spin.pack(side='left')

        # Month selection
        month_row = ttk.Frame(select_frame)
        month_row.pack(fill='x', pady=2)
        ttk.Label(month_row, text="Month:", width=15).pack(side='left')
        self.month_var = tk.StringVar(value=str(today.month))
        month_combo = ttk.Combobox(month_row, textvariable=self.month_var,
                                   width=15, state='readonly')
        month_combo['values'] = ('1 - January', '2 - February', '3 - March',
                                 '4 - April', '5 - May', '6 - June',
                                 '7 - July', '8 - August', '9 - September',
                                 '10 - October', '11 - November', '12 - December')
        month_combo.current(today.month - 1)
        month_combo.pack(side='left')

        # Bonus member configuration
        bonus_frame = ttk.LabelFrame(main_frame, text="Bonus Member (Optional)", padding=10)
        bonus_frame.pack(fill='x', pady=5)

        bonus_row = ttk.Frame(bonus_frame)
        bonus_row.pack(fill='x')
        ttk.Label(bonus_row, text="Callsign:", width=15).pack(side='left')
        self.bonus_member_var = tk.StringVar(value=self.config.get('monthly_brag.bonus_member', ''))
        ttk.Entry(bonus_row, textvariable=self.bonus_member_var, width=15).pack(side='left', padx=5)
        ttk.Label(bonus_row, text="(+25 points if worked)").pack(side='left')

        # Generate button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=10)
        ttk.Button(btn_frame, text="Generate Report", command=self.generate_report,
                  width=20).pack()

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill='both', expand=True, pady=5)

        # Summary
        self.summary_text = tk.Text(results_frame, height=4, wrap=tk.WORD, state='disabled')
        self.summary_text.pack(fill='x', pady=(0, 5))

        # SKCC numbers list
        list_label = ttk.Label(results_frame, text="SKCC Members Worked:")
        list_label.pack(anchor='w')

        # Scrollable list
        list_container = ttk.Frame(results_frame)
        list_container.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')

        self.members_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set,
                                         font=('', 10))
        self.members_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.members_listbox.yview)

        # Export button
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(fill='x', pady=5)
        self.export_btn = ttk.Button(export_frame, text="Export for SKCC Submission",
                                     command=self.export_report, state='disabled')
        self.export_btn.pack()

        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=5)

        # Store results for export
        self.report_data = None

    def generate_report(self):
        """Generate the Monthly Brag report"""
        try:
            # Get selected month/year
            month_str = self.month_var.get().split(' - ')[0]
            month = int(month_str)
            year = int(self.year_var.get())

            # Get bonus member
            bonus_member = self.bonus_member_var.get().strip().upper()
            if bonus_member:
                self.config.set('monthly_brag.bonus_member', bonus_member)

            # Calculate date range
            start_date = f"{year}-{month:02d}-01"
            last_day = monthrange(year, month)[1]
            end_date = f"{year}-{month:02d}-{last_day}"

            # Query database for SKCC contacts in this month
            cursor = self.database.conn.cursor()
            cursor.execute('''
                SELECT callsign, skcc_number, date, band, comment
                FROM contacts
                WHERE date >= ? AND date <= ?
                AND skcc_number IS NOT NULL AND skcc_number != ''
                ORDER BY date, time_on
            ''', (start_date, end_date))

            contacts = cursor.fetchall()

            # Filter out contest contacts
            skcc_members = {}  # {skcc_number: callsign}
            bonus_member_worked = False

            for callsign, skcc_num, contact_date, band, comment in contacts:
                # Skip contest contacts
                if comment and any(contest in comment.upper() for contest in
                                 ['WES CONTEST', 'SKS CONTEST', 'K3Y CONTEST']):
                    continue

                # Count unique SKCC numbers (not per band!)
                if skcc_num not in skcc_members:
                    skcc_members[skcc_num] = callsign

                # Check for bonus member
                if bonus_member and callsign.upper() == bonus_member:
                    bonus_member_worked = True

            # Calculate total score
            unique_count = len(skcc_members)
            bonus_points = 25 if bonus_member_worked else 0
            total_score = unique_count + bonus_points

            # Update summary
            month_name = datetime(year, month, 1).strftime('%B %Y')
            self.summary_text.config(state='normal')
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.insert('1.0', f"Month: {month_name}\n")
            self.summary_text.insert(tk.END, f"Unique SKCC Members: {unique_count}\n")
            if bonus_member:
                status = "✓ Worked" if bonus_member_worked else "✗ Not worked"
                self.summary_text.insert(tk.END, f"Bonus Member ({bonus_member}): {status} (+{bonus_points} pts)\n")
            self.summary_text.insert(tk.END, f"Total Score: {total_score}")
            self.summary_text.config(state='disabled')

            # Update list
            self.members_listbox.delete(0, tk.END)
            for skcc_num in sorted(skcc_members.keys()):
                callsign = skcc_members[skcc_num]
                self.members_listbox.insert(tk.END, f"{skcc_num} ({callsign})")

            # Store data for export
            self.report_data = {
                'month_name': month_name,
                'year': year,
                'month': month,
                'unique_count': unique_count,
                'bonus_member': bonus_member,
                'bonus_worked': bonus_member_worked,
                'bonus_points': bonus_points,
                'total_score': total_score,
                'members': skcc_members
            }

            # Enable export button
            self.export_btn.config(state='normal')

            if unique_count == 0:
                messagebox.showinfo("No Results",
                                   f"No SKCC contacts found for {month_name}\n(excluding WES/SKS/K3Y contests)")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating report:\n{str(e)}")

    def export_report(self):
        """Export the Monthly Brag report for SKCC submission"""
        if not self.report_data:
            messagebox.showwarning("No Data", "Please generate a report first")
            return

        # Get save filename
        my_call = self.config.get('callsign', 'N0CALL')
        month_abbr = datetime(self.report_data['year'], self.report_data['month'], 1).strftime('%b')
        default_filename = f"{my_call}_Brag_{month_abbr}{self.report_data['year']}.txt"

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Monthly Brag Report"
        )

        if not filename:
            return

        try:
            with open(filename, 'w') as f:
                # Header
                f.write(f"SKCC Monthly Brag Report\n")
                f.write(f"{'=' * 50}\n\n")

                # Station info
                f.write(f"Callsign: {my_call}\n")
                skcc_num = self.config.get('skcc_number', '')
                if skcc_num:
                    f.write(f"SKCC #: {skcc_num}\n")
                f.write(f"\nMonth: {self.report_data['month_name']}\n")
                f.write(f"\n{'=' * 50}\n\n")

                # Summary
                f.write(f"SUMMARY\n")
                f.write(f"Unique SKCC Members Worked: {self.report_data['unique_count']}\n")

                if self.report_data['bonus_member']:
                    status = "YES" if self.report_data['bonus_worked'] else "NO"
                    f.write(f"Bonus Member ({self.report_data['bonus_member']}): {status} (+{self.report_data['bonus_points']} points)\n")

                f.write(f"\nTOTAL SCORE: {self.report_data['total_score']}\n")
                f.write(f"\n{'=' * 50}\n\n")

                # Members list
                f.write(f"SKCC MEMBERS WORKED\n")
                f.write(f"{'SKCC #':<15} {'Callsign':<15}\n")
                f.write(f"{'-' * 30}\n")

                for skcc_num in sorted(self.report_data['members'].keys()):
                    callsign = self.report_data['members'][skcc_num]
                    f.write(f"{skcc_num:<15} {callsign:<15}\n")

                f.write(f"\n{'=' * 50}\n")
                f.write(f"\nNOTE: Contest contacts (WES, SKS, K3Y) are excluded per Monthly Brag rules.\n")

            messagebox.showinfo("Export Complete",
                              f"Exported Monthly Brag report to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting report:\n{str(e)}")
