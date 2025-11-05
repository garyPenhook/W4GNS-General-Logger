"""
ARRL Awards Tab - Display award progress and tracking
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from src.awards_calculator import AwardsCalculator


class AwardsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)
        self.calculator = AwardsCalculator(database)
        self.awards_data = None

        self.create_widgets()
        self.refresh_awards()

    def create_widgets(self):
        """Create the awards interface"""

        # Header with refresh button
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(header_frame, text="ARRL Awards Progress",
                 font=('', 14, 'bold')).pack(side='left')

        ttk.Button(header_frame, text="Refresh Awards",
                  command=self.refresh_awards).pack(side='right', padx=5)

        # Create notebook for different awards
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs for each award
        self.dxcc_frame = ttk.Frame(self.notebook)
        self.was_frame = ttk.Frame(self.notebook)
        self.wac_frame = ttk.Frame(self.notebook)
        self.wpx_frame = ttk.Frame(self.notebook)
        self.vucc_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.dxcc_frame, text="  DXCC  ")
        self.notebook.add(self.was_frame, text="  WAS  ")
        self.notebook.add(self.wac_frame, text="  WAC  ")
        self.notebook.add(self.wpx_frame, text="  WPX  ")
        self.notebook.add(self.vucc_frame, text="  VUCC  ")

        # Initialize award displays
        self.create_dxcc_display()
        self.create_was_display()
        self.create_wac_display()
        self.create_wpx_display()
        self.create_vucc_display()

    def create_dxcc_display(self):
        """Create DXCC (DX Century Club) display"""
        # Info section
        info_frame = ttk.LabelFrame(self.dxcc_frame, text="Award Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("DXCC (DX Century Club)\n\n"
                    "Work and confirm 100 different countries/entities.\n"
                    "This is the most prestigious award in Amateur Radio!")
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Progress section
        progress_frame = ttk.LabelFrame(self.dxcc_frame, text="Overall Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.dxcc_progress_label = ttk.Label(progress_frame, text="", font=('', 12, 'bold'))
        self.dxcc_progress_label.pack(anchor='w')

        self.dxcc_progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.dxcc_progress_bar.pack(fill='x', pady=5)

        # Band/Mode breakdown
        breakdown_frame = ttk.LabelFrame(self.dxcc_frame, text="By Band and Mode", padding=10)
        breakdown_frame.pack(fill='x', padx=10, pady=5)

        self.dxcc_breakdown_text = scrolledtext.ScrolledText(breakdown_frame, height=5, wrap='word')
        self.dxcc_breakdown_text.pack(fill='both', expand=True)

        # Countries list
        list_frame = ttk.LabelFrame(self.dxcc_frame, text="Countries Worked", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.dxcc_list_text = scrolledtext.ScrolledText(list_frame, height=10, wrap='word')
        self.dxcc_list_text.pack(fill='both', expand=True)

    def create_was_display(self):
        """Create WAS (Worked All States) display"""
        # Info section
        info_frame = ttk.LabelFrame(self.was_frame, text="Award Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("WAS (Worked All States)\n\n"
                    "Work and confirm all 50 U.S. states.\n"
                    "Endorsements available for different bands and modes.")
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Progress section
        progress_frame = ttk.LabelFrame(self.was_frame, text="Overall Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.was_progress_label = ttk.Label(progress_frame, text="", font=('', 12, 'bold'))
        self.was_progress_label.pack(anchor='w')

        self.was_progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.was_progress_bar.pack(fill='x', pady=5)

        # Band/Mode breakdown
        breakdown_frame = ttk.LabelFrame(self.was_frame, text="By Band and Mode", padding=10)
        breakdown_frame.pack(fill='x', padx=10, pady=5)

        self.was_breakdown_text = scrolledtext.ScrolledText(breakdown_frame, height=5, wrap='word')
        self.was_breakdown_text.pack(fill='both', expand=True)

        # States lists
        paned = ttk.PanedWindow(self.was_frame, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=5)

        # Worked states
        worked_frame = ttk.LabelFrame(paned, text="States Worked", padding=10)
        paned.add(worked_frame, weight=1)

        self.was_worked_text = scrolledtext.ScrolledText(worked_frame, height=10, wrap='word')
        self.was_worked_text.pack(fill='both', expand=True)

        # Needed states
        needed_frame = ttk.LabelFrame(paned, text="States Needed", padding=10)
        paned.add(needed_frame, weight=1)

        self.was_needed_text = scrolledtext.ScrolledText(needed_frame, height=10, wrap='word')
        self.was_needed_text.pack(fill='both', expand=True)

    def create_wac_display(self):
        """Create WAC (Worked All Continents) display"""
        # Info section
        info_frame = ttk.LabelFrame(self.wac_frame, text="Award Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("WAC (Worked All Continents)\n\n"
                    "Work and confirm all 6 continents:\n"
                    "North America, South America, Europe, Africa, Asia, Oceania")
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Progress section
        progress_frame = ttk.LabelFrame(self.wac_frame, text="Overall Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.wac_progress_label = ttk.Label(progress_frame, text="", font=('', 12, 'bold'))
        self.wac_progress_label.pack(anchor='w')

        self.wac_progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.wac_progress_bar.pack(fill='x', pady=5)

        # Band/Mode breakdown
        breakdown_frame = ttk.LabelFrame(self.wac_frame, text="By Band and Mode", padding=10)
        breakdown_frame.pack(fill='x', padx=10, pady=5)

        self.wac_breakdown_text = scrolledtext.ScrolledText(breakdown_frame, height=5, wrap='word')
        self.wac_breakdown_text.pack(fill='both', expand=True)

        # Continents display
        display_frame = ttk.LabelFrame(self.wac_frame, text="Continents Status", padding=10)
        display_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.wac_display_text = scrolledtext.ScrolledText(display_frame, height=10, wrap='word')
        self.wac_display_text.pack(fill='both', expand=True)

    def create_wpx_display(self):
        """Create WPX (Worked All Prefixes) display"""
        # Info section
        info_frame = ttk.LabelFrame(self.wpx_frame, text="Award Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("WPX (Worked All Prefixes)\n\n"
                    "Work different call sign prefixes.\n"
                    "Track your prefix diversity across bands and modes.")
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Progress section
        progress_frame = ttk.LabelFrame(self.wpx_frame, text="Overall Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.wpx_progress_label = ttk.Label(progress_frame, text="", font=('', 12, 'bold'))
        self.wpx_progress_label.pack(anchor='w')

        # Band/Mode breakdown
        breakdown_frame = ttk.LabelFrame(self.wpx_frame, text="By Band and Mode", padding=10)
        breakdown_frame.pack(fill='x', padx=10, pady=5)

        self.wpx_breakdown_text = scrolledtext.ScrolledText(breakdown_frame, height=5, wrap='word')
        self.wpx_breakdown_text.pack(fill='both', expand=True)

        # Prefixes list
        list_frame = ttk.LabelFrame(self.wpx_frame, text="Prefixes Worked", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.wpx_list_text = scrolledtext.ScrolledText(list_frame, height=10, wrap='word')
        self.wpx_list_text.pack(fill='both', expand=True)

    def create_vucc_display(self):
        """Create VUCC (VHF/UHF Century Club) display"""
        # Info section
        info_frame = ttk.LabelFrame(self.vucc_frame, text="Award Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)

        info_text = ("VUCC (VHF/UHF Century Club)\n\n"
                    "Work 100 different Maidenhead grid squares on VHF/UHF bands.\n"
                    "Bands: 6m, 2m, 70cm, and higher.")
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')

        # Progress section
        progress_frame = ttk.LabelFrame(self.vucc_frame, text="Overall Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)

        self.vucc_progress_label = ttk.Label(progress_frame, text="", font=('', 12, 'bold'))
        self.vucc_progress_label.pack(anchor='w')

        self.vucc_progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.vucc_progress_bar.pack(fill='x', pady=5)

        # Band breakdown
        breakdown_frame = ttk.LabelFrame(self.vucc_frame, text="By Band", padding=10)
        breakdown_frame.pack(fill='x', padx=10, pady=5)

        self.vucc_breakdown_text = scrolledtext.ScrolledText(breakdown_frame, height=5, wrap='word')
        self.vucc_breakdown_text.pack(fill='both', expand=True)

        # Grids list
        list_frame = ttk.LabelFrame(self.vucc_frame, text="Grid Squares Worked", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.vucc_list_text = scrolledtext.ScrolledText(list_frame, height=10, wrap='word')
        self.vucc_list_text.pack(fill='both', expand=True)

    def refresh_awards(self):
        """Refresh all award calculations and displays"""
        self.awards_data = self.calculator.calculate_all_awards()

        self.update_dxcc_display()
        self.update_was_display()
        self.update_wac_display()
        self.update_wpx_display()
        self.update_vucc_display()

    def update_dxcc_display(self):
        """Update DXCC display with current data"""
        if not self.awards_data:
            return

        dxcc = self.awards_data['dxcc']

        # Progress
        self.dxcc_progress_label.config(
            text=f"{dxcc['total']} / {dxcc['goal']} countries ({dxcc['percent']:.1f}%)")
        self.dxcc_progress_bar['value'] = dxcc['percent']

        # Breakdown
        self.dxcc_breakdown_text.delete('1.0', 'end')
        self.dxcc_breakdown_text.insert('end', "By Band:\n")
        for band, count in sorted(dxcc['by_band'].items()):
            self.dxcc_breakdown_text.insert('end', f"  {band}: {count}\n")
        self.dxcc_breakdown_text.insert('end', "\nBy Mode:\n")
        for mode, count in sorted(dxcc['by_mode'].items()):
            self.dxcc_breakdown_text.insert('end', f"  {mode}: {count}\n")

        # Countries list
        self.dxcc_list_text.delete('1.0', 'end')
        for country in dxcc['countries']:
            self.dxcc_list_text.insert('end', f"{country}\n")

    def update_was_display(self):
        """Update WAS display with current data"""
        if not self.awards_data:
            return

        was = self.awards_data['was']

        # Progress
        self.was_progress_label.config(
            text=f"{was['total']} / {was['goal']} states ({was['percent']:.1f}%)")
        self.was_progress_bar['value'] = was['percent']

        # Breakdown
        self.was_breakdown_text.delete('1.0', 'end')
        self.was_breakdown_text.insert('end', "By Band:\n")
        for band, count in sorted(was['by_band'].items()):
            self.was_breakdown_text.insert('end', f"  {band}: {count}\n")
        self.was_breakdown_text.insert('end', "\nBy Mode:\n")
        for mode, count in sorted(was['by_mode'].items()):
            self.was_breakdown_text.insert('end', f"  {mode}: {count}\n")

        # Worked states
        self.was_worked_text.delete('1.0', 'end')
        for state in was['states']:
            self.was_worked_text.insert('end', f"{state}\n")

        # Needed states
        self.was_needed_text.delete('1.0', 'end')
        if was['missing']:
            for state in was['missing']:
                self.was_needed_text.insert('end', f"{state}\n")
        else:
            self.was_needed_text.insert('end', "Congratulations! All 50 states worked!\n")

    def update_wac_display(self):
        """Update WAC display with current data"""
        if not self.awards_data:
            return

        wac = self.awards_data['wac']

        # Progress
        self.wac_progress_label.config(
            text=f"{wac['total']} / {wac['goal']} continents ({wac['percent']:.1f}%)")
        self.wac_progress_bar['value'] = wac['percent']

        # Breakdown
        self.wac_breakdown_text.delete('1.0', 'end')
        self.wac_breakdown_text.insert('end', "By Band:\n")
        for band, count in sorted(wac['by_band'].items()):
            self.wac_breakdown_text.insert('end', f"  {band}: {count}/6\n")
        self.wac_breakdown_text.insert('end', "\nBy Mode:\n")
        for mode, count in sorted(wac['by_mode'].items()):
            self.wac_breakdown_text.insert('end', f"  {mode}: {count}/6\n")

        # Continents display
        self.wac_display_text.delete('1.0', 'end')
        continent_names = {
            'NA': 'North America',
            'SA': 'South America',
            'EU': 'Europe',
            'AF': 'Africa',
            'AS': 'Asia',
            'OC': 'Oceania'
        }

        self.wac_display_text.insert('end', "Worked:\n")
        for cont in wac['continents']:
            name = continent_names.get(cont, cont)
            self.wac_display_text.insert('end', f"  ✓ {name}\n")

        if wac['missing']:
            self.wac_display_text.insert('end', "\nNeeded:\n")
            for cont_name in wac['missing']:
                self.wac_display_text.insert('end', f"  ✗ {cont_name}\n")
        else:
            self.wac_display_text.insert('end', "\nCongratulations! All 6 continents worked!\n")

    def update_wpx_display(self):
        """Update WPX display with current data"""
        if not self.awards_data:
            return

        wpx = self.awards_data['wpx']

        # Progress
        self.wpx_progress_label.config(
            text=f"Total Prefixes: {wpx['total']}")

        # Breakdown
        self.wpx_breakdown_text.delete('1.0', 'end')
        self.wpx_breakdown_text.insert('end', "By Band:\n")
        for band, count in sorted(wpx['by_band'].items()):
            self.wpx_breakdown_text.insert('end', f"  {band}: {count}\n")
        self.wpx_breakdown_text.insert('end', "\nBy Mode:\n")
        for mode, count in sorted(wpx['by_mode'].items()):
            self.wpx_breakdown_text.insert('end', f"  {mode}: {count}\n")

        # Prefixes list
        self.wpx_list_text.delete('1.0', 'end')
        # Display in columns
        prefixes = wpx['prefixes']
        for i, prefix in enumerate(prefixes):
            self.wpx_list_text.insert('end', f"{prefix:<10}")
            if (i + 1) % 6 == 0:
                self.wpx_list_text.insert('end', "\n")
        self.wpx_list_text.insert('end', "\n")

    def update_vucc_display(self):
        """Update VUCC display with current data"""
        if not self.awards_data:
            return

        vucc = self.awards_data['vucc']

        # Progress
        self.vucc_progress_label.config(
            text=f"{vucc['total']} / {vucc['goal']} grids ({vucc['percent']:.1f}%)")
        self.vucc_progress_bar['value'] = vucc['percent']

        # Breakdown
        self.vucc_breakdown_text.delete('1.0', 'end')
        self.vucc_breakdown_text.insert('end', "By Band:\n")
        for band, count in sorted(vucc['by_band'].items()):
            self.vucc_breakdown_text.insert('end', f"  {band}: {count}\n")

        # Grids list
        self.vucc_list_text.delete('1.0', 'end')
        # Display in columns
        grids = vucc['grids']
        for i, grid in enumerate(grids):
            self.vucc_list_text.insert('end', f"{grid:<8}")
            if (i + 1) % 8 == 0:
                self.vucc_list_text.insert('end', "\n")
        self.vucc_list_text.insert('end', "\n")

    def get_frame(self):
        """Return the frame widget"""
        return self.frame
