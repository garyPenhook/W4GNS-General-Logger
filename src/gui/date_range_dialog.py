"""
Date/Time Range Selection Dialog for ADIF Export
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class DateRangeDialog:
    """Dialog for selecting date/time range for export"""

    def __init__(self, parent):
        self.parent = parent
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export by Date/Time Range")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.center_window()

        # Create UI
        self.create_ui()

    def center_window(self):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.dialog.geometry(f'+{x}+{y}')

    def create_ui(self):
        """Create the dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Select Date/Time Range for Export",
            font=('', 12, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Export contacts within the specified date and time range.\nUseful for events like SKCC WES weekends.",
            justify='center'
        )
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))

        # Start Date/Time Section
        start_label = ttk.Label(main_frame, text="Start Date/Time:", font=('', 10, 'bold'))
        start_label.grid(row=2, column=0, columnspan=3, sticky='w', pady=(10, 5))

        # Start Date
        ttk.Label(main_frame, text="Date:").grid(row=3, column=0, sticky='w', padx=(0, 5))
        self.start_date_entry = ttk.Entry(main_frame, width=15)
        self.start_date_entry.grid(row=3, column=1, sticky='w', padx=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=('', 8)).grid(row=3, column=2, sticky='w')

        # Start Time
        ttk.Label(main_frame, text="Time:").grid(row=4, column=0, sticky='w', padx=(0, 5))
        self.start_time_entry = ttk.Entry(main_frame, width=15)
        self.start_time_entry.grid(row=4, column=1, sticky='w', padx=5)
        ttk.Label(main_frame, text="(HH:MM, optional)", font=('', 8)).grid(row=4, column=2, sticky='w')

        # End Date/Time Section
        end_label = ttk.Label(main_frame, text="End Date/Time:", font=('', 10, 'bold'))
        end_label.grid(row=5, column=0, columnspan=3, sticky='w', pady=(15, 5))

        # End Date
        ttk.Label(main_frame, text="Date:").grid(row=6, column=0, sticky='w', padx=(0, 5))
        self.end_date_entry = ttk.Entry(main_frame, width=15)
        self.end_date_entry.grid(row=6, column=1, sticky='w', padx=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=('', 8)).grid(row=6, column=2, sticky='w')

        # End Time
        ttk.Label(main_frame, text="Time:").grid(row=7, column=0, sticky='w', padx=(0, 5))
        self.end_time_entry = ttk.Entry(main_frame, width=15)
        self.end_time_entry.grid(row=7, column=1, sticky='w', padx=5)
        ttk.Label(main_frame, text="(HH:MM, optional)", font=('', 8)).grid(row=7, column=2, sticky='w')

        # Quick preset buttons
        preset_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding=10)
        preset_frame.grid(row=8, column=0, columnspan=3, pady=15, sticky='ew')

        ttk.Button(preset_frame, text="Today", command=self.set_today).pack(side='left', padx=5)
        ttk.Button(preset_frame, text="Yesterday", command=self.set_yesterday).pack(side='left', padx=5)
        ttk.Button(preset_frame, text="This Week", command=self.set_this_week).pack(side='left', padx=5)
        ttk.Button(preset_frame, text="This Month", command=self.set_this_month).pack(side='left', padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=(10, 0))

        ttk.Button(button_frame, text="Export", command=self.on_export, width=12).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=12).pack(side='left', padx=5)

        # Set default to today
        self.set_today()

    def set_today(self):
        """Set range to today"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, today)
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, today)
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, "00:00")
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "23:59")

    def set_yesterday(self):
        """Set range to yesterday"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, yesterday)
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, yesterday)
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, "00:00")
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "23:59")

    def set_this_week(self):
        """Set range to this week (Monday to Sunday)"""
        today = datetime.now()
        # Get Monday of this week
        monday = today - timedelta(days=today.weekday())
        # Get Sunday of this week
        sunday = monday + timedelta(days=6)

        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, monday.strftime('%Y-%m-%d'))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, sunday.strftime('%Y-%m-%d'))
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, "00:00")
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "23:59")

    def set_this_month(self):
        """Set range to this month"""
        today = datetime.now()
        # First day of month
        first_day = today.replace(day=1)
        # Last day of month
        if today.month == 12:
            last_day = today.replace(day=31)
        else:
            last_day = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))

        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, first_day.strftime('%Y-%m-%d'))
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, last_day.strftime('%Y-%m-%d'))
        self.start_time_entry.delete(0, tk.END)
        self.start_time_entry.insert(0, "00:00")
        self.end_time_entry.delete(0, tk.END)
        self.end_time_entry.insert(0, "23:59")

    def validate_input(self):
        """Validate the input dates and times"""
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()

        # Validate start date
        if not start_date:
            messagebox.showerror("Invalid Input", "Start date is required.")
            return False

        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Input", "Start date must be in YYYY-MM-DD format.")
            return False

        # Validate end date
        if not end_date:
            messagebox.showerror("Invalid Input", "End date is required.")
            return False

        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Input", "End date must be in YYYY-MM-DD format.")
            return False

        # Validate start time (optional)
        if start_time:
            try:
                datetime.strptime(start_time, '%H:%M')
            except ValueError:
                messagebox.showerror("Invalid Input", "Start time must be in HH:MM format.")
                return False

        # Validate end time (optional)
        if end_time:
            try:
                datetime.strptime(end_time, '%H:%M')
            except ValueError:
                messagebox.showerror("Invalid Input", "End time must be in HH:MM format.")
                return False

        # Check that start is before end
        start_datetime_str = f"{start_date} {start_time if start_time else '00:00'}"
        end_datetime_str = f"{end_date} {end_time if end_time else '23:59'}"

        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M')

        if start_datetime > end_datetime:
            messagebox.showerror("Invalid Input", "Start date/time must be before end date/time.")
            return False

        return True

    def on_export(self):
        """Handle export button click"""
        if self.validate_input():
            self.result = {
                'start_date': self.start_date_entry.get().strip(),
                'end_date': self.end_date_entry.get().strip(),
                'start_time': self.start_time_entry.get().strip() or None,
                'end_time': self.end_time_entry.get().strip() or None
            }
            self.dialog.destroy()

    def on_cancel(self):
        """Handle cancel button click"""
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Show the dialog and return the result"""
        self.dialog.wait_window()
        return self.result
