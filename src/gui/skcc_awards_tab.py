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
    QRP1xAward, QRP2xAward, QRPMPWAward, MarathonAward
)
from src.skcc_roster import get_roster_manager
from src.skcc_award_rosters import get_award_roster_manager
from src.skcc_awards.award_application import AwardApplicationGenerator
from src.theme_colors import get_success_color, get_info_color, get_muted_color
from src.utils.gridsquare import gridsquare_distance_nm


class SKCCAwardsTab:
    def __init__(self, parent, database, config):
        self.parent = parent
        self.database = database
        self.config = config
        self.frame = ttk.Frame(parent)

        # CRITICAL: Attach config to database so award instances can access it
        # Tribune/Senator awards need to read user's Centurion/Tribune dates from config
        # to filter contacts by achievement dates
        self.database.config = config

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
            'qrp_1x': QRP1xAward(database),
            'qrp_2x': QRP2xAward(database),
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
        specialty_container = ttk.Frame(self.notebook)
        self.geography_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.core_frame, text="  Core Awards  ")
        self.notebook.add(specialty_container, text="  Specialty Awards  ")
        self.notebook.add(self.geography_frame, text="  Geography Awards  ")

        # Create scrollable specialty frame (has many awards that go off screen)
        specialty_canvas = tk.Canvas(specialty_container, highlightthickness=0)
        specialty_scrollbar = ttk.Scrollbar(specialty_container, orient="vertical", command=specialty_canvas.yview)
        self.specialty_frame = ttk.Frame(specialty_canvas)

        self.specialty_frame.bind(
            "<Configure>",
            lambda e: specialty_canvas.configure(scrollregion=specialty_canvas.bbox("all"))
        )

        specialty_canvas.create_window((0, 0), window=self.specialty_frame, anchor="nw")
        specialty_canvas.configure(yscrollcommand=specialty_scrollbar.set)

        specialty_canvas.pack(side="left", fill="both", expand=True)
        specialty_scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling for specialty awards (cross-platform)
        def _on_specialty_mousewheel(event):
            # Cross-platform mousewheel handling
            if hasattr(event, 'delta'):
                # Windows and macOS: delta is typically ±120 on Windows, smaller on macOS
                delta = event.delta
                if delta > 0:
                    specialty_canvas.yview_scroll(-1, "units")
                elif delta < 0:
                    specialty_canvas.yview_scroll(1, "units")
            elif hasattr(event, 'num'):
                # Linux: Button-4 (scroll up) and Button-5 (scroll down)
                if event.num == 4:
                    specialty_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    specialty_canvas.yview_scroll(1, "units")

        # Bind mousewheel to canvas directly (not bind_all to avoid conflicts)
        specialty_canvas.bind("<MouseWheel>", _on_specialty_mousewheel)
        specialty_canvas.bind("<Button-4>", _on_specialty_mousewheel)  # Linux scroll up
        specialty_canvas.bind("<Button-5>", _on_specialty_mousewheel)  # Linux scroll down

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

        self.senator_band_progress = ttk.Label(
            senator_frame, text="", font=('', 9), foreground=get_muted_color(self.config)
        )
        self.senator_band_progress.pack(anchor='w', pady=(2, 0))

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

        ttk.Button(triple_key_frame, text="📄 Generate Award Application",
                  command=self.generate_triple_key_application).pack(anchor='w', pady=(10, 0))

        # Rag Chew
        rag_chew_frame = ttk.LabelFrame(self.specialty_frame, text="Rag Chew Award", padding=10)
        rag_chew_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(rag_chew_frame, text="Accumulate 300+ minutes of extended CW conversations",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.rag_chew_progress = ttk.Label(rag_chew_frame, text="", font=('', 11, 'bold'))
        self.rag_chew_progress.pack(anchor='w', pady=2)

        self.rag_chew_bar = ttk.Progressbar(rag_chew_frame, length=400, mode='determinate')
        self.rag_chew_bar.pack(fill='x', pady=2)

        ttk.Button(rag_chew_frame, text="📄 Generate Award Application",
                  command=self.generate_rag_chew_application).pack(anchor='w', pady=(10, 0))

        # PFX
        pfx_frame = ttk.LabelFrame(self.specialty_frame, text="PFX Award", padding=10)
        pfx_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(pfx_frame, text="Accumulate 500,000+ points from callsign prefixes",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.pfx_progress = ttk.Label(pfx_frame, text="", font=('', 11, 'bold'))
        self.pfx_progress.pack(anchor='w', pady=2)

        self.pfx_bar = ttk.Progressbar(pfx_frame, length=400, mode='determinate')
        self.pfx_bar.pack(fill='x', pady=2)

        ttk.Button(pfx_frame, text="📄 Generate Award Application",
                  command=self.generate_pfx_application).pack(anchor='w', pady=(10, 0))

        # Canadian Maple
        maple_frame = ttk.LabelFrame(self.specialty_frame, text="Canadian Maple Award", padding=10)
        maple_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(maple_frame, text="4 levels: Yellow (10 prov/terr), Orange (10 on one band), Red (90 contacts), Gold (90 QRP)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.maple_progress = ttk.Label(maple_frame, text="", font=('', 11, 'bold'))
        self.maple_progress.pack(anchor='w', pady=2)

        ttk.Button(maple_frame, text="📄 Generate Award Application",
                  command=self.generate_canadian_maple_application).pack(anchor='w', pady=(10, 0))

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

        ttk.Button(marathon_frame, text="📄 Generate Award Application",
                  command=self.generate_marathon_application).pack(anchor='w', pady=(10, 0))

        # 1xQRP
        qrp_1x_frame = ttk.LabelFrame(self.specialty_frame, text="1xQRP Award", padding=10)
        qrp_1x_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(qrp_1x_frame,
                 text="300 points; applicant QRP (≤5W), one contact per band per station",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.qrp_1x_progress = ttk.Label(qrp_1x_frame, text="", font=('', 11, 'bold'))
        self.qrp_1x_progress.pack(anchor='w', pady=2)

        self.qrp_1x_bar = ttk.Progressbar(qrp_1x_frame, length=400, mode='determinate')
        self.qrp_1x_bar.pack(fill='x', pady=2)

        self.qrp_1x_details = ttk.Label(qrp_1x_frame, text="", font=('', 9))
        self.qrp_1x_details.pack(anchor='w')

        ttk.Button(qrp_1x_frame, text="📄 Generate Award Application",
                  command=self.generate_qrp_1x_application).pack(anchor='w', pady=(10, 0))

        # 2xQRP
        qrp_2x_frame = ttk.LabelFrame(self.specialty_frame, text="2xQRP Award", padding=10)
        qrp_2x_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(qrp_2x_frame,
                 text="150 points; both stations QRP (≤5W), one contact per band per station",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.qrp_2x_progress = ttk.Label(qrp_2x_frame, text="", font=('', 11, 'bold'))
        self.qrp_2x_progress.pack(anchor='w', pady=2)

        self.qrp_2x_bar = ttk.Progressbar(qrp_2x_frame, length=400, mode='determinate')
        self.qrp_2x_bar.pack(fill='x', pady=2)

        self.qrp_2x_details = ttk.Label(qrp_2x_frame, text="", font=('', 9))
        self.qrp_2x_details.pack(anchor='w')

        ttk.Button(qrp_2x_frame, text="📄 Generate Award Application",
                  command=self.generate_qrp_2x_application).pack(anchor='w', pady=(10, 0))

        # QRP/MPW
        qrp_mpw_frame = ttk.LabelFrame(self.specialty_frame, text="QRP Miles Per Watt Award", padding=10)
        qrp_mpw_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(qrp_mpw_frame, text="Endorsements every 500 MPW starting at 1,000 (QRP ≤5W, N9SSA distance)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.qrp_mpw_progress = ttk.Label(qrp_mpw_frame, text="", font=('', 11, 'bold'))
        self.qrp_mpw_progress.pack(anchor='w', pady=2)

        self.qrp_mpw_details = ttk.Label(qrp_mpw_frame, text="", font=('', 9))
        self.qrp_mpw_details.pack(anchor='w')

        ttk.Button(qrp_mpw_frame, text="📄 Generate Award Application",
                  command=self.generate_qrp_mpw_application).pack(anchor='w', pady=(10, 0))

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

        ttk.Button(was_frame, text="📄 Generate Award Application",
                  command=self.generate_was_application).pack(anchor='w', pady=(10, 0))

        # SKCC WAS-T
        was_t_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAS-T (Tribune/Senator)", padding=10)
        was_t_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(was_t_frame, text="Contact Tribune OR Senator members in all 50 US states (effective Feb 1, 2016)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.was_t_progress = ttk.Label(was_t_frame, text="", font=('', 11, 'bold'))
        self.was_t_progress.pack(anchor='w', pady=2)

        self.was_t_bar = ttk.Progressbar(was_t_frame, length=400, mode='determinate')
        self.was_t_bar.pack(fill='x', pady=2)

        ttk.Button(was_t_frame, text="📄 Generate Award Application",
                  command=self.generate_was_t_application).pack(anchor='w', pady=(10, 0))

        # SKCC WAS-S
        was_s_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAS-S (Senator Only)", padding=10)
        was_s_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(was_s_frame, text="Contact Senator members ONLY in all 50 US states (most restrictive)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.was_s_progress = ttk.Label(was_s_frame, text="", font=('', 11, 'bold'))
        self.was_s_progress.pack(anchor='w', pady=2)

        self.was_s_bar = ttk.Progressbar(was_s_frame, length=400, mode='determinate')
        self.was_s_bar.pack(fill='x', pady=2)

        ttk.Button(was_s_frame, text="📄 Generate Award Application",
                  command=self.generate_was_s_application).pack(anchor='w', pady=(10, 0))

        # SKCC WAC
        wac_frame = ttk.LabelFrame(self.geography_frame, text="SKCC WAC (Worked All Continents)", padding=10)
        wac_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(wac_frame, text="Contact SKCC members in all 6 continents",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.wac_progress = ttk.Label(wac_frame, text="", font=('', 11, 'bold'))
        self.wac_progress.pack(anchor='w', pady=2)

        self.wac_bar = ttk.Progressbar(wac_frame, length=400, mode='determinate')
        self.wac_bar.pack(fill='x', pady=2)

        ttk.Button(wac_frame, text="📄 Generate Award Application",
                  command=self.generate_wac_application).pack(anchor='w', pady=(10, 0))

        # DXQ
        dxq_frame = ttk.LabelFrame(self.geography_frame, text="SKCC DXQ (QSO-based DX)", padding=10)
        dxq_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(dxq_frame, text="Contact SKCC members in 10+ DXCC entities (each contact counts)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.dxq_progress = ttk.Label(dxq_frame, text="", font=('', 11, 'bold'))
        self.dxq_progress.pack(anchor='w', pady=2)

        ttk.Button(dxq_frame, text="📄 Generate Award Application",
                  command=self.generate_dxq_application).pack(anchor='w', pady=(10, 0))

        # DXC
        dxc_frame = ttk.LabelFrame(self.geography_frame, text="SKCC DXC (Country-based DX)", padding=10)
        dxc_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(dxc_frame, text="Contact SKCC members in 10+ DXCC entities (each country counts once)",
                 font=('', 9, 'italic')).pack(anchor='w')

        self.dxc_progress = ttk.Label(dxc_frame, text="", font=('', 11, 'bold'))
        self.dxc_progress.pack(anchor='w', pady=2)

        ttk.Button(dxc_frame, text="📄 Generate Award Application",
                  command=self.generate_dxc_application).pack(anchor='w', pady=(10, 0))

    def refresh_awards(self):
        """Refresh all award progress displays"""
        # Get all contacts for calculations
        contacts = self.database.get_all_contacts(limit=999999)
        contacts_list = [dict(c) for c in contacts]

        # Calculate distance from gridsquares if not already set
        contacts_to_update = []
        for contact in contacts_list:
            if contact.get('distance_nm') is None:
                my_grid = contact.get('my_gridsquare', '').strip()
                their_grid = contact.get('gridsquare', '').strip()

                if my_grid and their_grid and len(my_grid) >= 4 and len(their_grid) >= 4:
                    try:
                        distance_nm = gridsquare_distance_nm(my_grid, their_grid)
                        if distance_nm is not None:
                            contact['distance_nm'] = distance_nm
                            # Queue this contact for database update
                            if contact.get('id'):
                                contacts_to_update.append((contact['id'], distance_nm))
                    except Exception:
                        pass  # Skip if calculation fails

        # Persist calculated distances to database
        if contacts_to_update:
            try:
                for contact_id, distance_nm in contacts_to_update:
                    self.database.update_contact(contact_id, {'distance_nm': distance_nm})
            except Exception as e:
                print(f"Warning: Could not persist distance calculations: {e}")

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

        # 1xQRP
        qrp_1x_progress = self.awards['qrp_1x'].calculate_progress(contacts_list)
        self.update_qrp_1x_display(qrp_1x_progress)

        # 2xQRP
        qrp_2x_progress = self.awards['qrp_2x'].calculate_progress(contacts_list)
        self.update_qrp_2x_display(qrp_2x_progress)

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

        band_counts = progress.get('band_counts') or {}
        band_endorsements = progress.get('band_endorsements') or []
        if band_endorsements:
            bands_str = ", ".join(band_endorsements)
            self.senator_band_progress.config(
                text=f"Per-band endorsements earned: {bands_str}"
            )
        elif band_counts:
            best_band, best_count = max(band_counts.items(), key=lambda item: item[1])
            needed = max(0, 200 - best_count)
            self.senator_band_progress.config(
                text=f"Per-band best: {best_band} {best_count}/200 (need {needed})"
            )
        else:
            self.senator_band_progress.config(text="Per-band endorsements: none yet")

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

    def _format_qrp_band_summary(self, progress):
        """Format band/points summary for QRP awards."""
        points_by_band = progress.get('points_by_band', {})
        qsos_by_band = progress.get('qsos_by_band', {})
        if not points_by_band:
            return "No qualifying QSOs yet"

        band_order = ['160M', '80M', '60M', '40M', '30M', '20M', '17M',
                      '15M', '12M', '10M', '6M', '2M']
        parts = []

        for band in band_order:
            if band in points_by_band:
                points = points_by_band[band]
                points_str = f"{points:.1f}" if points % 1 else f"{int(points)}"
                qsos = qsos_by_band.get(band, 0)
                parts.append(f"{band}:{points_str} ({qsos})")

        for band in sorted(points_by_band.keys()):
            if band not in band_order:
                points = points_by_band[band]
                points_str = f"{points:.1f}" if points % 1 else f"{int(points)}"
                qsos = qsos_by_band.get(band, 0)
                parts.append(f"{band}:{points_str} ({qsos})")

        duplicate_contacts = progress.get('duplicate_contacts', 0)
        summary = "Bands: " + " | ".join(parts)
        if duplicate_contacts:
            summary += f" | Duplicates ignored: {duplicate_contacts}"
        return summary

    def update_qrp_1x_display(self, progress):
        """Update 1xQRP award display"""
        current_points = progress.get('current_points', 0)
        required = progress.get('required_points', 0)
        pct = progress.get('progress_pct', 0)

        status = "✅ ACHIEVED!" if progress.get('achieved', False) else "In Progress"
        self.qrp_1x_progress.config(
            text=f"{status} - {current_points:.1f} of {required} points ({pct:.1f}%)",
            foreground=get_success_color(self.config) if progress.get('achieved', False) else 'black'
        )
        self.qrp_1x_bar['value'] = pct
        self.qrp_1x_details.config(text=self._format_qrp_band_summary(progress))

    def update_qrp_2x_display(self, progress):
        """Update 2xQRP award display"""
        current_points = progress.get('current_points', 0)
        required = progress.get('required_points', 0)
        pct = progress.get('progress_pct', 0)

        status = "✅ ACHIEVED!" if progress.get('achieved', False) else "In Progress"
        self.qrp_2x_progress.config(
            text=f"{status} - {current_points:.1f} of {required} points ({pct:.1f}%)",
            foreground=get_success_color(self.config) if progress.get('achieved', False) else 'black'
        )
        self.qrp_2x_bar['value'] = pct
        self.qrp_2x_details.config(text=self._format_qrp_band_summary(progress))

    def update_qrp_mpw_display(self, progress):
        """Update QRP/MPW award display"""
        max_mpw = progress.get('max_mpw', 0)
        count_1000 = progress.get('count_1000', 0)
        count_1500 = progress.get('count_1500', 0)
        count_2000 = progress.get('count_2000', 0)
        current_level = progress.get('current_level', 'Not Achieved')
        achieved = progress.get('achieved', False)

        status = "✅ ACHIEVED!" if achieved else "In Progress"
        self.qrp_mpw_progress.config(
            text=f"{status} - Best: {max_mpw:.1f} MPW - Level: {current_level}",
            foreground=get_success_color(self.config) if achieved else 'black'
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

    # Core Awards
    def generate_centurion_application(self):
        """Generate Centurion award application"""
        self._generate_award_application('centurion', 'Centurion')

    def generate_tribune_application(self):
        """Generate Tribune award application"""
        self._generate_award_application('tribune', 'Tribune')

    def generate_senator_application(self):
        """Generate Senator award application"""
        self._generate_award_application('senator', 'Senator')

    # Specialty Awards
    def generate_triple_key_application(self):
        """Generate Triple Key award application"""
        self._generate_award_application('triple_key', 'Triple_Key')

    def generate_rag_chew_application(self):
        """Generate Rag Chew award application"""
        self._generate_award_application('rag_chew', 'Rag_Chew')

    def generate_marathon_application(self):
        """Generate Marathon award application"""
        self._generate_award_application('marathon', 'Marathon')

    def generate_qrp_1x_application(self):
        """Generate 1xQRP award application"""
        self._generate_award_application('qrp_1x', '1xQRP')

    def generate_qrp_2x_application(self):
        """Generate 2xQRP award application"""
        self._generate_award_application('qrp_2x', '2xQRP')

    def generate_pfx_application(self):
        """Generate PFX award application"""
        self._generate_award_application('pfx', 'PFX')

    def generate_canadian_maple_application(self):
        """Generate Canadian Maple award application"""
        self._generate_award_application('canadian_maple', 'Canadian_Maple')

    def generate_qrp_mpw_application(self):
        """Generate QRP/MPW award application"""
        self._generate_award_application('qrp_mpw', 'QRP_MPW')

    # Geography Awards
    def generate_dxq_application(self):
        """Generate DXQ award application"""
        self._generate_award_application('dxq', 'DXQ')

    def generate_dxc_application(self):
        """Generate DXC award application"""
        self._generate_award_application('dxc', 'DXC')

    def generate_was_application(self):
        """Generate WAS award application"""
        self._generate_award_application('was', 'WAS')

    def generate_was_t_application(self):
        """Generate WAS-T award application"""
        self._generate_award_application('was_t', 'WAS-T')

    def generate_was_s_application(self):
        """Generate WAS-S award application"""
        self._generate_award_application('was_s', 'WAS-S')

    def generate_wac_application(self):
        """Generate WAC award application"""
        self._generate_award_application('wac', 'WAC')

    def _generate_award_application(self, award_type: str, award_name: str):
        """
        Generate award application report and save to file

        Args:
            award_type: Type of award (centurion, tribune, senator, dxq, dxc, etc.)
            award_name: Display name of the award
        """
        # Get all contacts
        all_contacts = self.database.get_all_contacts(limit=999999)
        contacts_list = [dict(c) for c in all_contacts]

        # Get qualifying contacts for this award
        award_instance = self.awards[award_type]
        if hasattr(award_instance, 'get_application_contacts'):
            qualifying_contacts = award_instance.get_application_contacts(contacts_list)
        else:
            qualifying_contacts = [c for c in contacts_list if award_instance.validate(c)]

            # Sort by date (earliest first)
            qualifying_contacts.sort(key=lambda x: (x.get('date', ''), x.get('time_on', '')))

            # Deduplicate by SKCC number when required by award rules
            if award_instance.should_deduplicate_for_export():
                from src.utils.skcc_number import extract_base_skcc_number
                seen_skcc_numbers = set()
                deduplicated_contacts = []

                for contact in qualifying_contacts:
                    skcc_number = contact.get('skcc_number', '').strip()
                    if skcc_number:
                        base_number = extract_base_skcc_number(skcc_number)
                        if base_number and base_number not in seen_skcc_numbers:
                            seen_skcc_numbers.add(base_number)
                            deduplicated_contacts.append(contact)

                qualifying_contacts = deduplicated_contacts

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

        # Sort for output consistency if not already sorted
        qualifying_contacts.sort(key=lambda x: (x.get('date', ''), x.get('time_on', '')))

        # Generate the report based on award type
        try:
            report = self._get_report_for_award(award_type, qualifying_contacts)
        except ValueError as e:
            messagebox.showerror(
                "Unknown Award Type",
                f"Failed to generate report: {e}"
            )
            return

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

    def _get_report_for_award(self, award_type: str, contacts):
        """
        Get the appropriate report generator for the award type

        Args:
            award_type: Type of award
            contacts: List of qualifying contacts

        Returns:
            Generated report string
        """
        report_generators = {
            'centurion': self.app_generator.generate_centurion_report,
            'tribune': self.app_generator.generate_tribune_report,
            'senator': self.app_generator.generate_senator_report,
            'dxq': self.app_generator.generate_dxq_report,
            'dxc': self.app_generator.generate_dxc_report,
            'was': self.app_generator.generate_was_report,
            'was_t': self.app_generator.generate_was_t_report,
            'was_s': self.app_generator.generate_was_s_report,
            'wac': self.app_generator.generate_wac_report,
            'triple_key': self.app_generator.generate_triple_key_report,
            'rag_chew': self.app_generator.generate_rag_chew_report,
            'marathon': self.app_generator.generate_marathon_report,
            'qrp_1x': self.app_generator.generate_qrp_1x_report,
            'qrp_2x': self.app_generator.generate_qrp_2x_report,
            'pfx': self.app_generator.generate_pfx_report,
            'canadian_maple': self.app_generator.generate_canadian_maple_report,
            'qrp_mpw': self.app_generator.generate_qrp_mpw_report,
        }

        generator = report_generators.get(award_type)
        if generator:
            return generator(contacts)
        else:
            raise ValueError(f"Unknown award type: {award_type}")

    def get_frame(self):
        """Return the main frame"""
        return self.frame
