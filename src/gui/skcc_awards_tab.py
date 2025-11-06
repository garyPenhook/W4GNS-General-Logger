"""
SKCC Awards Tab - Display Straight Key Century Club award progress
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from src.skcc_awards import (
    CenturionAward, TribuneAward, SenatorAward,
    TripleKeyAward, RagChewAward, CanadianMapleAward,
    SKCCDXQAward, SKCCDXCAward, PFXAward,
    SKCCWASAward, SKCCWASTAward, SKCCWASSAward, SKCCWACAward,
    QRPMPWAward, MarathonAward
)
from src.skcc_roster import get_roster_manager


class SKCCAwardsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)

        # Initialize roster manager
        self.roster_manager = get_roster_manager()

        # Initialize award instances
        self.awards = {
            'centurion': CenturionAward(database),
            'tribune': TribuneAward(database),
            'senator': SenatorAward(database),
            'triple_key': TripleKeyAward(database),
            'rag_chew': RagChewAward(database),
            'marathon': MarathonAward(database),
            'qrp_mpw': QRPMPWAward(database),
            'canadian_maple': CanadianMapleAward(database),
            'dxq': SKCCDXQAward(database),
            'dxc': SKCCDXCAward(database),
            'pfx': PFXAward(database),
            'was': SKCCWASAward(database),
            'was_t': SKCCWASTAward(database),
            'was_s': SKCCWASSAward(database),
            'wac': SKCCWACAward(database)
        }

        self.create_widgets()
        self.update_roster_status()
        self.refresh_awards()

        # CRITICAL: Auto-download roster on EVERY startup for accurate award validation
        self.auto_download_roster_if_needed()

    def create_widgets(self):
        """Create the SKCC awards interface"""

        # Header with refresh button
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(header_frame, text="SKCC Awards Progress",
                 font=('', 14, 'bold')).pack(side='left')
        ttk.Label(header_frame, text="(Straight Key Century Club)",
                 font=('', 10), foreground='gray').pack(side='left', padx=10)

        ttk.Button(header_frame, text="🔍 Run Diagnostic",
                  command=self.run_diagnostic).pack(side='right', padx=2)
        ttk.Button(header_frame, text="Refresh Awards",
                  command=self.refresh_awards).pack(side='right', padx=5)

        # SKCC Roster section
        roster_frame = ttk.LabelFrame(self.frame, text="SKCC Membership Roster", padding=10)
        roster_frame.pack(fill='x', padx=10, pady=5)

        roster_info_frame = ttk.Frame(roster_frame)
        roster_info_frame.pack(fill='x')

        ttk.Label(roster_info_frame, text="Roster Status:", font=('', 10, 'bold')).pack(side='left')
        self.roster_status_label = ttk.Label(roster_info_frame, text="Loading...", font=('', 10))
        self.roster_status_label.pack(side='left', padx=10)

        ttk.Button(roster_info_frame, text="Download Roster",
                  command=self.download_roster_manual).pack(side='right', padx=5)

        ttk.Label(roster_frame,
                 text="The membership roster is used to identify SKCC members and their numbers for award tracking.",
                 font=('', 9, 'italic'), foreground='gray').pack(anchor='w', pady=(5, 0))

        # User's SKCC Join Date section
        user_info_frame = ttk.LabelFrame(self.frame, text="Your SKCC Information", padding=10)
        user_info_frame.pack(fill='x', padx=10, pady=5)

        # SKCC Join Date
        join_date_row = ttk.Frame(user_info_frame)
        join_date_row.pack(fill='x', pady=2)

        ttk.Label(join_date_row, text="SKCC Join Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(join_date_row, text="(YYYYMMDD)", font=('', 9), foreground='gray').pack(side='left', padx=5)

        self.join_date_var = tk.StringVar(value=self.config.get('skcc.join_date', ''))
        self.join_date_entry = ttk.Entry(join_date_row, textvariable=self.join_date_var, width=12)
        self.join_date_entry.pack(side='left', padx=5)

        ttk.Button(join_date_row, text="Save",
                  command=self.save_join_date).pack(side='left', padx=5)

        self.join_date_status = ttk.Label(join_date_row, text="", font=('', 9))
        self.join_date_status.pack(side='left', padx=10)

        # Centurion Achievement Date
        centurion_date_row = ttk.Frame(user_info_frame)
        centurion_date_row.pack(fill='x', pady=2)

        ttk.Label(centurion_date_row, text="Centurion Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(centurion_date_row, text="(YYYYMMDD)", font=('', 9), foreground='gray').pack(side='left', padx=5)

        self.centurion_date_var = tk.StringVar(value=self.config.get('skcc.centurion_date', ''))
        self.centurion_date_entry = ttk.Entry(centurion_date_row, textvariable=self.centurion_date_var, width=12)
        self.centurion_date_entry.pack(side='left', padx=5)

        ttk.Button(centurion_date_row, text="Save",
                  command=self.save_centurion_date).pack(side='left', padx=5)

        self.centurion_date_status = ttk.Label(centurion_date_row, text="", font=('', 9))
        self.centurion_date_status.pack(side='left', padx=10)

        # Tribune x8 Achievement Date
        tribune_x8_date_row = ttk.Frame(user_info_frame)
        tribune_x8_date_row.pack(fill='x', pady=2)

        ttk.Label(tribune_x8_date_row, text="Tribune x8 Date:", font=('', 10, 'bold'), width=20).pack(side='left')
        ttk.Label(tribune_x8_date_row, text="(YYYYMMDD)", font=('', 9), foreground='gray').pack(side='left', padx=5)

        self.tribune_x8_date_var = tk.StringVar(value=self.config.get('skcc.tribune_x8_date', ''))
        self.tribune_x8_date_entry = ttk.Entry(tribune_x8_date_row, textvariable=self.tribune_x8_date_var, width=12)
        self.tribune_x8_date_entry.pack(side='left', padx=5)

        ttk.Button(tribune_x8_date_row, text="Save",
                  command=self.save_tribune_x8_date).pack(side='left', padx=5)

        self.tribune_x8_date_status = ttk.Label(tribune_x8_date_row, text="", font=('', 9))
        self.tribune_x8_date_status.pack(side='left', padx=10)

        ttk.Label(user_info_frame,
                 text="⚠️ Critical: Join date required for all awards.",
                 font=('', 9, 'italic'), foreground='darkorange').pack(anchor='w', pady=(5, 0))
        ttk.Label(user_info_frame,
                 text="Centurion date required for Tribune/Senator. Tribune x8 date required for Senator.",
                 font=('', 9, 'italic'), foreground='darkorange').pack(anchor='w')
        ttk.Label(user_info_frame,
                 text="QSOs before these dates will not count toward respective awards.",
                 font=('', 9, 'italic'), foreground='darkorange').pack(anchor='w')

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

        # Marathon
        marathon_frame = ttk.LabelFrame(self.specialty_frame, text="Marathon Award", padding=10)
        marathon_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(marathon_frame, text="100 QSOs of 60+ minutes each, with different SKCC members",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.marathon_progress = ttk.Label(marathon_frame, text="", font=('', 11, 'bold'))
        self.marathon_progress.pack(anchor='w', pady=2)

        self.marathon_bar = ttk.Progressbar(marathon_frame, length=400, mode='determinate')
        self.marathon_bar.pack(fill='x', pady=2)

        self.marathon_details = ttk.Label(marathon_frame, text="", font=('', 9))
        self.marathon_details.pack(anchor='w')

        # QRP/MPW
        qrp_mpw_frame = ttk.LabelFrame(self.specialty_frame, text="QRP Miles Per Watt Award", padding=10)
        qrp_mpw_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(qrp_mpw_frame, text="3 levels: 1,000 MPW, 1,500 MPW, 2,000 MPW (QRP power ≤5W)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.qrp_mpw_progress = ttk.Label(qrp_mpw_frame, text="", font=('', 11, 'bold'))
        self.qrp_mpw_progress.pack(anchor='w', pady=2)

        self.qrp_mpw_details = ttk.Label(qrp_mpw_frame, text="", font=('', 9))
        self.qrp_mpw_details.pack(anchor='w')

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

        # SKCC WAS-T
        was_t_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAS-T (Tribune/Senator)", padding=10)
        was_t_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(was_t_frame, text="Contact Tribune OR Senator members in all 50 US states (effective Feb 1, 2016)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.was_t_progress = ttk.Label(was_t_frame, text="", font=('', 11, 'bold'))
        self.was_t_progress.pack(anchor='w', pady=2)

        self.was_t_bar = ttk.Progressbar(was_t_frame, length=400, mode='determinate')
        self.was_t_bar.pack(fill='x', pady=2)

        # SKCC WAS-S
        was_s_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAS-S (Senator Only)", padding=10)
        was_s_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(was_s_frame, text="Contact Senator members ONLY in all 50 US states (most restrictive)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.was_s_progress = ttk.Label(was_s_frame, text="", font=('', 11, 'bold'))
        self.was_s_progress.pack(anchor='w', pady=2)

        self.was_s_bar = ttk.Progressbar(was_s_frame, length=400, mode='determinate')
        self.was_s_bar.pack(fill='x', pady=2)

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

        # Marathon
        marathon_progress = self.awards['marathon'].calculate_progress(contacts_list)
        self.update_marathon_display(marathon_progress)

        # QRP/MPW
        qrp_mpw_progress = self.awards['qrp_mpw'].calculate_progress(contacts_list)
        self.update_qrp_mpw_display(qrp_mpw_progress)

        # WAS-T
        was_t_progress = self.awards['was_t'].calculate_progress(contacts_list)
        self.update_was_t_display(was_t_progress)

        # WAS-S
        was_s_progress = self.awards['was_s'].calculate_progress(contacts_list)
        self.update_was_s_display(was_s_progress)

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

    def update_marathon_display(self, progress):
        """Update Marathon award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        total_minutes = progress.get('total_minutes', 0)
        unique_members = progress.get('unique_members', 0)
        avg_duration = progress.get('average_duration', 0)

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.marathon_progress.config(
            text=f"{status} - {current} of {required} marathons ({pct:.1f}%)",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.marathon_bar['value'] = pct
        self.marathon_details.config(
            text=f"Total minutes: {total_minutes:,} | Unique members: {unique_members} | Avg duration: {avg_duration:.1f} min"
        )

    def update_qrp_mpw_display(self, progress):
        """Update QRP/MPW award display"""
        max_mpw = progress.get('max_mpw', 0)
        count_1000 = progress.get('count_1000', 0)
        count_1500 = progress.get('count_1500', 0)
        count_2000 = progress.get('count_2000', 0)
        current_level = progress.get('current_level', 'Not Yet')

        status = "✅ ACHIEVED!" if current_level != "Not Yet" else "In Progress"
        self.qrp_mpw_progress.config(
            text=f"{status} - Best: {max_mpw:.1f} MPW - Level: {current_level}",
            foreground='green' if current_level != "Not Yet" else 'black'
        )
        self.qrp_mpw_details.config(
            text=f"≥1,000 MPW: {count_1000} | ≥1,500 MPW: {count_1500} | ≥2,000 MPW: {count_2000}"
        )

    def update_was_t_display(self, progress):
        """Update WAS-T award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        level = progress['level']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.was_t_progress.config(
            text=f"{status} - {current} of {required} states ({pct:.1f}%) - {level}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.was_t_bar['value'] = pct

    def update_was_s_display(self, progress):
        """Update WAS-S award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        level = progress['level']

        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"
        self.was_s_progress.config(
            text=f"{status} - {current} of {required} states ({pct:.1f}%) - {level}",
            foreground='green' if progress['achieved'] else 'black'
        )
        self.was_s_bar['value'] = pct

    def run_diagnostic(self):
        """Run SKCC awards diagnostic to identify configuration issues"""
        # Analyze configuration
        join_date = self.config.get('skcc.join_date', '')
        centurion_date = self.config.get('skcc.centurion_date', '')
        tribune_x8_date = self.config.get('skcc.tribune_x8_date', '')

        # Analyze contacts
        contacts = self.database.get_all_contacts(limit=999999)
        contacts_list = list(contacts)
        total_contacts = len(contacts_list)

        cw_contacts = 0
        skcc_contacts = 0
        key_type_contacts = 0

        for contact in contacts_list:
            if contact['mode'] and contact['mode'].upper() == 'CW':
                cw_contacts += 1
            if contact['skcc_number'] and contact['skcc_number'].strip():
                skcc_contacts += 1
            if contact['key_type'] and contact['key_type'].strip():
                key_type_contacts += 1

        # Build diagnostic message
        report = "SKCC AWARDS DIAGNOSTIC\n" + "="*60 + "\n\n"

        report += "CONFIGURATION:\n" + "-"*60 + "\n"
        if join_date:
            report += f"✓ SKCC Join Date: {join_date}\n"
        else:
            report += "❌ SKCC Join Date: NOT SET (CRITICAL!)\n"

        if centurion_date:
            report += f"✓ Centurion Date: {centurion_date}\n"
        else:
            report += "⚪ Centurion Date: NOT SET\n"

        if tribune_x8_date:
            report += f"✓ Tribune x8 Date: {tribune_x8_date}\n"
        else:
            report += "⚪ Tribune x8 Date: NOT SET\n"

        report += f"\nCONTACT DATA:\n" + "-"*60 + "\n"
        report += f"Total contacts: {total_contacts:,}\n"
        if total_contacts > 0:
            report += f"CW contacts: {cw_contacts:,} ({cw_contacts/total_contacts*100:.1f}%)\n"
            report += f"With SKCC numbers: {skcc_contacts:,} ({skcc_contacts/total_contacts*100:.1f}%)\n"
            report += f"With key types: {key_type_contacts:,} ({key_type_contacts/total_contacts*100:.1f}%)\n"

        # Identify issues and recommendations
        issues = []
        fixes = []

        if not join_date:
            issues.append("SKCC Join Date is NOT SET")
            fixes.append(
                "1. Enter your SKCC Join Date below\n"
                "   Format: YYYYMMDD (e.g., 20200315)\n"
                "   Click 'Save' then 'Refresh Awards'"
            )

        if not centurion_date:
            issues.append("Centurion Date is NOT SET")
            fixes.append(
                "2. Enter your Centurion Date below\n"
                "   (When you reached 100 members)\n"
                "   Click 'Save' then 'Refresh Awards'"
            )

        if total_contacts > 0 and skcc_contacts == 0:
            issues.append("No SKCC numbers in contacts")
            fixes.append(
                "3. Your contacts are missing SKCC numbers\n"
                "   Check ADIF export includes SKCC data"
            )

        if total_contacts > 0 and key_type_contacts == 0:
            issues.append("No key types in contacts")
            fixes.append(
                "4. Contacts need key type data\n"
                "   (STRAIGHT, BUG, SIDESWIPER)"
            )

        if issues:
            report += f"\nISSUES FOUND:\n" + "-"*60 + "\n"
            for i, issue in enumerate(issues, 1):
                report += f"{i}. {issue}\n"

            report += f"\nHOW TO FIX:\n" + "-"*60 + "\n"
            for fix in fixes:
                report += f"\n{fix}\n"

            # Show error dialog
            messagebox.showwarning("SKCC Awards Diagnostic", report)
        else:
            report += f"\n✅ Configuration looks good!\n"
            report += f"\nIf awards still don't show, click 'Refresh Awards'."
            messagebox.showinfo("SKCC Awards Diagnostic", report)

    def get_frame(self):
        """Return the main frame"""
        return self.frame

    # SKCC Roster Management Methods

    def save_join_date(self):
        """Save user's SKCC join date to config"""
        join_date = self.join_date_var.get().strip().replace('-', '')

        # Validate format
        if join_date and (len(join_date) != 8 or not join_date.isdigit()):
            self.join_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground='red'
            )
            return

        # Save to config
        self.config.set('skcc.join_date', join_date)

        # Update status
        if join_date:
            self.join_date_status.config(
                text="✅ Saved",
                foreground='green'
            )
            # Refresh awards to apply new validation
            self.refresh_awards()
        else:
            self.join_date_status.config(
                text="⚠️ Join date cleared",
                foreground='orange'
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.join_date_status.config(text=""))

    def save_centurion_date(self):
        """Save user's Centurion achievement date to config"""
        centurion_date = self.centurion_date_var.get().strip().replace('-', '')

        # Validate format
        if centurion_date and (len(centurion_date) != 8 or not centurion_date.isdigit()):
            self.centurion_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground='red'
            )
            return

        # Validate it's not before join date
        join_date = self.config.get('skcc.join_date', '')
        if centurion_date and join_date and centurion_date < join_date:
            self.centurion_date_status.config(
                text="❌ Cannot be before join date",
                foreground='red'
            )
            return

        # Save to config
        self.config.set('skcc.centurion_date', centurion_date)

        # Update status
        if centurion_date:
            self.centurion_date_status.config(
                text="✅ Saved",
                foreground='green'
            )
            # Refresh awards to apply new validation
            self.refresh_awards()
        else:
            self.centurion_date_status.config(
                text="⚠️ Centurion date cleared",
                foreground='orange'
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.centurion_date_status.config(text=""))

    def save_tribune_x8_date(self):
        """Save user's Tribune x8 achievement date to config"""
        tribune_x8_date = self.tribune_x8_date_var.get().strip().replace('-', '')

        # Validate format
        if tribune_x8_date and (len(tribune_x8_date) != 8 or not tribune_x8_date.isdigit()):
            self.tribune_x8_date_status.config(
                text="❌ Invalid format (use YYYYMMDD)",
                foreground='red'
            )
            return

        # Validate it's not before Centurion date
        centurion_date = self.config.get('skcc.centurion_date', '')
        if tribune_x8_date and centurion_date and tribune_x8_date < centurion_date:
            self.tribune_x8_date_status.config(
                text="❌ Cannot be before Centurion date",
                foreground='red'
            )
            return

        # Save to config
        self.config.set('skcc.tribune_x8_date', tribune_x8_date)

        # Update status
        if tribune_x8_date:
            self.tribune_x8_date_status.config(
                text="✅ Saved",
                foreground='green'
            )
            # Refresh awards to apply new validation
            self.refresh_awards()
        else:
            self.tribune_x8_date_status.config(
                text="⚠️ Tribune x8 date cleared",
                foreground='orange'
            )

        # Clear status after 3 seconds
        self.parent.after(3000, lambda: self.tribune_x8_date_status.config(text=""))

    def update_roster_status(self):
        """Update the roster status label"""
        if self.roster_manager.has_local_roster():
            count = self.roster_manager.get_member_count()
            age = self.roster_manager.get_roster_age()
            self.roster_status_label.config(
                text=f"{count:,} members | Downloaded: {age}",
                foreground='green'
            )
        else:
            self.roster_status_label.config(
                text="Not downloaded - Click 'Download Roster' to download",
                foreground='orange'
            )

    def download_roster_manual(self):
        """Manually triggered roster download"""
        self.roster_status_label.config(text="Downloading...", foreground='blue')

        def progress_callback(msg):
            # Update UI in main thread
            self.parent.after(0, lambda: self.roster_status_label.config(text=msg))

        def completion_callback(success):
            # Update UI when complete
            self.parent.after(0, self.update_roster_status)
            if success:
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Download Complete",
                    f"Successfully downloaded {self.roster_manager.get_member_count():,} SKCC members.\n\n"
                    "The roster is now available for award tracking."
                ))

        self.roster_manager.download_roster_async(progress_callback, completion_callback)

    def auto_download_roster_if_needed(self):
        """
        Auto-download roster on EVERY startup.

        CRITICAL: The roster MUST be updated on every startup to ensure contacts
        are validated with current membership data and member status (C/T/S suffixes)
        at the time of QSO. This is essential for accurate award validation since:
        - Member status can change over time
        - Join dates are critical for validation
        - Awards require both parties to be members at time of contact
        """
        # ALWAYS download roster on startup for accurate award validation
        self.roster_status_label.config(text="Updating SKCC roster...", foreground='blue')

        def progress_callback(msg):
            # Update status label with progress
            self.parent.after(0, lambda: self.roster_status_label.config(text=msg))

        def completion_callback(success):
            # Update roster status display
            self.parent.after(0, self.update_roster_status)
            if success:
                print(f"✓ SKCC roster updated: {self.roster_manager.get_member_count():,} members")

        # Download roster asynchronously so it doesn't block UI startup
        self.roster_manager.download_roster_async(progress_callback, completion_callback)
