"""
SKCC Awards Tab - Display Straight Key Century Club award progress
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from src.skcc_awards import (
    CenturionAward, TribuneAward, SenatorAward,
    TripleKeyAward, RagChewAward, CanadianMapleAward,
    SKCCDXQAward, SKCCDXCAward, PFXAward,
    SKCCWASAward, SKCCWACAward
)


class SKCCAwardsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)

        # Initialize award instances
        self.awards = {
            'centurion': CenturionAward(database),
            'tribune': TribuneAward(database),
            'senator': SenatorAward(database),
            'triple_key': TripleKeyAward(database),
            'rag_chew': RagChewAward(database),
            'canadian_maple': CanadianMapleAward(database),
            'dxq': SKCCDXQAward(database),
            'dxc': SKCCDXCAward(database),
            'pfx': PFXAward(database),
            'was': SKCCWASAward(database),
            'wac': SKCCWACAward(database)
        }

        self.create_widgets()
        self.refresh_awards()

    def create_widgets(self):
        """Create the SKCC awards interface"""

        # Header with refresh button
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(header_frame, text="SKCC Awards Progress",
                 font=('', 14, 'bold')).pack(side='left')
        ttk.Label(header_frame, text="(Straight Key Century Club)",
                 font=('', 10), foreground='gray').pack(side='left', padx=10)

        ttk.Button(header_frame, text="Refresh Awards",
                  command=self.refresh_awards).pack(side='right', padx=5)

        # Create notebook for different awards
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs for each award category
        self.core_frame = ttk.Frame(self.notebook)
        self.specialty_frame = ttk.Frame(self.notebook)
        self.geography_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.core_frame, text="  Core Awards  ")
        self.notebook.add(self.specialty_frame, text="  Specialty Awards  ")
        self.notebook.add(self.geography_frame, text="  Geography Awards  ")

        # Initialize displays
        self.create_core_awards_display()
        self.create_specialty_awards_display()
        self.create_geography_awards_display()

    def create_core_awards_display(self):
        """Create display for core SKCC awards (Centurion, Tribune, Senator)"""
        # Centurion
        centurion_frame = ttk.LabelFrame(self.core_frame, text="Centurion Award", padding=10)
        centurion_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(centurion_frame, text="Contact 100 different SKCC members",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.centurion_progress = ttk.Label(centurion_frame, text="", font=('', 11, 'bold'))
        self.centurion_progress.pack(anchor='w', pady=2)

        self.centurion_bar = ttk.Progressbar(centurion_frame, length=400, mode='determinate')
        self.centurion_bar.pack(fill='x', pady=2)

        self.centurion_endorsement = ttk.Label(centurion_frame, text="", foreground='blue')
        self.centurion_endorsement.pack(anchor='w')

        # Tribune
        tribune_frame = ttk.LabelFrame(self.core_frame, text="Tribune Award", padding=10)
        tribune_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(tribune_frame, text="Contact 50 Tribune/Senator members (requires Centurion)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.tribune_progress = ttk.Label(tribune_frame, text="", font=('', 11, 'bold'))
        self.tribune_progress.pack(anchor='w', pady=2)

        self.tribune_bar = ttk.Progressbar(tribune_frame, length=400, mode='determinate')
        self.tribune_bar.pack(fill='x', pady=2)

        self.tribune_endorsement = ttk.Label(tribune_frame, text="", foreground='blue')
        self.tribune_endorsement.pack(anchor='w')

        # Senator
        senator_frame = ttk.LabelFrame(self.core_frame, text="Senator Award", padding=10)
        senator_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(senator_frame, text="Contact 200 Tribune/Senator members AFTER achieving Tribune x8",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.senator_progress = ttk.Label(senator_frame, text="", font=('', 11, 'bold'))
        self.senator_progress.pack(anchor='w', pady=2)

        self.senator_bar = ttk.Progressbar(senator_frame, length=400, mode='determinate')
        self.senator_bar.pack(fill='x', pady=2)

        self.senator_endorsement = ttk.Label(senator_frame, text="", foreground='blue')
        self.senator_endorsement.pack(anchor='w')

    def create_specialty_awards_display(self):
        """Create display for specialty awards (Triple Key, Rag Chew, PFX, Canadian Maple)"""
        # Triple Key
        triple_key_frame = ttk.LabelFrame(self.specialty_frame, text="Triple Key Award", padding=10)
        triple_key_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(triple_key_frame, text="Contact 100 members with EACH key type (Straight, Bug, Sideswiper)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.triple_key_progress = ttk.Label(triple_key_frame, text="", font=('', 11, 'bold'))
        self.triple_key_progress.pack(anchor='w', pady=2)

        self.triple_key_details = ttk.Label(triple_key_frame, text="", font=('', 9))
        self.triple_key_details.pack(anchor='w')

        # Rag Chew
        rag_chew_frame = ttk.LabelFrame(self.specialty_frame, text="Rag Chew Award", padding=10)
        rag_chew_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(rag_chew_frame, text="Accumulate 300+ minutes of extended CW conversations",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.rag_chew_progress = ttk.Label(rag_chew_frame, text="", font=('', 11, 'bold'))
        self.rag_chew_progress.pack(anchor='w', pady=2)

        self.rag_chew_bar = ttk.Progressbar(rag_chew_frame, length=400, mode='determinate')
        self.rag_chew_bar.pack(fill='x', pady=2)

        # PFX
        pfx_frame = ttk.LabelFrame(self.specialty_frame, text="PFX Award", padding=10)
        pfx_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(pfx_frame, text="Accumulate 500,000+ points from callsign prefixes",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.pfx_progress = ttk.Label(pfx_frame, text="", font=('', 11, 'bold'))
        self.pfx_progress.pack(anchor='w', pady=2)

        self.pfx_bar = ttk.Progressbar(pfx_frame, length=400, mode='determinate')
        self.pfx_bar.pack(fill='x', pady=2)

        # Canadian Maple
        maple_frame = ttk.LabelFrame(self.specialty_frame, text="Canadian Maple Award", padding=10)
        maple_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(maple_frame, text="4 levels: Yellow (10 prov/terr), Orange (10 on one band), Red (90 contacts), Gold (90 QRP)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.maple_progress = ttk.Label(maple_frame, text="", font=('', 11, 'bold'))
        self.maple_progress.pack(anchor='w', pady=2)

    def create_geography_awards_display(self):
        """Create display for geography awards (DXQ, DXC, WAS, WAC)"""
        # SKCC WAS
        was_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAS (Worked All States)", padding=10)
        was_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(was_frame, text="Contact SKCC members in all 50 US states",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.was_progress = ttk.Label(was_frame, text="", font=('', 11, 'bold'))
        self.was_progress.pack(anchor='w', pady=2)

        self.was_bar = ttk.Progressbar(was_frame, length=400, mode='determinate')
        self.was_bar.pack(fill='x', pady=2)

        # SKCC WAC
        wac_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAC (Worked All Continents)", padding=10)
        wac_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(wac_frame, text="Contact SKCC members in all 6 continents",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.wac_progress = ttk.Label(wac_frame, text="", font=('', 11, 'bold'))
        self.wac_progress.pack(anchor='w', pady=2)

        self.wac_bar = ttk.Progressbar(wac_frame, length=400, mode='determinate')
        self.wac_bar.pack(fill='x', pady=2)

        # DXQ
        dxq_frame = ttk.LabelFrame(self.geography_frame, text="SKCC DXQ (QSO-based DX)", padding=10)
        dxq_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(dxq_frame, text="Contact SKCC members in 10+ DXCC entities (each contact counts)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.dxq_progress = ttk.Label(dxq_frame, text="", font=('', 11, 'bold'))
        self.dxq_progress.pack(anchor='w', pady=2)

        # DXC
        dxc_frame = ttk.LabelFrame(self.geography_frame, text="SKCC DXC (Country-based DX)", padding=10)
        dxc_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(dxc_frame, text="Contact SKCC members in 10+ DXCC entities (each country counts once)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.dxc_progress = ttk.Label(dxc_frame, text="", font=('', 11, 'bold'))
        self.dxc_progress.pack(anchor='w', pady=2)

    def refresh_awards(self):
        """Refresh all award progress displays"""
        # Get all contacts for calculations
        contacts = self.database.get_all_contacts(limit=999999)
        contacts_list = [dict(c) for c in contacts]

        # Centurion
        centurion_progress = self.awards['centurion'].calculate_progress(contacts_list)
        self.update_centurion_display(centurion_progress)

        # Tribune
        tribune_progress = self.awards['tribune'].calculate_progress(contacts_list)
        self.update_tribune_display(tribune_progress)

        # Senator
        senator_progress = self.awards['senator'].calculate_progress(contacts_list)
        self.update_senator_display(senator_progress)

        # Triple Key
        triple_key_progress = self.awards['triple_key'].calculate_progress(contacts_list)
        self.update_triple_key_display(triple_key_progress)

        # Rag Chew
        rag_chew_progress = self.awards['rag_chew'].calculate_progress(contacts_list)
        self.update_rag_chew_display(rag_chew_progress)

        # PFX
        pfx_progress = self.awards['pfx'].calculate_progress(contacts_list)
        self.update_pfx_display(pfx_progress)

        # Canadian Maple
        maple_progress = self.awards['canadian_maple'].calculate_progress(contacts_list)
        self.update_maple_display(maple_progress)

        # WAS
        was_progress = self.awards['was'].calculate_progress(contacts_list)
        self.update_was_display(was_progress)

        # WAC
        wac_progress = self.awards['wac'].calculate_progress(contacts_list)
        self.update_wac_display(wac_progress)

        # DXQ
        dxq_progress = self.awards['dxq'].calculate_progress(contacts_list)
        self.update_dxq_display(dxq_progress)

        # DXC
        dxc_progress = self.awards['dxc'].calculate_progress(contacts_list)
        self.update_dxc_display(dxc_progress)

    def update_centurion_display(self, progress):
        """Update Centurion award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']

        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"
        self.centurion_progress.config(
            text=f"{status} - {current} of {required} members ({pct:.1f}%)",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.centurion_bar['value'] = pct
        self.centurion_endorsement.config(text=f"Current Level: {endorsement}")

    def update_tribune_display(self, progress):
        """Update Tribune award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']

        prereq_status = "✅" if progress.get('prerequisite_met') else "❌"
        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"

        self.tribune_progress.config(
            text=f"{prereq_status} Centurion | {status} - {current} of {required} Tribune/Senator members ({pct:.1f}%)",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.tribune_bar['value'] = pct
        self.tribune_endorsement.config(text=f"Current Level: {endorsement}")

    def update_senator_display(self, progress):
        """Update Senator award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']

        prereq_status = "✅" if progress.get('prerequisite_met') else "❌"
        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"

        self.senator_progress.config(
            text=f"{prereq_status} Tribune x8 | {status} - {current} of {required} post-x8 contacts ({pct:.1f}%)",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.senator_bar['value'] = pct
        self.senator_endorsement.config(text=f"Current Level: {endorsement}")

    def update_triple_key_display(self, progress):
        """Update Triple Key award display"""
        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"

        by_key = progress['by_key_type']
        straight = by_key['STRAIGHT']['count']
        bug = by_key['BUG']['count']
        sideswiper = by_key['SIDESWIPER']['count']

        self.triple_key_progress.config(
            text=f"{status} - Minimum: {progress['current']} of 100",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.triple_key_details.config(
            text=f"Straight: {straight}/100 | Bug: {bug}/100 | Sideswiper: {sideswiper}/100 | Level: {progress['endorsement']}"
        )

    def update_rag_chew_display(self, progress):
        """Update Rag Chew award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.rag_chew_progress.config(
            text=f"{status} - {current} of {required} minutes ({pct:.1f}%) - Level: {endorsement}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.rag_chew_bar['value'] = pct

    def update_pfx_display(self, progress):
        """Update PFX award display"""
        current = progress['current_points']
        required = progress['required_points']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.pfx_progress.config(
            text=f"{status} - {current:,} of {required:,} points ({pct:.1f}%) - Level: {endorsement}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.pfx_bar['value'] = pct

    def update_maple_display(self, progress):
        """Update Canadian Maple award display"""
        highest = progress['highest_achieved']
        yellow = progress['yellow_maple']
        orange = progress['orange_maple']
        red = progress['red_maple']
        gold = progress['gold_maple']

        levels_text = f"Yellow: {yellow['locations_count']}/10 | Orange: {orange['locations_count']}/10 | Red: {red['total_contacts']}/90 | Gold: {gold['total_contacts']}/90"

        self.maple_progress.config(
            text=f"Highest Achieved: {highest} | {levels_text}",
            foreground='green' if highest != "Not Yet" else 'black'
        )

    def update_was_display(self, progress):
        """Update WAS award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        level = progress['level']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.was_progress.config(
            text=f"{status} - {current} of {required} states ({pct:.1f}%) - {level}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.was_bar['value'] = pct

    def update_wac_display(self, progress):
        """Update WAC award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        level = progress['level']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.wac_progress.config(
            text=f"{status} - {current} of {required} continents ({pct:.1f}%) - {level}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.wac_bar['value'] = pct

    def update_dxq_display(self, progress):
        """Update DXQ award display"""
        entities = progress['entities_worked']
        qsos = progress['total_qsos']
        level = progress['achieved_level']

        self.dxq_progress.config(
            text=f"{entities} entities worked, {qsos} total QSOs - Level: {level}",
            foreground='green' if level != "Not Yet" else 'black'
        )

    def update_dxc_display(self, progress):
        """Update DXC award display"""
        entities = progress['current']
        level = progress['achieved_level']

        self.dxc_progress.config(
            text=f"{entities} entities worked (each counts once) - Level: {level}",
            foreground='green' if level != "Not Yet" else 'black'
        )

    def get_frame(self):
        """Return the main frame"""
        return self.frame
