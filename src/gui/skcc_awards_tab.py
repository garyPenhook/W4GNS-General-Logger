"""
SKCC Awards Tab - Display Straight Key Century Club award progress
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from src.skcc_awards import (
    CenturionAward, TribuneAward, SenatorAward,
    TripleKeyAward, RagChewAward, CanadianMapleAward,
    SKCCDXQAward, SKCCDXCAward, PFXAward,
    SKCCWASAward, SKCCWASTAward, SKCCWASSAward, SKCCWACAward,
    QRPMPWAward, MarathonAward
)
from src.skcc_roster import get_roster_manager
from src.skcc_award_rosters import get_award_roster_manager
from src.skcc_awards.award_application import AwardApplicationGenerator
from src.theme_colors import get_success_color, get_error_color, get_warning_color, get_info_color, get_muted_color


class SKCCAwardsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)

        # Initialize roster managers
        self.roster_manager = get_roster_manager()
        self.award_rosters = get_award_roster_manager(database=self.database)

        # Initialize award application generator
        self.app_generator = AwardApplicationGenerator(database, config)

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
        self.refresh_awards()

    def create_widgets(self):
        """Create the SKCC awards interface"""

        # Header with refresh button
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(header_frame, text="SKCC Awards Progress",
                 font=('', 14, 'bold')).pack(side='left')
        ttk.Label(header_frame, text="(Straight Key Century Club)",
                 font=('', 10), foreground=get_muted_color(self.config)).pack(side='left', padx=10)

        ttk.Button(header_frame, text="🔍 Run Diagnostic",
                  command=self.run_diagnostic).pack(side='right', padx=2)
        ttk.Button(header_frame, text="Refresh Awards",
                  command=self.refresh_awards).pack(side='right', padx=5)

        # Info message about settings
        info_frame = ttk.Frame(self.frame)
        info_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(info_frame,
                 text="💡 Configure SKCC settings (Join Date, Centurion Date, etc.) in the Settings tab",
                 font=('', 9, 'italic'), foreground=get_info_color(self.config)).pack(anchor='w')

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

        # Endorsement status section
        endorsement_centurion_frame = ttk.Frame(centurion_frame)
        endorsement_centurion_frame.pack(fill='x', pady=(5, 0))

        self.centurion_endorsement = ttk.Label(endorsement_centurion_frame, text="",
                                               font=('', 10, 'bold'), foreground=get_info_color(self.config))
        self.centurion_endorsement.pack(anchor='w')

        # Progress to next endorsement
        self.centurion_next_endorsement = ttk.Label(endorsement_centurion_frame, text="",
                                                     font=('', 9), foreground=get_muted_color(self.config))
        self.centurion_next_endorsement.pack(anchor='w')

        self.centurion_endorsement_bar = ttk.Progressbar(endorsement_centurion_frame,
                                                          length=300, mode='determinate')
        self.centurion_endorsement_bar.pack(anchor='w', pady=(2, 0))

        # Generate Application button
        ttk.Button(centurion_frame, text="📄 Generate Award Application",
                  command=self.generate_centurion_application).pack(anchor='w', pady=(10, 0))

        # Tribune
        tribune_frame = ttk.LabelFrame(self.core_frame, text="Tribune Award", padding=10)
        tribune_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(tribune_frame, text="Contact 50 Tribune/Senator members (requires Centurion)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.tribune_progress = ttk.Label(tribune_frame, text="", font=('', 11, 'bold'))
        self.tribune_progress.pack(anchor='w', pady=2)

        self.tribune_bar = ttk.Progressbar(tribune_frame, length=400, mode='determinate')
        self.tribune_bar.pack(fill='x', pady=2)

        # Endorsement status section
        endorsement_tribune_frame = ttk.Frame(tribune_frame)
        endorsement_tribune_frame.pack(fill='x', pady=(5, 0))

        self.tribune_endorsement = ttk.Label(endorsement_tribune_frame, text="",
                                             font=('', 10, 'bold'), foreground=get_info_color(self.config))
        self.tribune_endorsement.pack(anchor='w')

        # Progress to next endorsement
        self.tribune_next_endorsement = ttk.Label(endorsement_tribune_frame, text="",
                                                   font=('', 9), foreground=get_muted_color(self.config))
        self.tribune_next_endorsement.pack(anchor='w')

        self.tribune_endorsement_bar = ttk.Progressbar(endorsement_tribune_frame,
                                                        length=300, mode='determinate')
        self.tribune_endorsement_bar.pack(anchor='w', pady=(2, 0))

        # Generate Application button
        ttk.Button(tribune_frame, text="📄 Generate Award Application",
                  command=self.generate_tribune_application).pack(anchor='w', pady=(10, 0))

        # Senator
        senator_frame = ttk.LabelFrame(self.core_frame, text="Senator Award", padding=10)
        senator_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(senator_frame, text="Contact 200 Tribune/Senator members AFTER achieving Tribune x8",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.senator_progress = ttk.Label(senator_frame, text="", font=('', 11, 'bold'))
        self.senator_progress.pack(anchor='w', pady=2)

        self.senator_bar = ttk.Progressbar(senator_frame, length=400, mode='determinate')
        self.senator_bar.pack(fill='x', pady=2)

        # Endorsement status section
        endorsement_senator_frame = ttk.Frame(senator_frame)
        endorsement_senator_frame.pack(fill='x', pady=(5, 0))

        self.senator_endorsement = ttk.Label(endorsement_senator_frame, text="",
                                             font=('', 10, 'bold'), foreground=get_info_color(self.config))
        self.senator_endorsement.pack(anchor='w')

        # Progress to next endorsement
        self.senator_next_endorsement = ttk.Label(endorsement_senator_frame, text="",
                                                   font=('', 9), foreground=get_muted_color(self.config))
        self.senator_next_endorsement.pack(anchor='w')

        self.senator_endorsement_bar = ttk.Progressbar(endorsement_senator_frame,
                                                        length=300, mode='determinate')
        self.senator_endorsement_bar.pack(anchor='w', pady=(2, 0))

        # Generate Application button
        ttk.Button(senator_frame, text="📄 Generate Award Application",
                  command=self.generate_senator_application).pack(anchor='w', pady=(10, 0))

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
        next_level_count = progress.get('next_level_count')

        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"
        self.centurion_progress.config(
            text=f"{status} - {current} of {required} members ({pct:.1f}%)",
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
        )
        self.centurion_bar['value'] = pct

        # Update endorsement status
        if endorsement == "Not Yet":
            self.centurion_endorsement.config(text="Endorsement Level: Not Yet Achieved")
            self.centurion_next_endorsement.config(text=f"Need {required - current} more contacts for Centurion")
            self.centurion_endorsement_bar['value'] = pct
        else:
            self.centurion_endorsement.config(text=f"🏆 Endorsement Level: {endorsement}")

            # Show progress to next level
            if next_level_count and next_level_count > current:
                needed = next_level_count - current
                from src.skcc_awards.constants import CENTURION_ENDORSEMENTS
                next_endorsement = None
                for threshold, name in CENTURION_ENDORSEMENTS:
                    if threshold == next_level_count:
                        next_endorsement = name
                        break

                # Calculate previous threshold
                prev_threshold = 0
                for threshold, name in CENTURION_ENDORSEMENTS:
                    if threshold <= current:
                        prev_threshold = threshold

                # Calculate progress between previous and next threshold
                if next_level_count > prev_threshold:
                    progress_to_next = ((current - prev_threshold) / (next_level_count - prev_threshold)) * 100
                else:
                    progress_to_next = 0

                self.centurion_next_endorsement.config(
                    text=f"Next: {next_endorsement} ({current}/{next_level_count}) - Need {needed} more"
                )
                self.centurion_endorsement_bar['value'] = progress_to_next
            else:
                self.centurion_next_endorsement.config(text="🌟 Maximum endorsement level achieved!")
                self.centurion_endorsement_bar['value'] = 100

    def update_tribune_display(self, progress):
        """Update Tribune award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']
        next_level_count = progress.get('next_level_count')

        prereq_status = "✅" if progress.get('prerequisite_met') else "❌"
        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"

        self.tribune_progress.config(
            text=f"{prereq_status} Centurion | {status} - {current} of {required} Tribune/Senator members ({pct:.1f}%)",
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
        )
        self.tribune_bar['value'] = pct

        # Update endorsement status
        if endorsement == "Not Yet":
            self.tribune_endorsement.config(text="Endorsement Level: Not Yet Achieved")
            self.tribune_next_endorsement.config(text=f"Need {required - current} more contacts for Tribune")
            self.tribune_endorsement_bar['value'] = pct
        else:
            self.tribune_endorsement.config(text=f"🏆 Endorsement Level: {endorsement}")

            # Show progress to next level
            if next_level_count and next_level_count > current:
                needed = next_level_count - current
                from src.skcc_awards.constants import TRIBUNE_ENDORSEMENTS
                next_endorsement = None
                for threshold, name in TRIBUNE_ENDORSEMENTS:
                    if threshold == next_level_count:
                        next_endorsement = name
                        break

                # Calculate previous threshold
                prev_threshold = 0
                for threshold, name in TRIBUNE_ENDORSEMENTS:
                    if threshold <= current:
                        prev_threshold = threshold

                # Calculate progress between previous and next threshold
                if next_level_count > prev_threshold:
                    progress_to_next = ((current - prev_threshold) / (next_level_count - prev_threshold)) * 100
                else:
                    progress_to_next = 0

                self.tribune_next_endorsement.config(
                    text=f"Next: {next_endorsement} ({current}/{next_level_count}) - Need {needed} more"
                )
                self.tribune_endorsement_bar['value'] = progress_to_next
            else:
                self.tribune_next_endorsement.config(text="🌟 Maximum endorsement level achieved!")
                self.tribune_endorsement_bar['value'] = 100

    def update_senator_display(self, progress):
        """Update Senator award display"""
        current = progress['current']
        required = progress['required']
        pct = progress['progress_pct']
        endorsement = progress['endorsement']
        next_level_count = progress.get('next_level_count')

        prereq_status = "✅" if progress.get('prerequisite_met') else "❌"
        status = "✅ ACHIEVED!" if progress['achieved'] else f"In Progress"

        self.senator_progress.config(
            text=f"{prereq_status} Tribune x8 | {status} - {current} of {required} post-x8 contacts ({pct:.1f}%)",
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
        )
        self.senator_bar['value'] = pct

        # Update endorsement status
        if endorsement == "Not Yet":
            self.senator_endorsement.config(text="Endorsement Level: Not Yet Achieved")
            self.senator_next_endorsement.config(text=f"Need {required - current} more contacts for Senator")
            self.senator_endorsement_bar['value'] = pct
        else:
            self.senator_endorsement.config(text=f"🏆 Endorsement Level: {endorsement}")

            # Show progress to next level
            if next_level_count and next_level_count > current:
                needed = next_level_count - current
                from src.skcc_awards.constants import SENATOR_ENDORSEMENTS
                next_endorsement = None
                for threshold, name in SENATOR_ENDORSEMENTS:
                    if threshold == next_level_count:
                        next_endorsement = name
                        break

                # Calculate previous threshold
                prev_threshold = 0
                for threshold, name in SENATOR_ENDORSEMENTS:
                    if threshold <= current:
                        prev_threshold = threshold

                # Calculate progress between previous and next threshold
                if next_level_count > prev_threshold:
                    progress_to_next = ((current - prev_threshold) / (next_level_count - prev_threshold)) * 100
                else:
                    progress_to_next = 0

                self.senator_next_endorsement.config(
                    text=f"Next: {next_endorsement} ({current}/{next_level_count}) - Need {needed} more"
                )
                self.senator_endorsement_bar['value'] = progress_to_next
            else:
                self.senator_next_endorsement.config(text="🌟 Maximum endorsement level achieved!")
                self.senator_endorsement_bar['value'] = 100

    def update_triple_key_display(self, progress):
        """Update Triple Key award display"""
        status = "✅ ACHIEVED!" if progress['achieved'] else "In Progress"

        by_key = progress['by_key_type']
        straight = by_key['STRAIGHT']['count']
        bug = by_key['BUG']['count']
        sideswiper = by_key['SIDESWIPER']['count']

        self.triple_key_progress.config(
            text=f"{status} - Minimum: {progress['current']} of 100",
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if highest != "Not Yet" else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
        )
        self.wac_bar['value'] = pct

    def update_dxq_display(self, progress):
        """Update DXQ award display"""
        entities = progress['entities_worked']
        qsos = progress['total_qsos']
        level = progress['achieved_level']

        self.dxq_progress.config(
            text=f"{entities} entities worked, {qsos} total QSOs - Level: {level}",
            foreground=get_success_color(self.config) if level != "Not Yet" else 'black'
        )

    def update_dxc_display(self, progress):
        """Update DXC award display"""
        entities = progress['current']
        level = progress['achieved_level']

        self.dxc_progress.config(
            text=f"{entities} entities worked (each counts once) - Level: {level}",
            foreground=get_success_color(self.config) if level != "Not Yet" else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if current_level != "Not Yet" else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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
            foreground=get_success_color(self.config) if progress['achieved'] else 'black'
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

    def generate_centurion_application(self):
        """Generate Centurion award application"""
        self._generate_award_application('centurion', 'Centurion')

    def generate_tribune_application(self):
        """Generate Tribune award application"""
        self._generate_award_application('tribune', 'Tribune')

    def generate_senator_application(self):
        """Generate Senator award application"""
        self._generate_award_application('senator', 'Senator')

    def _generate_award_application(self, award_type: str, award_name: str):
        """
        Generate award application report and save to file

        Args:
            award_type: Type of award ('centurion', 'tribune', 'senator')
            award_name: Display name of the award
        """
        # Get all contacts
        all_contacts = self.database.get_all_contacts(limit=999999)
        contacts_list = [dict(c) for c in all_contacts]

        # Get qualifying contacts for this award
        award_instance = self.awards[award_type]
        qualifying_contacts = []

        for contact in contacts_list:
            if award_instance.validate(contact):
                qualifying_contacts.append(contact)

        if not qualifying_contacts:
            messagebox.showwarning(
                "No Qualifying Contacts",
                f"No contacts found that qualify for the {award_name} award.\n\n"
                f"Make sure you have:\n"
                f"- Logged contacts with SKCC members\n"
                f"- Used CW mode\n"
                f"- Recorded key types\n"
                f"- Set your SKCC configuration in Settings"
            )
            return

        # Sort by date
        qualifying_contacts.sort(key=lambda x: (x.get('date', ''), x.get('time_on', '')))

        # Generate the report
        if award_type == 'centurion':
            report = self.app_generator.generate_centurion_report(qualifying_contacts)
        elif award_type == 'tribune':
            report = self.app_generator.generate_tribune_report(qualifying_contacts)
        elif award_type == 'senator':
            report = self.app_generator.generate_senator_report(qualifying_contacts)

        # Ask user where to save
        callsign = self.config.get('callsign', 'UNKNOWN')
        default_filename = f"SKCC_{award_name}_{callsign}_{datetime.now().strftime('%Y%m%d')}.txt"

        filename = filedialog.asksaveasfilename(
            title=f"Save {award_name} Award Application",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if not filename:
            return  # User cancelled

        # Save the report
        if self.app_generator.save_report_to_file(report, filename):
            messagebox.showinfo(
                "Application Generated",
                f"{award_name} award application generated successfully!\n\n"
                f"File: {filename}\n\n"
                f"Qualifying contacts: {len(qualifying_contacts)}\n\n"
                f"You can now submit this file to the SKCC awards manager."
            )
        else:
            messagebox.showerror(
                "Error",
                f"Failed to save award application to:\n{filename}"
            )

    def get_frame(self):
        """Return the main frame"""
        return self.frame
