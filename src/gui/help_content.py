"""
Comprehensive help content for W4GNS General Logger
All help topics with detailed instructions and examples
"""


class HelpContent:
    """Provides detailed help content for all application features"""

    @staticmethod
    def get_content(topic_id):
        """Get help content for a specific topic"""
        content_map = {
            'welcome': HelpContent.welcome,
            'installation': HelpContent.installation,
            'first_time_setup': HelpContent.first_time_setup,
            'quick_start': HelpContent.quick_start,
            'log_qso': HelpContent.log_qso,
            'fields': HelpContent.fields,
            'auto_lookup': HelpContent.auto_lookup,
            'duplicate_detection': HelpContent.duplicate_detection,
            'keyboard_shortcuts': HelpContent.keyboard_shortcuts,
            'contest_overview': HelpContent.contest_overview,
            'wes_contest': HelpContent.wes_contest,
            'sks_contest': HelpContent.sks_contest,
            'k3y_contest': HelpContent.k3y_contest,
            'contest_scoring': HelpContent.contest_scoring,
            'contest_export': HelpContent.contest_export,
            'brag_overview': HelpContent.brag_overview,
            'brag_usage': HelpContent.brag_usage,
            'brag_submission': HelpContent.brag_submission,
            'cluster_connect': HelpContent.cluster_connect,
            'cluster_commands': HelpContent.cluster_commands,
            'cluster_spots': HelpContent.cluster_spots,
            'skcc_highlighting': HelpContent.skcc_highlighting,
            'arrl_awards': HelpContent.arrl_awards,
            'skcc_awards': HelpContent.skcc_awards,
            'adif_export': HelpContent.adif_export,
            'adif_date_range': HelpContent.adif_date_range,
            'adif_skcc': HelpContent.adif_skcc,
            'adif_import': HelpContent.adif_import,
            'qrz_setup': HelpContent.qrz_setup,
            'qrz_lookup': HelpContent.qrz_lookup,
            'qrz_upload': HelpContent.qrz_upload,
            'space_weather_overview': HelpContent.space_weather_overview,
            'nasa_api': HelpContent.nasa_api,
            'propagation': HelpContent.propagation,
            'station_info': HelpContent.station_info,
            'preferences': HelpContent.preferences,
            'backup': HelpContent.backup,
            'themes': HelpContent.themes,
            'monthly_brag_report': HelpContent.monthly_brag_report,
            'qrz_issues': HelpContent.qrz_issues,
            'cluster_issues': HelpContent.cluster_issues,
            'database_issues': HelpContent.database_issues,
            'common_problems': HelpContent.common_problems,
            'keyboard_reference': HelpContent.keyboard_reference,
            'field_reference': HelpContent.field_reference,
            'cluster_commands_ref': HelpContent.cluster_commands_ref,
        }

        if topic_id in content_map:
            return content_map[topic_id]()
        else:
            return [("No help available for this topic yet.\n", 'italic')]

    @staticmethod
    def welcome():
        return [
            ("Welcome to W4GNS General Logger\n", 'title'),
            ("Version 1.0.0\n\n", 'italic'),

            ("Thank you for using W4GNS General Logger! This comprehensive amateur radio logging application provides everything you need for contact logging, contest participation, awards tracking, and more.\n\n", ()),

            ("What's Included:\n", 'heading'),
            ("• Professional contact logging with Log4OM-style interface\n", 'bullet'),
            ("• Real-time DX cluster integration with 10+ worldwide nodes\n", 'bullet'),
            ("• Complete SKCC contest support (WES, SKS, K3Y) with automatic scoring\n", 'bullet'),
            ("• SKCC Monthly Brag reporting and tracking\n", 'bullet'),
            ("• ARRL and SKCC awards progress tracking\n", 'bullet'),
            ("• QRZ.com integration for callsign lookups and logbook uploads\n", 'bullet'),
            ("• Space weather integration with NASA DONKI for propagation info\n", 'bullet'),
            ("• ADIF import/export with date range filtering\n", 'bullet'),
            ("• Google Drive automatic backups\n", 'bullet'),
            ("• Dark and light themes\n\n", 'bullet'),

            ("Quick Navigation:\n", 'heading'),
            ("New to the application? Start here:\n", ()),
            ("1. ", ()), ("Installation", 'link', 'link_installation'), (" - System requirements and setup\n", ()),
            ("2. ", ()), ("First Time Setup", 'link', 'link_first_time_setup'), (" - Configure your station\n", ()),
            ("3. ", ()), ("Quick Start Guide", 'link', 'link_quick_start'), (" - Log your first contact\n\n", ()),

            ("Feature Documentation:\n", 'heading'),
            ("• ", ()), ("Contact Logging", 'link', 'link_log_qso'), (" - Log QSOs with auto-lookup\n", ()),
            ("• ", ()), ("SKCC Contests", 'link', 'link_contest_overview'), (" - Participate in WES/SKS/K3Y\n", ()),
            ("• ", ()), ("DX Clusters", 'link', 'link_cluster_connect'), (" - Real-time DX spot monitoring\n", ()),
            ("• ", ()), ("Awards Tracking", 'link', 'link_arrl_awards'), (" - Track your progress\n", ()),
            ("• ", ()), ("ADIF Import/Export", 'link', 'link_adif_export'), (" - Share your log\n\n", ()),

            ("Need Help?\n", 'heading'),
            ("Use the search box above to find topics quickly, or browse the topic tree on the left. All major features are documented with step-by-step instructions.\n\n", ()),

            ("Tips:\n", 'heading'),
            ("• Click blue underlined text to jump to related topics\n", 'bullet'),
            ("• Press Ctrl+Enter anywhere to log a contact quickly\n", 'bullet'),
            ("• Check the Troubleshooting section if you encounter issues\n", 'bullet'),
            ("• Visit the SKCC website for contest schedules and rules\n\n", 'bullet'),

            ("73 and happy logging!\n", 'bold')
        ]

    @staticmethod
    def installation():
        return [
            ("Installation\n", 'title'),

            ("\nSystem Requirements:\n", 'heading'),
            ("Before installing, ensure your system meets these requirements:\n\n", ()),

            ("Required:\n", 'subheading'),
            ("• Python 3.12 or higher\n", 'bullet'),
            ("• tkinter GUI library (usually included with Python)\n", 'bullet'),
            ("• Internet connection (for lookups and DX clusters)\n", 'bullet'),
            ("• 50 MB free disk space\n\n", 'bullet'),

            ("Optional:\n", 'subheading'),
            ("• QRZ.com account with XML subscription (for callsign lookups)\n", 'bullet'),
            ("• NASA API key (for space weather alerts)\n", 'bullet'),
            ("• Google account (for automatic cloud backups)\n\n", 'bullet'),

            ("Installation Steps:\n", 'heading'),

            ("1. Install Python\n", 'numbered'),
            ("   If you don't have Python 3.12+, download it from python.org\n", ()),
            ("   Verify installation by opening a terminal and running:\n", ()),
            ("   python3 --version\n\n", 'code'),

            ("2. Download W4GNS General Logger\n", 'numbered'),
            ("   Clone the repository from GitHub:\n", ()),
            ("   git clone https://github.com/garyPenhook/W4GNS-General-Logger.git\n", 'code'),
            ("   cd W4GNS-General-Logger\n\n", 'code'),

            ("3. Install Dependencies\n", 'numbered'),
            ("   Install required Python packages:\n", ()),
            ("   pip install -r requirements.txt\n\n", 'code'),
            ("   This installs:\n", ()),
            ("   - requests (for POTA API and space weather)\n", 'bullet'),
            ("   - google-auth libraries (optional, for Drive backup)\n\n", 'bullet'),

            ("4. Run the Application\n", 'numbered'),
            ("   Start the logger:\n", ()),
            ("   python3 main.py\n\n", 'code'),
            ("   Or make it executable (Linux/Mac):\n", ()),
            ("   chmod +x main.py\n", 'code'),
            ("   ./main.py\n\n", 'code'),

            ("First Launch:\n", 'heading'),
            ("On first launch, the application will:\n", ()),
            ("• Create a logger.db SQLite database\n", 'bullet'),
            ("• Create a config.json settings file\n", 'bullet'),
            ("• Download SKCC roster files for awards tracking\n", 'bullet'),
            ("• Open to the Log Contacts tab\n\n", 'bullet'),

            ("Next Steps:\n", 'heading'),
            ("After installation, proceed to ", ()),
            ("First Time Setup", 'link', 'link_first_time_setup'),
            (" to configure your station information.\n\n", ()),

            ("Troubleshooting:\n", 'heading'),
            ("• If tkinter is missing, install it:\n", 'bullet'),
            ("  Ubuntu/Debian: sudo apt-get install python3-tk\n", 'code'),
            ("  macOS: Included with Python from python.org\n", 'code'),
            ("  Windows: Included with Python installer\n\n", 'code'),
            ("• If you get permission errors, run as administrator/sudo\n", 'bullet'),
            ("• Check the ", ()), ("Common Problems", 'link', 'link_common_problems'), (" section for more help\n", ())
        ]

    @staticmethod
    def first_time_setup():
        return [
            ("First Time Setup\n", 'title'),

            ("\nBefore logging your first contact, configure these essential settings:\n\n", ()),

            ("1. Station Information (Required)\n", 'heading'),
            ("Navigate to: Settings tab\n\n", 'italic'),

            ("Enter your station details:\n", ()),
            ("• ", ()), ("Callsign", 'bold'), (" - Your amateur radio call sign (e.g., W4GNS)\n", ()),
            ("• ", ()), ("Grid Square", 'bold'), (" - Your Maidenhead locator (e.g., EM73)\n", ()),
            ("• ", ()), ("Default Power", 'bold'), (" - Your typical power level in watts (e.g., 100)\n", ()),
            ("• ", ()), ("Default RST Sent/Received", 'bold'), (" - Usually 59 for phone, 599 for CW\n", ()),
            ("• ", ()), ("SKCC Number", 'bold'), (" - If you're an SKCC member (e.g., 12345C)\n\n", ()),

            ("Click ", ()), ("Save Settings", 'bold'), (" when done.\n\n", ()),

            ("2. QRZ.com Integration (Recommended)\n", 'heading'),
            ("Navigate to: Settings tab → QRZ.com Integration section\n\n", 'italic'),

            ("For automatic callsign lookups, you need:\n", ()),
            ("• QRZ.com account (free registration at qrz.com)\n", 'bullet'),
            ("• XML Subscription (paid, for XML lookups)\n", 'bullet'),
            ("• API Key (free, for logbook uploads)\n\n", 'bullet'),

            ("Configuration steps:\n", ()),
            ("1. Enter your QRZ username and password\n", 'numbered'),
            ("2. Get your API key:\n", 'numbered'),
            ("   - Log into QRZ.com\n", 'bullet'),
            ("   - Go to Logbook → Settings → API\n", 'bullet'),
            ("   - Copy your API key\n", 'bullet'),
            ("3. Paste the API key in the application\n", 'numbered'),
            ("4. Enable 'Auto-lookup' for automatic callsign info\n", 'numbered'),
            ("5. Enable 'Auto-upload' if you want contacts uploaded automatically\n", 'numbered'),
            ("6. Click 'Test QRZ Connection' to verify\n\n", 'numbered'),

            ("Without QRZ XML subscription:\n", 'italic'),
            ("You'll still get DXCC country/continent/zone lookups (built-in, no subscription needed).\n\n", ()),

            ("3. NASA Space Weather API (Optional)\n", 'heading'),
            ("Navigate to: Settings tab → NASA Space Weather API section\n\n", 'italic'),

            ("Get real-time space weather alerts:\n", ()),
            ("1. Visit https://api.nasa.gov/\n", 'numbered'),
            ("2. Click 'Get Your API Key'\n", 'numbered'),
            ("3. Register (free, instant approval)\n", 'numbered'),
            ("4. Copy your API key\n", 'numbered'),
            ("5. Paste it in the application\n", 'numbered'),
            ("6. Set cache duration (default 24 hours is good)\n\n", 'numbered'),

            ("Note: A default API key is included, but getting your own is recommended for better rate limits.\n\n", 'italic'),

            ("4. Logging Preferences\n", 'heading'),
            ("Navigate to: Settings tab → Logging Preferences section\n\n", 'italic'),

            ("Recommended settings:\n", ()),
            ("☑ ", ()), ("Auto-lookup", 'bold'), (" - Automatically lookup callsigns when entered\n", ()),
            ("☑ ", ()), ("Warn duplicates", 'bold'), (" - Show warnings for duplicate contacts\n", ()),
            ("☑ ", ()), ("Auto-fill Time OFF", 'bold'), (" - Automatically set end time when logging\n\n", ()),

            ("5. DX Cluster Settings (Optional)\n", 'heading'),
            ("Navigate to: Settings tab → DX Cluster Preferences section\n\n", 'italic'),

            ("Configure your preferred cluster:\n", ()),
            ("• Select a cluster from the dropdown (W3LPL, AE5E, etc.)\n", 'bullet'),
            ("• Enable 'Auto-connect' if you want automatic connection on startup\n", 'bullet'),
            ("• Choose which spots to show: CW, SSB, Digital\n\n", 'bullet'),

            ("6. Theme Selection\n", 'heading'),
            ("Navigate to: Settings tab → Appearance section\n\n", 'italic'),

            ("Choose your preferred theme:\n", ()),
            ("• Light theme (default)\n", 'bullet'),
            ("• Dark theme (easy on the eyes at night)\n\n", 'bullet'),

            ("Configuration Complete!\n", 'heading'),
            ("You're now ready to start logging contacts. Proceed to the ", ()),
            ("Quick Start Guide", 'link', 'link_quick_start'),
            (" to log your first QSO, or jump straight to ", ()),
            ("Logging a QSO", 'link', 'link_log_qso'),
            (" for detailed instructions.\n\n", ()),

            ("Your settings are automatically saved to config.json and will persist across sessions.\n", 'italic')
        ]

    @staticmethod
    def quick_start():
        return [
            ("Quick Start Guide\n", 'title'),

            ("\nLog your first contact in 5 easy steps!\n\n", ()),

            ("Step 1: Open the Log Contacts Tab\n", 'heading'),
            ("Click the 'Log Contacts' tab at the top of the window.\n\n", ()),

            ("Step 2: Enter the Callsign\n", 'heading'),
            ("1. Click in the Callsign field (or it's already focused)\n", 'numbered'),
            ("2. Type the callsign (e.g., W1AW)\n", 'numbered'),
            ("3. Press Tab or click outside the field\n\n", 'numbered'),

            ("What happens automatically:\n", 'subheading'),
            ("✓ Name, QTH, and grid are looked up from QRZ (if configured)\n", 'bullet'),
            ("✓ Country, continent, and zones are filled from DXCC database\n", 'bullet'),
            ("✓ Duplicate warning appears if you've worked them recently\n", 'bullet'),
            ("✓ Current UTC date/time is filled\n\n", 'bullet'),

            ("Step 3: Enter Frequency and Mode\n", 'heading'),
            ("1. Enter the frequency (e.g., 14.250)\n", 'numbered'),
            ("   - Band auto-selects (14.250 → 20m)\n\n", ()),
            ("2. Select the mode from dropdown:\n", 'numbered'),
            ("   - SSB, CW, FT8, FT4, RTTY, PSK31, etc.\n\n", ()),

            ("Step 4: Verify/Add Information\n", 'heading'),
            ("Check these auto-filled fields:\n", ()),
            ("• RST Sent/Received (defaults from settings)\n", 'bullet'),
            ("• Power (from settings)\n", 'bullet'),
            ("• Time ON (current UTC)\n\n", 'bullet'),

            ("Optionally add:\n", ()),
            ("• Name (if not auto-filled)\n", 'bullet'),
            ("• Notes or comments\n", 'bullet'),
            ("• SKCC number, POTA reference, etc.\n\n", 'bullet'),

            ("Step 5: Log the Contact\n", 'heading'),
            ("Click the ", ()), ("Log Contact", 'bold'), (" button, or press ", ()),
            ("Ctrl+Enter", 'bold'), ("\n\n", ()),

            ("What happens:\n", 'subheading'),
            ("✓ Contact is saved to the database\n", 'bullet'),
            ("✓ Contact appears in the log display below\n", 'bullet'),
            ("✓ If QRZ auto-upload is enabled, it's uploaded to QRZ\n", 'bullet'),
            ("✓ Form clears, ready for the next contact\n\n", 'bullet'),

            ("Keyboard Shortcuts:\n", 'heading'),
            ("• Ctrl+Enter - Log the contact\n", 'bullet'),
            ("• Esc - Clear the form\n", 'bullet'),
            ("• Tab - Move to next field\n\n", 'bullet'),

            ("Common Questions:\n", 'heading'),

            ("Q: What if I don't have QRZ XML subscription?\n", 'bold'),
            ("A: You'll still get country/continent/zone lookups from the built-in DXCC database. Name/QTH must be entered manually.\n\n", ()),

            ("Q: How do I edit a contact?\n", 'bold'),
            ("A: Currently, contacts must be edited in the database directly. Export to ADIF, edit, and re-import.\n\n", ()),

            ("Q: Where is my log stored?\n", 'bold'),
            ("A: In logger.db SQLite database in the application directory.\n\n", ()),

            ("Next Steps:\n", 'heading'),
            ("• Learn about all available fields: ", ()), ("QSO Fields Explained", 'link', 'link_fields'), ("\n", ()),
            ("• Configure auto-lookup: ", ()), ("Auto-Lookup Features", 'link', 'link_auto_lookup'), ("\n", ()),
            ("• Explore DX clusters: ", ()), ("DX Cluster Integration", 'link', 'link_cluster_connect'), ("\n", ()),
            ("• Try a contest: ", ()), ("SKCC Contests", 'link', 'link_contest_overview'), ("\n", ())
        ]

    # Due to length, I'll create a file with the remaining comprehensive content
    # Let me continue with the most important topics first

    @staticmethod
    def log_qso():
        return [
            ("Logging a QSO\n", 'title'),

            ("\nThe Log Contacts tab provides a professional interface for logging amateur radio contacts with automatic lookups, duplicate detection, and QRZ integration.\n\n", ()),

            ("Location: Log Contacts tab (first tab)\n\n", 'italic'),

            ("Complete Logging Workflow:\n", 'heading'),

            ("1. Callsign Entry\n", 'subheading'),
            ("• Click in the Callsign field (large, bold field at top)\n", 'bullet'),
            ("• Type the callsign in uppercase or lowercase\n", 'bullet'),
            ("• Press Tab or click outside the field to trigger lookup\n\n", 'bullet'),

            ("Automatic Actions:\n", ()),
            ("If QRZ lookup is enabled and configured:\n", ()),
            ("  ✓ Name is populated (operator's first name)\n", 'bullet'),
            ("  ✓ QTH is populated (state for US, country for DX)\n", 'bullet'),
            ("  ✓ Grid square is filled if available\n", 'bullet'),
            ("  ✓ State and county are filled (US stations)\n", 'bullet'),
            ("  ✓ CQ and ITU zones are populated\n\n", 'bullet'),

            ("Always happens (built-in DXCC lookup):\n", ()),
            ("  ✓ Country is determined from callsign prefix\n", 'bullet'),
            ("  ✓ Continent is filled (NA, EU, AS, etc.)\n", 'bullet'),
            ("  ✓ DXCC entity number is assigned\n", 'bullet'),
            ("  ✓ CQ and ITU zones are filled if known\n\n", 'bullet'),

            ("Duplicate Detection:\n", ()),
            ("If you've worked this station on the same band and mode today:\n", ()),
            ("  ⚠️ Red warning appears: 'DUPLICATE - Worked on HH:MM'\n\n", 'bullet'),

            ("2. Frequency and Band\n", 'subheading'),
            ("• Enter frequency in MHz (e.g., 14.250, 7.055, 21.350)\n", 'bullet'),
            ("• Band auto-selects from frequency:\n", 'bullet'),
            ("  - 1.8-2.0 MHz → 160m\n", ()),
            ("  - 3.5-4.0 MHz → 80m\n", ()),
            ("  - 7.0-7.3 MHz → 40m\n", ()),
            ("  - 14.0-14.35 MHz → 20m\n", ()),
            ("  - And so on...\n\n", ()),

            ("3. Mode Selection\n", 'subheading'),
            ("Select from dropdown:\n", ()),
            ("• Phone modes: SSB, AM, FM\n", 'bullet'),
            ("• CW (Morse code)\n", 'bullet'),
            ("• Digital: FT8, FT4, RTTY, PSK31, MFSK, JT65, etc.\n\n", 'bullet'),

            ("4. Date and Time\n", 'subheading'),
            ("Auto-filled with current UTC:\n", ()),
            ("• Date - YYYY-MM-DD format\n", 'bullet'),
            ("• Time ON - Automatically set to current time\n", 'bullet'),
            ("• Time OFF - Auto-filled when logging (if enabled in settings)\n\n", 'bullet'),

            ("To change:\n", ()),
            ("• Click the date/time field\n", 'bullet'),
            ("• Use the picker or type manually\n", 'bullet'),
            ("• Format must be: YYYY-MM-DD for date, HH:MM for time\n\n", 'bullet'),

            ("5. Signal Reports\n", 'subheading'),
            ("RST Sent and RST Received:\n", ()),
            ("• Auto-filled from your default settings\n", 'bullet'),
            ("• Phone: Usually 59 (5=readability, 9=signal strength)\n", 'bullet'),
            ("• CW/Digital: Usually 599 (5=readability, 9=strength, 9=tone)\n", 'bullet'),
            ("• Adjust if needed for actual conditions\n\n", 'bullet'),

            ("6. Power\n", 'subheading'),
            ("• Auto-filled from default setting\n", 'bullet'),
            ("• Enter in watts (e.g., 100, 5, 1500)\n", 'bullet'),
            ("• This is YOUR transmit power\n\n", 'bullet'),

            ("7. Optional Information\n", 'subheading'),
            ("Additional fields you can fill:\n", ()),
            ("• ", ()), ("Name", 'bold'), (" - Operator's name\n", ()),
            ("• ", ()), ("QTH", 'bold'), (" - Location/city\n", ()),
            ("• ", ()), ("Grid Square", 'bold'), (" - Maidenhead locator\n", ()),
            ("• ", ()), ("County", 'bold'), (" - For US stations\n", ()),
            ("• ", ()), ("State", 'bold'), (" - For US stations\n", ()),
            ("• ", ()), ("IOTA", 'bold'), (" - Islands On The Air reference\n", ()),
            ("• ", ()), ("SOTA", 'bold'), (" - Summits On The Air reference\n", ()),
            ("• ", ()), ("POTA", 'bold'), (" - Parks On The Air reference\n", ()),
            ("• ", ()), ("SKCC Number", 'bold'), (" - Straight Key Century Club number\n", ()),
            ("• ", ()), ("Notes", 'bold'), (" - Any comments about the contact\n\n", ()),

            ("8. Logging the Contact\n", 'subheading'),
            ("Two methods:\n", ()),
            ("• Click the ", ()), ("Log Contact", 'bold'), (" button\n", ()),
            ("• Press ", ()), ("Ctrl+Enter", 'bold'), (" (fastest!)\n\n", ()),

            ("What happens when you log:\n", ()),
            ("✓ Contact is saved to logger.db database\n", 'bullet'),
            ("✓ Contact appears in the log table at bottom\n", 'bullet'),
            ("✓ If QRZ auto-upload is enabled, contact is uploaded\n", 'bullet'),
            ("✓ Form clears for next contact\n", 'bullet'),
            ("✓ Callsign field gets focus\n\n", 'bullet'),

            ("Keyboard Shortcuts:\n", 'heading'),
            ("• ", ()), ("Ctrl+Enter", 'bold'), (" - Log the contact\n", ()),
            ("• ", ()), ("Esc", 'bold'), (" - Clear all fields\n", ()),
            ("• ", ()), ("Tab", 'bold'), (" - Move to next field\n", ()),
            ("• ", ()), ("Shift+Tab", 'bold'), (" - Move to previous field\n\n", ()),

            ("Manual QRZ Upload:\n", 'heading'),
            ("If auto-upload is disabled:\n", ()),
            ("• Click the ", ()), ("Upload to QRZ", 'bold'), (" button after logging\n", ()),
            ("• Uploads the most recent contact\n", ()),
            ("• Requires QRZ API key in settings\n\n", ()),

            ("Tips and Best Practices:\n", 'heading'),
            ("• Set your defaults in Settings to minimize typing\n", 'bullet'),
            ("• Use Tab to move between fields (faster than mouse)\n", 'bullet'),
            ("• Enable auto-lookup for automatic callsign information\n", 'bullet'),
            ("• Pay attention to duplicate warnings\n", 'bullet'),
            ("• Double-check UTC time if logging after the fact\n", 'bullet'),
            ("• Use the Notes field for QSL info or special circumstances\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QSO Fields Explained", 'link', 'link_fields'), (" - Details on all 25+ fields\n", ()),
            ("• ", ()), ("Auto-Lookup Features", 'link', 'link_auto_lookup'), (" - How automatic lookups work\n", ()),
            ("• ", ()), ("Duplicate Detection", 'link', 'link_duplicate_detection'), (" - Avoiding duplicate contacts\n", ()),
            ("• ", ()), ("QRZ.com Integration", 'link', 'link_qrz_setup'), (" - Setup and configuration\n", ())
        ]

    # I'll add placeholder methods for the remaining topics to keep the file from being too long
    # These can be expanded further as needed

    @staticmethod
    def fields():
        return [
            ("QSO Fields Explained\n", 'title'),
            ("\nThe application supports 25+ fields for comprehensive contact logging. Here's what each field means:\n\n", ()),

            ("Required Fields:\n", 'heading'),
            ("• Callsign - Station you contacted\n", 'bullet'),
            ("• Date - Date of contact (UTC)\n", 'bullet'),
            ("• Time ON - Start time (UTC)\n", 'bullet'),
            ("• Frequency - Operating frequency in MHz\n", 'bullet'),
            ("• Band - Amateur radio band (auto-filled)\n", 'bullet'),
            ("• Mode - Operating mode (SSB, CW, FT8, etc.)\n\n", 'bullet'),

            ("Signal Reports:\n", 'heading'),
            ("• RST Sent - Signal report you sent (e.g., 599)\n", 'bullet'),
            ("• RST Received - Signal report you received\n\n", 'bullet'),

            ("Station Information:\n", 'heading'),
            ("• Name - Operator's name\n", 'bullet'),
            ("• QTH - Location (city/state/country)\n", 'bullet'),
            ("• Grid Square - Maidenhead locator (e.g., FN20)\n", 'bullet'),
            ("• County - US county\n", 'bullet'),
            ("• State - US state or province\n", 'bullet'),
            ("• Country - DXCC country name\n", 'bullet'),
            ("• Continent - NA, EU, AS, AF, OC, SA, AN\n\n", 'bullet'),

            ("Location Data:\n", 'heading'),
            ("• CQ Zone - CQ Magazine zone (1-40)\n", 'bullet'),
            ("• ITU Zone - ITU zone (1-90)\n", 'bullet'),
            ("• DXCC - DXCC entity number\n\n", 'bullet'),

            ("Awards and Activities:\n", 'heading'),
            ("• IOTA - Islands On The Air reference\n", 'bullet'),
            ("• SOTA - Summits On The Air reference\n", 'bullet'),
            ("• POTA - Parks On The Air reference\n", 'bullet'),
            ("• SKCC Number - Straight Key Century Club number\n\n", 'bullet'),

            ("Technical:\n", 'heading'),
            ("• Power - Your transmit power in watts\n", 'bullet'),
            ("• Time OFF - End time of contact\n", 'bullet'),
            ("• Notes/Comments - Any additional information\n", 'bullet'),
        ]

    @staticmethod
    def auto_lookup():
        return [
            ("Auto-Lookup Features\n", 'title'),
            ("\nThe application provides two levels of automatic callsign lookups:\n\n", ()),

            ("1. DXCC Prefix Lookup (Always Available)\n", 'heading'),
            ("Built into the application, no subscription needed:\n", ()),
            ("• Country name\n", 'bullet'),
            ("• Continent\n", 'bullet'),
            ("• CQ Zone\n", 'bullet'),
            ("• ITU Zone\n", 'bullet'),
            ("• DXCC entity number\n\n", 'bullet'),

            ("Covers 40+ major DXCC entities including:\n", ()),
            ("• All US call areas (W/K/N 1-0)\n", 'bullet'),
            ("• Canada (VE/VA)\n", 'bullet'),
            ("• Europe (G, DL, F, etc.)\n", 'bullet'),
            ("• Asia, Oceania, South America\n", 'bullet'),
            ("• Special prefixes and portable operations\n\n", 'bullet'),

            ("2. QRZ.com XML Lookup (Requires Subscription)\n", 'heading'),
            ("With QRZ XML subscription, you also get:\n", ()),
            ("• Operator's name\n", 'bullet'),
            ("• QTH (location)\n", 'bullet'),
            ("• Grid square\n", 'bullet'),
            ("• State/county (US stations)\n", 'bullet'),
            ("• Email address\n", 'bullet'),
            ("• License class\n\n", 'bullet'),

            ("Setup: See ", ()), ("QRZ.com Integration", 'link', 'link_qrz_setup'), ("\n\n", ()),

            ("How It Works:\n", 'heading'),
            ("1. Enter a callsign\n", 'numbered'),
            ("2. Press Tab or click outside the field\n", 'numbered'),
            ("3. DXCC lookup happens instantly (offline)\n", 'numbered'),
            ("4. If QRZ is configured, XML lookup happens (online)\n", 'numbered'),
            ("5. All available fields are populated\n\n", 'numbered'),

            ("Enable/Disable:\n", 'heading'),
            ("Settings → Logging Preferences → Auto-lookup checkbox\n\n", ()),

            ("Manual Lookup:\n", 'heading'),
            ("Even with auto-lookup disabled, you can manually lookup:\n", ()),
            ("• Click the 'Lookup' button next to callsign field\n", ()),
        ]

    @staticmethod
    def duplicate_detection():
        return [
            ("Duplicate Detection\n", 'title'),
            ("\nPrevents accidentally logging the same contact twice.\n\n", ()),

            ("How It Works:\n", 'heading'),
            ("The app checks for duplicates when you enter a callsign based on:\n", ()),
            ("• Same callsign\n", 'bullet'),
            ("• Same band\n", 'bullet'),
            ("• Same mode\n", 'bullet'),
            ("• Same day (UTC)\n\n", 'bullet'),

            ("Warning Display:\n", 'heading'),
            ("If a duplicate is detected:\n", ()),
            ("• Red text appears: '⚠️ DUPLICATE - Worked on HH:MM'\n", 'bullet'),
            ("• Shows the time of the previous contact\n", 'bullet'),
            ("• You can still log if intentional (confirmation required)\n\n", 'bullet'),

            ("Different Band/Mode:\n", 'heading'),
            ("Working the same station on a different band or mode is NOT a duplicate:\n", ()),
            ("• W1AW on 20m SSB\n", 'bullet'),
            ("• W1AW on 40m CW\n", 'bullet'),
            ("These are two separate, valid contacts.\n\n", ()),

            ("Enable/Disable:\n", 'heading'),
            ("Settings → Logging Preferences → Warn duplicates checkbox\n", ()),
        ]

    @staticmethod
    def keyboard_shortcuts():
        return [
            ("Keyboard Shortcuts\n", 'title'),
            ("\nSpeed up your logging with these keyboard shortcuts:\n\n", ()),

            ("Contact Logging:\n", 'heading'),
            ("• Ctrl+Enter - Log the contact (works anywhere)\n", 'bullet'),
            ("• Esc - Clear the form\n", 'bullet'),
            ("• Tab - Next field\n", 'bullet'),
            ("• Shift+Tab - Previous field\n\n", 'bullet'),

            ("Navigation:\n", 'heading'),
            ("• Tab/Shift+Tab - Move between tabs\n", 'bullet'),
            ("• Arrow keys - Navigate within dropdowns\n\n", 'bullet'),

            ("See ", ()), ("Keyboard Reference", 'link', 'link_keyboard_reference'), (" for complete list.\n", ())
        ]

    # Continue with contest-related content...
    @staticmethod
    def contest_overview():
        return [
            ("SKCC Contest Overview\n", 'title'),
            ("\nComprehensive support for all SKCC contests with automatic scoring, duplicate checking, and export.\n\n", ()),

            ("Location: Contest tab\n\n", 'italic'),

            ("Supported Contests:\n", 'heading'),
            ("• ", ()), ("WES - Weekend Sprintathon", 'link', 'link_wes_contest'), (" - Monthly weekend events\n", ()),
            ("• ", ()), ("SKS - Weekday Sprint", 'link', 'link_sks_contest'), (" - 4th Wednesday, 2 hours\n", ()),
            ("• ", ()), ("K3Y - Straight Key Month", 'link', 'link_k3y_contest'), (" - January celebration\n\n", ()),

            ("Key Features:\n", 'heading'),
            ("✓ Real-time scoring with live updates\n", 'bullet'),
            ("✓ Automatic multiplier tracking (states/provinces/countries)\n", 'bullet'),
            ("✓ Per-band duplicate detection\n", 'bullet'),
            ("✓ QRZ and SKCC roster integration\n", 'bullet'),
            ("✓ Configurable bonus values (updated monthly)\n", 'bullet'),
            ("✓ Rate calculator (QSOs per hour)\n", 'bullet'),
            ("✓ Complete score breakdown\n", 'bullet'),
            ("✓ One-click SKCC export\n\n", 'bullet'),

            ("Automatic Bonus Tracking:\n", 'heading'),
            ("The app automatically detects and scores:\n", ()),
            ("• C/T/S achievement bonuses (Centurion/Tribune/Senator)\n", 'bullet'),
            ("• KS1KCC special station (WES/K3Y)\n", 'bullet'),
            ("• Designated member (SKS, rotates monthly)\n", 'bullet'),
            ("• Monthly theme bonuses (WES, 12 different themes)\n\n", 'bullet'),

            ("Basic Contest Workflow:\n", 'heading'),
            ("1. Go to Contest tab\n", 'numbered'),
            ("2. Select contest type (WES, SKS, or K3Y)\n", 'numbered'),
            ("3. Update bonus values if needed (monthly)\n", 'numbered'),
            ("4. Click 'Start Contest'\n", 'numbered'),
            ("5. Log QSOs - scoring updates automatically\n", 'numbered'),
            ("6. Monitor score and rate in real-time\n", 'numbered'),
            ("7. Click 'End Contest' when finished\n", 'numbered'),
            ("8. Export for SKCC submission\n\n", 'numbered'),

            ("Learn More:\n", 'heading'),
            ("• ", ()), ("WES Contest Details", 'link', 'link_wes_contest'), ("\n", ()),
            ("• ", ()), ("SKS Contest Details", 'link', 'link_sks_contest'), ("\n", ()),
            ("• ", ()), ("K3Y Contest Details", 'link', 'link_k3y_contest'), ("\n", ()),
            ("• ", ()), ("Scoring and Bonuses", 'link', 'link_contest_scoring'), ("\n", ()),
            ("• ", ()), ("Exporting Results", 'link', 'link_contest_export'), ("\n", ()),
        ]

    # Add remaining stub methods to prevent errors
    @staticmethod
    def wes_contest():
        return [
            ("WES - Weekend Sprintathon\n", 'title'),
            ("\nThe Weekend Sprintathon (WES) is SKCC's monthly weekend contest celebrating straight key operation.\n\n", ()),

            ("Schedule:\n", 'heading'),
            ("• Monthly event (check skccgroup.com for dates)\n", 'bullet'),
            ("• Typically runs Friday-Sunday\n", 'bullet'),
            ("• 48-hour operating window\n", 'bullet'),
            ("• CW (Morse code) only\n", 'bullet'),
            ("• Mechanical keys only (straight key, bug, sideswiper)\n\n", 'bullet'),

            ("Objective:\n", 'heading'),
            ("Work as many SKCC members as possible on as many bands as possible to maximize your score.\n\n", ()),

            ("Scoring Formula:\n", 'heading'),
            ("Score = (QSO Points × Multipliers) + Bonuses\n\n", 'bold'),

            ("• QSO Points: 2 points per SKCC member contact\n", 'bullet'),
            ("• Multipliers: Unique states/provinces/countries worked\n", 'bullet'),
            ("• Bonuses: C/T/S achievements, KS1KCC station, monthly theme\n\n", 'bullet'),

            ("Monthly Themes (Rotating):\n", 'heading'),
            ("WES features a different theme each month with bonus points:\n", ()),
            ("• January - Winter Bands (160m/80m)\n", 'bullet'),
            ("• February - Boat Anchors (vintage rigs)\n", 'bullet'),
            ("• March - Bug/Cootie (semi-automatic keys)\n", 'bullet'),
            ("• April - Easter Egg Hunt\n", 'bullet'),
            ("• May - First Year Members\n", 'bullet'),
            ("• June - Old Timers/Summer Bands (10m/15m/20m)\n", 'bullet'),
            ("• July - 13 Colonies (special calls)\n", 'bullet'),
            ("• August - Home Brew Key (homemade keys)\n", 'bullet'),
            ("• September - Club Calls\n", 'bullet'),
            ("• October - TKA (Triple Key Award holders)\n", 'bullet'),
            ("• November - Veterans\n", 'bullet'),
            ("• December - Reindeer\n\n", 'bullet'),

            ("Bonus Points:\n", 'heading'),
            ("Values change monthly - check skccgroup.com:\n", ()),
            ("• Centurion (C): Typically 5 points\n", 'bullet'),
            ("• Tribune (T): Typically 10 points\n", 'bullet'),
            ("• Senator (S): Typically 15 points\n", 'bullet'),
            ("• KS1KCC: 25 points per band (special station)\n", 'bullet'),
            ("• Monthly Theme: Varies by month\n\n", 'bullet'),

            ("WES Workflow in App:\n", 'heading'),
            ("1. Go to Contest tab\n", 'numbered'),
            ("2. Select 'WES - Weekend Sprintathon'\n", 'numbered'),
            ("3. Update bonus values from SKCC website\n", 'numbered'),
            ("4. Select current monthly theme from dropdown\n", 'numbered'),
            ("5. Click 'Start Contest'\n", 'numbered'),
            ("6. Log QSOs - duplicates prevented per band\n", 'numbered'),
            ("7. Watch score and rate update in real-time\n", 'numbered'),
            ("8. Click 'End Contest' when finished\n", 'numbered'),
            ("9. Export for SKCC submission\n\n", 'numbered'),

            ("Exchange:\n", 'heading'),
            ("Send: RST + State/Province + SKCC# or SPF\n", ()),
            ("Receive: Same information from other station\n\n", ()),

            ("Duplicates:\n", 'heading'),
            ("You can work the same station on different bands:\n", ()),
            ("• K1ABC on 40m = Valid\n", 'bullet'),
            ("• K1ABC on 20m = Valid (different band)\n", 'bullet'),
            ("• K1ABC on 40m again = DUPE (same band)\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Contest Scoring", 'link', 'link_contest_scoring'), (" - Detailed scoring breakdown\n", ()),
            ("• ", ()), ("Exporting Results", 'link', 'link_contest_export'), (" - Submit to SKCC\n", ()),
            ("• ", ()), ("Contest Overview", 'link', 'link_contest_overview'), (" - All contest features\n", ())
        ]

    @staticmethod
    def sks_contest():
        return [
            ("SKS - Weekday Sprint\n", 'title'),
            ("\nThe Weekday Sprint (SKS) is a fast-paced 2-hour SKCC contest held monthly on Wednesday evenings.\n\n", ()),

            ("Schedule:\n", 'heading'),
            ("• 4th Wednesday of every month\n", 'bullet'),
            ("• Time: 0000-0200 UTC (evening US time on Tuesday)\n", 'bullet'),
            ("• Duration: 2 hours\n", 'bullet'),
            ("• CW (Morse code) only\n", 'bullet'),
            ("• Mechanical keys only (straight key, bug, sideswiper)\n\n", 'bullet'),

            ("Time Zone Conversion Examples:\n", 'subheading'),
            ("0000-0200 UTC translates to:\n", ()),
            ("• US Eastern: 7pm-9pm (Tuesday evening)\n", 'bullet'),
            ("• US Central: 6pm-8pm (Tuesday evening)\n", 'bullet'),
            ("• US Mountain: 5pm-7pm (Tuesday evening)\n", 'bullet'),
            ("• US Pacific: 4pm-6pm (Tuesday evening)\n\n", 'bullet'),

            ("Objective:\n", 'heading'),
            ("Work as many SKCC members as possible in 2 hours to maximize your score. Speed and efficiency are key!\n\n", ()),

            ("Scoring Formula:\n", 'heading'),
            ("Score = (QSO Points × Multipliers) + Bonuses\n\n", 'bold'),

            ("• QSO Points: 2 points per SKCC member contact\n", 'bullet'),
            ("• Multipliers: Unique states/provinces/countries worked\n", 'bullet'),
            ("• Bonuses: C/T/S achievements, Designated Member\n\n", 'bullet'),

            ("Designated Member Bonus:\n", 'heading'),
            ("SKCC designates one member each month as a bonus station:\n", ()),
            ("• Typically worth 25 points PER BAND\n", 'bullet'),
            ("• Changes monthly - check SKCC website\n", 'bullet'),
            ("• Working on multiple bands multiplies the bonus\n", 'bullet'),
            ("• Configure in Contest tab → SKS Member field\n\n", 'bullet'),

            ("Example: Work designated member on 3 bands = 75 bonus points!\n\n", 'italic'),

            ("Bonus Points (Check SKCC website monthly):\n", 'heading'),
            ("• Centurion (C): Typically 5 points\n", 'bullet'),
            ("• Tribune (T): Typically 10 points\n", 'bullet'),
            ("• Senator (S): Typically 15 points\n", 'bullet'),
            ("• Designated Member: 25 points per band\n\n", 'bullet'),

            ("SKS Workflow in App:\n", 'heading'),
            ("1. Go to Contest tab\n", 'numbered'),
            ("2. Select 'SKS - Weekday Sprint'\n", 'numbered'),
            ("3. Update bonus values from SKCC website\n", 'numbered'),
            ("4. Enter designated member callsign\n", 'numbered'),
            ("5. Click 'Start Contest' at 0000 UTC\n", 'numbered'),
            ("6. Log QSOs rapidly - duplicates prevented per band\n", 'numbered'),
            ("7. Monitor your rate (QSOs per hour)\n", 'numbered'),
            ("8. Click 'End Contest' at 0200 UTC\n", 'numbered'),
            ("9. Export for SKCC submission\n\n", 'numbered'),

            ("Exchange:\n", 'heading'),
            ("Send: RST + State/Province + SKCC# or SPF\n", ()),
            ("Receive: Same information from other station\n\n", ()),

            ("Duplicates:\n", 'heading'),
            ("Same as WES - can work same station on different bands:\n", ()),
            ("• N1ABC on 40m = Valid\n", 'bullet'),
            ("• N1ABC on 20m = Valid (different band)\n", 'bullet'),
            ("• N1ABC on 40m again = DUPE\n\n", 'bullet'),

            ("Tips for SKS Success:\n", 'heading'),
            ("• Pre-tune to popular SKCC frequencies (3.550, 7.055, 14.050)\n", 'bullet'),
            ("• Keep exchanges brief - it's a sprint!\n", 'bullet'),
            ("• Send at comfortable speed (12-18 WPM typical)\n", 'bullet'),
            ("• Listen for the designated member on multiple bands\n", 'bullet'),
            ("• Watch your QSO rate - aim for 20+ QSOs/hour\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Contest Scoring", 'link', 'link_contest_scoring'), (" - Detailed scoring breakdown\n", ()),
            ("• ", ()), ("Exporting Results", 'link', 'link_contest_export'), (" - Submit to SKCC\n", ()),
            ("• ", ()), ("Contest Overview", 'link', 'link_contest_overview'), (" - All contest features\n", ())
        ]

    @staticmethod
    def k3y_contest():
        return [
            ("K3Y - Straight Key Month\n", 'title'),
            ("\nK3Y is SKCC's annual January celebration of straight key operation, honoring the legacy of hand-sent Morse code.\n\n", ()),

            ("Schedule:\n", 'heading'),
            ("• Entire month of January (January 1-31)\n", 'bullet'),
            ("• 31 days to participate\n", 'bullet'),
            ("• CW (Morse code) only\n", 'bullet'),
            ("• Straight keys ONLY (no bugs or sidesipers for K3Y)\n\n", 'bullet'),

            ("Special Significance:\n", 'heading'),
            ("K3Y celebrates the traditional straight key, the oldest and most basic form of CW operation. SKCC considers it the 'purist' form of hand-sent Morse.\n\n", ()),

            ("Objective:\n", 'heading'),
            ("Work as many SKCC members as possible throughout January using only a straight key.\n\n", ()),

            ("Scoring Formula:\n", 'heading'),
            ("Score = (QSO Points × Multipliers) + Bonuses\n\n", 'bold'),

            ("• QSO Points: 2 points per SKCC member contact\n", 'bullet'),
            ("• Multipliers: Unique states/provinces/countries worked\n", 'bullet'),
            ("• Bonuses: C/T/S achievements, KS1KCC station\n\n", 'bullet'),

            ("KS1KCC Special Station:\n", 'heading'),
            ("The KS1KCC special event station operates during K3Y:\n", ()),
            ("• Bonus: 25 points per band worked\n", 'bullet'),
            ("• Listen for KS1KCC on popular bands\n", 'bullet'),
            ("• Working multiple bands multiplies the bonus\n", 'bullet'),
            ("• Example: KS1KCC on 40m, 20m, 15m = 75 points\n\n", 'bullet'),

            ("Bonus Points (Check SKCC website):\n", 'heading'),
            ("• Centurion (C): Typically 5 points\n", 'bullet'),
            ("• Tribune (T): Typically 10 points\n", 'bullet'),
            ("• Senator (S): Typically 15 points\n", 'bullet'),
            ("• KS1KCC: 25 points per band\n\n", 'bullet'),

            ("K3Y Workflow in App:\n", 'heading'),
            ("1. Go to Contest tab\n", 'numbered'),
            ("2. Select 'K3Y - Straight Key Month'\n", 'numbered'),
            ("3. Update bonus values from SKCC website\n", 'numbered'),
            ("4. Click 'Start Contest' (anytime in January)\n", 'numbered'),
            ("5. Log QSOs throughout the month\n", 'numbered'),
            ("6. Watch for KS1KCC on multiple bands\n", 'numbered'),
            ("7. Track your score and multipliers\n", 'numbered'),
            ("8. Click 'End Contest' at end of January\n", 'numbered'),
            ("9. Export for SKCC submission\n\n", 'numbered'),

            ("Exchange:\n", 'heading'),
            ("Send: RST + State/Province + SKCC# or SPF\n", ()),
            ("Receive: Same information from other station\n\n", ()),

            ("Duplicates:\n", 'heading'),
            ("Same as WES/SKS - can work same station on different bands:\n", ()),
            ("• W2XYZ on 40m = Valid\n", 'bullet'),
            ("• W2XYZ on 20m = Valid (different band)\n", 'bullet'),
            ("• W2XYZ on 40m again = DUPE\n\n", 'bullet'),

            ("Important Notes:\n", 'heading'),
            ("• ONLY straight keys are valid for K3Y (bugs/sidesipers not allowed)\n", 'bullet'),
            ("• Record your key type in Notes field for proof\n", 'bullet'),
            ("• Entire month gives more time for casual operation\n", 'bullet'),
            ("• Focus on quality contacts and clean sending\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Contest Scoring", 'link', 'link_contest_scoring'), (" - Detailed scoring breakdown\n", ()),
            ("• ", ()), ("Exporting Results", 'link', 'link_contest_export'), (" - Submit to SKCC\n", ()),
            ("• ", ()), ("Contest Overview", 'link', 'link_contest_overview'), (" - All contest features\n", ())
        ]

    @staticmethod
    def contest_scoring():
        return [
            ("Contest Scoring and Bonuses\n", 'title'),
            ("\nDetailed breakdown of how SKCC contest scores are calculated.\n\n", ()),

            ("Scoring Formula:\n", 'heading'),
            ("Final Score = (QSO Points × Multipliers) + All Bonuses\n\n", 'bold'),

            ("Component 1: QSO Points\n", 'heading'),
            ("• 2 points per SKCC member contact\n", 'bullet'),
            ("• Non-SKCC stations: 0 points (can still be multipliers)\n", 'bullet'),
            ("• Example: 50 SKCC contacts = 100 QSO points\n\n", 'bullet'),

            ("Component 2: Multipliers\n", 'heading'),
            ("Unique states, provinces, and countries worked:\n", ()),
            ("• Each unique US state = 1 multiplier\n", 'bullet'),
            ("• Each unique Canadian province/territory = 1 multiplier\n", 'bullet'),
            ("• Each unique DX country = 1 multiplier\n", 'bullet'),
            ("• Work same state on different bands = still 1 multiplier\n", 'bullet'),
            ("• Example: 25 states/provinces/countries = ×25\n\n", 'bullet'),

            ("Component 3: Achievement Bonuses\n", 'heading'),
            ("Earned when working SKCC members with awards:\n\n", ()),

            ("Centurion (C) Bonus:\n", 'subheading'),
            ("• Contact has 'C' suffix (e.g., 12345C)\n", 'bullet'),
            ("• Typically 5 points per contact\n", 'bullet'),
            ("• Only counted once per unique callsign\n", 'bullet'),
            ("• Example: Work 10 different Centurions = 50 bonus points\n\n", 'bullet'),

            ("Tribune (T) Bonus:\n", 'subheading'),
            ("• Contact has 'T' suffix (e.g., 12345T)\n", 'bullet'),
            ("• Typically 10 points per contact\n", 'bullet'),
            ("• Only counted once per unique callsign\n", 'bullet'),
            ("• Example: Work 5 different Tribunes = 50 bonus points\n\n", 'bullet'),

            ("Senator (S) Bonus:\n", 'subheading'),
            ("• Contact has 'S' suffix (e.g., 12345S)\n", 'bullet'),
            ("• Typically 15 points per contact\n", 'bullet'),
            ("• Only counted once per unique callsign\n", 'bullet'),
            ("• Example: Work 3 different Senators = 45 bonus points\n\n", 'bullet'),

            ("Component 4: Special Station Bonuses\n", 'heading'),

            ("KS1KCC Bonus (WES/K3Y):\n", 'subheading'),
            ("• Work the KS1KCC special event station\n", 'bullet'),
            ("• Typically 25 points PER BAND\n", 'bullet'),
            ("• Counted separately for each band\n", 'bullet'),
            ("• Example: KS1KCC on 40m, 20m, 15m = 75 points\n\n", 'bullet'),

            ("Designated Member Bonus (SKS Only):\n", 'subheading'),
            ("• Work the monthly designated member\n", 'bullet'),
            ("• Typically 25 points PER BAND\n", 'bullet'),
            ("• Changes monthly - check SKCC website\n", 'bullet'),
            ("• Configure in Contest tab → SKS Member field\n\n", 'bullet'),

            ("Component 5: Monthly Theme Bonus (WES Only)\n", 'heading'),
            ("Earn bonus points by matching the monthly theme:\n", ()),
            ("• Theme changes each month\n", 'bullet'),
            ("• Bonus values vary (typically 5-10 points)\n", 'bullet'),
            ("• Select theme from dropdown in Contest tab\n", 'bullet'),
            ("• Examples:\n", 'bullet'),
            ("  - January: Use 160m or 80m (Winter Bands)\n", ()),
            ("  - March: Use bug or cootie key\n", ()),
            ("  - June: Use 10m, 15m, or 20m (Summer Bands)\n\n", ()),

            ("Scoring Example (WES):\n", 'heading'),
            ("50 QSO points × 25 multipliers = 1,250 base score\n", ()),
            ("+ 5 Centurions × 5 pts = 25\n", ()),
            ("+ 3 Tribunes × 10 pts = 30\n", ()),
            ("+ 1 Senator × 15 pts = 15\n", ()),
            ("+ KS1KCC on 3 bands × 25 pts = 75\n", ()),
            ("+ 10 theme bonus QSOs × 5 pts = 50\n", ()),
            ("Total Score = 1,445 points\n\n", 'bold'),

            ("Live Score Display:\n", 'heading'),
            ("The app shows real-time scoring as you log:\n", ()),
            ("• QSO count and points\n", 'bullet'),
            ("• Multiplier count\n", 'bullet'),
            ("• Each bonus category breakdown\n", 'bullet'),
            ("• Current total score\n", 'bullet'),
            ("• QSO rate (per hour)\n\n", 'bullet'),

            ("Important Notes:\n", 'heading'),
            ("• Bonus values change monthly - always check SKCC website\n", 'bullet'),
            ("• Update values in Contest tab before starting\n", 'bullet'),
            ("• App validates SKCC numbers against roster\n", 'bullet'),
            ("• Achievement bonuses (C/T/S) counted once per unique call\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("WES Contest", 'link', 'link_wes_contest'), ("\n", ()),
            ("• ", ()), ("SKS Contest", 'link', 'link_sks_contest'), ("\n", ()),
            ("• ", ()), ("K3Y Contest", 'link', 'link_k3y_contest'), ("\n", ())
        ]

    @staticmethod
    def contest_export():
        return [
            ("Exporting Contest Results\n", 'title'),
            ("\nExport your contest log for submission to SKCC in the proper format.\n\n", ()),

            ("Location: Contest tab → Export for SKCC button\n\n", 'italic'),

            ("Export Process:\n", 'heading'),
            ("1. Complete your contest operating\n", 'numbered'),
            ("2. Click 'End Contest' button\n", 'numbered'),
            ("3. Click 'Export for SKCC' button\n", 'numbered'),
            ("4. Choose save location and filename\n", 'numbered'),
            ("5. Submit the file to SKCC website\n\n", 'numbered'),

            ("Export File Contents:\n", 'heading'),
            ("The exported file includes:\n\n", ()),

            ("Header Section:\n", 'subheading'),
            ("• Your callsign\n", 'bullet'),
            ("• Contest type (WES/SKS/K3Y)\n", 'bullet'),
            ("• Contest date/time period\n", 'bullet'),
            ("• Score summary with complete breakdown\n", 'bullet'),
            ("• QSO count, multipliers, and all bonuses\n\n", 'bullet'),

            ("QSO Section:\n", 'subheading'),
            ("Each contact line includes:\n", ()),
            ("• Date and time (UTC)\n", 'bullet'),
            ("• Callsign worked\n", 'bullet'),
            ("• Frequency and band\n", 'bullet'),
            ("• RST sent and received\n", 'bullet'),
            ("• SKCC number received\n", 'bullet'),
            ("• State/province/country\n", 'bullet'),
            ("• Any bonuses earned (C/T/S, theme, etc.)\n\n", 'bullet'),

            ("Score Summary Section:\n", 'subheading'),
            ("Complete breakdown showing:\n", ()),
            ("• Total QSOs and QSO points\n", 'bullet'),
            ("• Multipliers (with list of states/provinces/countries)\n", 'bullet'),
            ("• Centurion bonuses (count and points)\n", 'bullet'),
            ("• Tribune bonuses (count and points)\n", 'bullet'),
            ("• Senator bonuses (count and points)\n", 'bullet'),
            ("• KS1KCC bonuses (bands and points)\n", 'bullet'),
            ("• Designated member bonuses (SKS)\n", 'bullet'),
            ("• Monthly theme bonuses (WES)\n", 'bullet'),
            ("• Final total score\n\n", 'bullet'),

            ("File Format:\n", 'heading'),
            ("• Plain text format\n", 'bullet'),
            ("• Human-readable\n", 'bullet'),
            ("• Ready for SKCC submission\n", 'bullet'),
            ("• Can be opened in any text editor\n\n", 'bullet'),

            ("Submitting to SKCC:\n", 'heading'),
            ("1. Visit skccgroup.com\n", 'numbered'),
            ("2. Log into your account\n", 'numbered'),
            ("3. Navigate to contest results submission\n", 'numbered'),
            ("4. Upload or paste your exported file\n", 'numbered'),
            ("5. Verify your score matches\n", 'numbered'),
            ("6. Submit!\n\n", 'numbered'),

            ("Alternative Export:\n", 'heading'),
            ("You can also export contest QSOs as ADIF:\n", ()),
            ("1. Note the contest start/end times\n", 'numbered'),
            ("2. Go to File → Export by Date/Time Range\n", 'numbered'),
            ("3. Enter contest time period\n", 'numbered'),
            ("4. Export in ADIF format\n", 'numbered'),
            ("5. Import into other logging software if needed\n\n", 'numbered'),

            ("Tips:\n", 'heading'),
            ("• Export immediately after contest while fresh\n", 'bullet'),
            ("• Keep a copy of your export file for records\n", 'bullet'),
            ("• Verify score matches your final display\n", 'bullet'),
            ("• Submit within SKCC deadline (usually 1 week)\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Contest Scoring", 'link', 'link_contest_scoring'), (" - How scores are calculated\n", ()),
            ("• ", ()), ("ADIF Export", 'link', 'link_adif_export'), (" - Alternative export format\n", ()),
            ("• ", ()), ("Contest Overview", 'link', 'link_contest_overview'), (" - All contest features\n", ())
        ]

    @staticmethod
    def brag_overview():
        return [
            ("SKCC Monthly Brag\n", 'title'),
            ("\nThe SKCC Monthly Brag is a year-round activity where you work unique SKCC members each month and report your totals.\n\n", ()),

            ("What is Monthly Brag?\n", 'heading'),
            ("A friendly monthly competition to work as many different SKCC members as possible during regular (non-contest) operation.\n\n", ()),

            ("Objective:\n", 'heading'),
            ("• Work unique SKCC members during the calendar month\n", 'bullet'),
            ("• Contest QSOs (WES/SKS/K3Y) are excluded\n", 'bullet'),
            ("• Only regular contacts count\n", 'bullet'),
            ("• Report your count to SKCC monthly\n\n", 'bullet'),

            ("Scoring:\n", 'heading'),
            ("Simple and straightforward:\n", ()),
            ("• Base Score: Count of unique SKCC members worked\n", 'bullet'),
            ("• Bonus Member: +25 points if you work the monthly bonus member\n", 'bullet'),
            ("• Final Score: Unique Members + Bonus (if applicable)\n\n", 'bullet'),

            ("Example:\n", 'italic'),
            ("Work 42 unique SKCC members in March\n", ()),
            ("Work the bonus member (N4ABC)\n", ()),
            ("Total Score: 42 + 25 = 67 points\n\n", ()),

            ("Contest Exclusion:\n", 'heading'),
            ("The app automatically excludes:\n", ()),
            ("• All WES Weekend Sprintathon contacts\n", 'bullet'),
            ("• All SKS Weekday Sprint contacts\n", 'bullet'),
            ("• All K3Y Straight Key Month contacts\n", 'bullet'),
            ("• Only regular operating contacts are counted\n\n", 'bullet'),

            ("This ensures fair competition and rewards regular activity.\n\n", 'italic'),

            ("Bonus Member:\n", 'heading'),
            ("SKCC designates one member each month as a bonus:\n", ()),
            ("• Changes monthly - check SKCC website\n", 'bullet'),
            ("• Worth 25 bonus points if worked\n", 'bullet'),
            ("• Configure in Settings or Monthly Brag dialog\n", 'bullet'),
            ("• Must work during the calendar month\n\n", 'bullet'),

            ("Reporting Period:\n", 'heading'),
            ("• Reports cover a calendar month (1st-last day)\n", 'bullet'),
            ("• Submit by SKCC deadline (usually first week of next month)\n", 'bullet'),
            ("• Can generate reports for any past month\n", 'bullet'),
            ("• Great way to track your SKCC activity\n\n", 'bullet'),

            ("Why Participate?\n", 'heading'),
            ("• Encourages regular SKCC activity year-round\n", 'bullet'),
            ("• Friendly monthly competition\n", 'bullet'),
            ("• Separate from high-pressure contests\n", 'bullet'),
            ("• Works toward your Centurion award progress\n", 'bullet'),
            ("• Recognition on SKCC website\n\n", 'bullet'),

            ("How to Use:\n", 'heading'),
            ("1. Operate normally throughout the month\n", 'numbered'),
            ("2. Log all SKCC contacts in the app\n", 'numbered'),
            ("3. At month end, generate Monthly Brag Report\n", 'numbered'),
            ("4. Export and submit to SKCC\n\n", 'numbered'),

            ("See ", ()), ("Using Monthly Brag Report", 'link', 'link_brag_usage'), (" for step-by-step instructions.\n\n", ()),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Using the Report", 'link', 'link_brag_usage'), (" - Generate report\n", ()),
            ("• ", ()), ("Submitting Results", 'link', 'link_brag_submission'), (" - Submit to SKCC\n", ()),
            ("• ", ()), ("SKCC Contests", 'link', 'link_contest_overview'), (" - Contest activities\n", ())
        ]

    @staticmethod
    def brag_usage():
        return [
            ("Using Monthly Brag Report\n", 'title'),
            ("\nStep-by-step guide to generating your SKCC Monthly Brag report.\n\n", ()),

            ("Location: Reports menu → SKCC Monthly Brag Report\n\n", 'italic'),

            ("Report Generation Steps:\n", 'heading'),

            ("1. Open the Report Dialog\n", 'subheading'),
            ("• Click 'Reports' in the menu bar\n", 'bullet'),
            ("• Select 'SKCC Monthly Brag Report'\n", 'bullet'),
            ("• Dialog window opens\n\n", 'bullet'),

            ("2. Select Month and Year\n", 'subheading'),
            ("• Year: Use spinner or type (2010-2050)\n", 'bullet'),
            ("• Month: Select from dropdown (1-12)\n", 'bullet'),
            ("• Defaults to current month\n", 'bullet'),
            ("• Can generate reports for any past month\n\n", 'bullet'),

            ("3. Configure Bonus Member (Optional)\n", 'subheading'),
            ("• Enter the monthly bonus member callsign\n", 'bullet'),
            ("• Check SKCC website for current month's bonus member\n", 'bullet'),
            ("• Leave blank if not applicable\n", 'bullet'),
            ("• Worth +25 points if you worked them\n\n", 'bullet'),

            ("4. Generate the Report\n", 'subheading'),
            ("• Click 'Generate Report' button\n", 'bullet'),
            ("• App queries database for the selected month\n", 'bullet'),
            ("• Automatically excludes all contest contacts\n", 'bullet'),
            ("• Calculates unique members and bonus\n\n", 'bullet'),

            ("What You'll See:\n", 'heading'),

            ("Summary Section:\n", 'subheading'),
            ("• Total unique SKCC members worked\n", 'bullet'),
            ("• Bonus member status (worked or not)\n", 'bullet'),
            ("• Final score\n", 'bullet'),
            ("• Month and year\n\n", 'bullet'),

            ("Members List:\n", 'subheading'),
            ("• Scrollable list of all SKCC numbers worked\n", 'bullet'),
            ("• Sorted for easy verification\n", 'bullet'),
            ("• Shows which members counted\n", 'bullet'),
            ("• Bonus member highlighted if worked\n\n", 'bullet'),

            ("5. Export the Report\n", 'subheading'),
            ("• Click 'Export for SKCC Submission' button\n", 'bullet'),
            ("• Choose save location\n", 'bullet'),
            ("• File saved in text format\n", 'bullet'),
            ("• Ready for SKCC submission\n\n", 'bullet'),

            ("Report File Contents:\n", 'heading'),
            ("The exported file includes:\n", ()),
            ("• Your callsign and SKCC number\n", 'bullet'),
            ("• Month and year\n", 'bullet'),
            ("• Total unique members worked\n", 'bullet'),
            ("• Bonus member (if worked)\n", 'bullet'),
            ("• Final score\n", 'bullet'),
            ("• Complete list of SKCC numbers worked\n\n", 'bullet'),

            ("Contest Contact Handling:\n", 'heading'),
            ("The app intelligently filters out contests:\n", ()),
            ("• Checks if contact occurred during WES weekend\n", 'bullet'),
            ("• Checks if contact occurred during SKS (0000-0200 UTC, 4th Wed)\n", 'bullet'),
            ("• Checks if contact occurred during K3Y (January)\n", 'bullet'),
            ("• Only non-contest contacts are counted\n\n", 'bullet'),

            ("Historical Reports:\n", 'heading'),
            ("• Generate reports for any past month\n", 'bullet'),
            ("• Useful for missed submissions\n", 'bullet'),
            ("• Review your activity trends\n", 'bullet'),
            ("• Compare month-to-month performance\n\n", 'bullet'),

            ("Tips:\n", 'heading'),
            ("• Update bonus member callsign at start of each month\n", 'bullet'),
            ("• Generate report before end of month to check progress\n", 'bullet'),
            ("• Keep exported files for your records\n", 'bullet'),
            ("• Listen for the bonus member during the month\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Monthly Brag Overview", 'link', 'link_brag_overview'), (" - What is Monthly Brag\n", ()),
            ("• ", ()), ("Submitting Results", 'link', 'link_brag_submission'), (" - How to submit\n", ()),
            ("• ", ()), ("SKCC Contests", 'link', 'link_contest_overview'), (" - Contest activities\n", ())
        ]

    @staticmethod
    def brag_submission():
        return [
            ("Submitting Monthly Brag Results\n", 'title'),
            ("\nHow to submit your Monthly Brag report to SKCC for recognition and scoring.\n\n", ()),

            ("Prerequisites:\n", 'heading'),
            ("Before submitting:\n", ()),
            ("• Generated your Monthly Brag report\n", 'bullet'),
            ("• Exported the report file\n", 'bullet'),
            ("• Have SKCC website account (free at skccgroup.com)\n\n", 'bullet'),

            ("Submission Process:\n", 'heading'),

            ("1. Generate and Export Report\n", 'subheading'),
            ("• Reports → SKCC Monthly Brag Report\n", 'bullet'),
            ("• Select month and year\n", 'bullet'),
            ("• Enter bonus member callsign (if applicable)\n", 'bullet'),
            ("• Click 'Generate Report'\n", 'bullet'),
            ("• Click 'Export for SKCC Submission'\n", 'bullet'),
            ("• Save the text file\n\n", 'bullet'),

            ("2. Visit SKCC Website\n", 'subheading'),
            ("• Go to skccgroup.com\n", 'bullet'),
            ("• Log into your account\n", 'bullet'),
            ("• Navigate to Monthly Brag submission page\n", 'bullet'),
            ("• Select the appropriate month\n\n", 'bullet'),

            ("3. Submit Your Results\n", 'subheading'),
            ("Two submission methods:\n\n", ()),

            ("Method A - File Upload:\n", 'italic'),
            ("• Use the file upload feature\n", 'bullet'),
            ("• Select your exported text file\n", 'bullet'),
            ("• Upload\n\n", 'bullet'),

            ("Method B - Copy/Paste:\n", 'italic'),
            ("• Open exported file in text editor\n", 'bullet'),
            ("• Copy all contents\n", 'bullet'),
            ("• Paste into SKCC submission form\n", 'bullet'),
            ("• Submit\n\n", 'bullet'),

            ("4. Verify Submission\n", 'subheading'),
            ("• Check that your score appears correctly\n", 'bullet'),
            ("• Verify unique member count\n", 'bullet'),
            ("• Confirm bonus member credit (if worked)\n", 'bullet'),
            ("• Save confirmation for records\n\n", 'bullet'),

            ("Submission Deadline:\n", 'heading'),
            ("• Usually first week of following month\n", 'bullet'),
            ("• Check SKCC website for exact deadline\n", 'bullet'),
            ("• Late submissions may not be accepted\n", 'bullet'),
            ("• Set calendar reminder for monthly submission\n\n", 'bullet'),

            ("What Gets Submitted:\n", 'heading'),
            ("• Your callsign and SKCC number\n", 'bullet'),
            ("• Month and year of report\n", 'bullet'),
            ("• Count of unique members worked\n", 'bullet'),
            ("• Bonus member (if applicable)\n", 'bullet'),
            ("• Final score\n", 'bullet'),
            ("• Optional: List of members worked (for verification)\n\n", 'bullet'),

            ("Recognition:\n", 'heading'),
            ("After submission:\n", ()),
            ("• Your score appears on SKCC Monthly Brag leaderboard\n", 'bullet'),
            ("• Top scores recognized monthly\n", 'bullet'),
            ("• Year-end awards for consistent participation\n", 'bullet'),
            ("• Encourages regular SKCC activity\n\n", 'bullet'),

            ("Troubleshooting:\n", 'heading'),
            ("• Score seems wrong? Review Members List in report dialog\n", 'bullet'),
            ("• Missing members? Check if worked during contest time\n", 'bullet'),
            ("• Can't submit? Verify SKCC account and deadline\n", 'bullet'),
            ("• Need help? Contact SKCC support\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Monthly Brag Overview", 'link', 'link_brag_overview'), (" - What is Monthly Brag\n", ()),
            ("• ", ()), ("Using the Report", 'link', 'link_brag_usage'), (" - Generate report\n", ()),
            ("• ", ()), ("SKCC Contests", 'link', 'link_contest_overview'), (" - Contest activities\n", ())
        ]

    @staticmethod
    def cluster_connect():
        return [
            ("Connecting to DX Clusters\n", 'title'),
            ("\nConnect to worldwide DX spotting networks to see real-time band activity and find stations to work.\n\n", ()),

            ("Location: DX Clusters tab\n\n", 'italic'),

            ("What are DX Clusters?\n", 'heading'),
            ("DX clusters are worldwide networks where operators share real-time information about:\n", ()),
            ("• Stations currently on the air\n", 'bullet'),
            ("• Frequencies they're operating on\n", 'bullet'),
            ("• Rare DX stations\n", 'bullet'),
            ("• SKCC members active\n", 'bullet'),
            ("• Propagation conditions\n\n", 'bullet'),

            ("Available Clusters (20+ nodes):\n", 'heading'),

            ("North America (RBN-Enabled):\n", 'subheading'),
            ("• AE5E - Thief River Falls, MN\n", 'bullet'),
            ("• K1AX-11 - N. Virginia\n", 'bullet'),
            ("• AI9T - Marshall, IL\n", 'bullet'),
            ("• K7TJ-1 - Spokane, WA\n", 'bullet'),
            ("• AI6W-1 - Newcastle, CA\n", 'bullet'),
            ("• KB8PMY-3 - Hamilton, OH\n", 'bullet'),
            ("• K9LC - Rockford, IL\n", 'bullet'),
            ("• AE3N-2 - Virginia\n", 'bullet'),
            ("• K4GSO-2 - Ocala, FL\n", 'bullet'),
            ("• K2CAN - Oswego, NY\n\n", 'bullet'),

            ("North America (Traditional):\n", 'subheading'),
            ("• NC7J - Syracuse, UT (Skimmer)\n", 'bullet'),
            ("• W1NR - Marlborough, MA\n", 'bullet'),
            ("• W1NR-9 - US DX (zones 1-8)\n", 'bullet'),
            ("• K1TTT - Peru, MA\n", 'bullet'),
            ("• W3LPL - Glenwood, MD\n", 'bullet'),
            ("• W6RFU - Santa Barbara, CA\n\n", 'bullet'),

            ("International:\n", 'subheading'),
            ("• G6NHU-2 - Essex, UK (RBN feed)\n", 'bullet'),
            ("• DL8LAS - Kiel, Germany (Skimmer)\n", 'bullet'),
            ("• S50CLX - Slovenia (Multi-mode)\n", 'bullet'),
            ("• ZL2ARN-10 - New Zealand\n\n", 'bullet'),

            ("RBN = Reverse Beacon Network (automated CW spotting)\n\n", 'italic'),

            ("Connection Steps:\n", 'heading'),

            ("1. Configure Your Callsign\n", 'subheading'),
            ("• Enter your callsign in the 'Your Callsign' field\n", 'bullet'),
            ("• Or configure once in Settings → Station Information\n", 'bullet'),
            ("• Callsign is required for cluster login\n\n", 'bullet'),

            ("2. Select a Cluster\n", 'subheading'),
            ("• Open 'Select Cluster' dropdown\n", 'bullet'),
            ("• Choose from 20+ available clusters\n", 'bullet'),
            ("• Recommendation: Start with AE5E or K1AX-11 (RBN-enabled)\n", 'bullet'),
            ("• US operators: Choose North American clusters for lower latency\n", 'bullet'),
            ("• DX operators: Choose clusters in your region\n\n", 'bullet'),

            ("3. Connect\n", 'subheading'),
            ("• Click 'Connect' button\n", 'bullet'),
            ("• App connects via telnet\n", 'bullet'),
            ("• Status changes to 'Connected' (green)\n", 'bullet'),
            ("• Cluster info displays (software version, node)\n", 'bullet'),
            ("• Spots begin appearing in table\n\n", 'bullet'),

            ("Connection Status Indicators:\n", 'heading'),
            ("• Disconnected (red) - Not connected\n", 'bullet'),
            ("• Connecting... - Connection in progress\n", 'bullet'),
            ("• Connected (green) - Active connection\n", 'bullet'),
            ("• Error (red) - Connection failed\n\n", 'bullet'),

            ("Auto-Connect on Startup:\n", 'heading'),
            ("Configure automatic connection:\n", ()),
            ("1. Go to Settings → DX Cluster Preferences\n", 'numbered'),
            ("2. Select your preferred cluster\n", 'numbered'),
            ("3. Enable 'Auto-connect on startup'\n", 'numbered'),
            ("4. Save settings\n", 'numbered'),
            ("5. Next launch automatically connects\n\n", 'numbered'),

            ("Disconnecting:\n", 'heading'),
            ("• Click 'Disconnect' button (replaces Connect when active)\n", 'bullet'),
            ("• Cleanly closes telnet connection\n", 'bullet'),
            ("• Stops receiving spots\n", 'bullet'),
            ("• Can reconnect anytime\n\n", 'bullet'),

            ("Cluster Information Display:\n", 'heading'),
            ("When connected, you'll see:\n", ()),
            ("• Cluster software (DX Spider, AR-Cluster, etc.)\n", 'bullet'),
            ("• Node callsign and location\n", 'bullet'),
            ("• Connection status\n", 'bullet'),
            ("• RBN support indicator\n\n", 'bullet'),

            ("Troubleshooting Connection Issues:\n", 'heading'),
            ("• Can't connect? Try a different cluster\n", 'bullet'),
            ("• Firewall blocking? Check port 7300 or 7373\n", 'bullet'),
            ("• Timeout? Choose cluster closer to your location\n", 'bullet'),
            ("• See ", ()), ("Cluster Troubleshooting", 'link', 'link_cluster_issues'), (" for more help\n\n", ()),

            ("Best Practices:\n", 'heading'),
            ("• Choose clusters near your geographic location\n", 'bullet'),
            ("• RBN clusters provide more CW spots (automated)\n", 'bullet'),
            ("• Traditional clusters have human spotters\n", 'bullet'),
            ("• Try different clusters to find your favorite\n", 'bullet'),
            ("• Disconnect when not actively using\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Cluster Commands", 'link', 'link_cluster_commands'), (" - Send commands to cluster\n", ()),
            ("• ", ()), ("Reading Spots", 'link', 'link_cluster_spots'), (" - Understanding spot display\n", ()),
            ("• ", ()), ("SKCC Highlighting", 'link', 'link_skcc_highlighting'), (" - C/T/S member spots\n", ()),
            ("• ", ()), ("Troubleshooting", 'link', 'link_cluster_issues'), (" - Connection problems\n", ())
        ]

    @staticmethod
    def cluster_commands():
        return [
            ("DX Cluster Commands\n", 'title'),
            ("\nSend commands to the DX cluster for information and configuration.\n\n", ()),

            ("Location: DX Clusters tab → Command input field\n\n", 'italic'),

            ("How to Send Commands:\n", 'heading'),
            ("1. Ensure you're connected to a cluster\n", 'numbered'),
            ("2. Type command in the command input field\n", 'numbered'),
            ("3. Press Enter\n", 'numbered'),
            ("4. Response appears in the cluster output window\n\n", 'numbered'),

            ("Common Commands:\n", 'heading'),

            ("Spot Information:\n", 'subheading'),
            ("• SH/DX - Show recent DX spots\n", 'bullet'),
            ("• SH/DX 25 - Show last 25 spots\n", 'bullet'),
            ("• SH/DX on 20m - Show spots on 20 meters\n", 'bullet'),
            ("• SH/DX K1ABC - Show spots for specific callsign\n\n", 'bullet'),

            ("Propagation Information:\n", 'subheading'),
            ("• SH/WWV - Show WWV/WWVH propagation bulletins\n", 'bullet'),
            ("• SH/WCY - Show WCY propagation data\n", 'bullet'),
            ("• SH/SUN - Show solar data (SFI, A/K index)\n\n", 'bullet'),

            ("Station Information:\n", 'subheading'),
            ("• SH/QRZ W1AW - Show callsign info from QRZ\n", 'bullet'),
            ("• SH/PREFIX VP2 - Show DXCC prefix information\n\n", 'bullet'),

            ("Announcements:\n", 'subheading'),
            ("• SH/ANNOUNCE - Show recent announcements\n", 'bullet'),
            ("• SH/WX - Show weather information\n\n", 'bullet'),

            ("User Management:\n", 'subheading'),
            ("• SET/NAME your_name - Set your name\n", 'bullet'),
            ("• SET/QTH your_location - Set your location\n", 'bullet'),
            ("• SET/HOMENODE callsign - Set your home node\n\n", 'bullet'),

            ("Filtering (if supported):\n", 'subheading'),
            ("• SET/FILTER - Configure spot filters\n", 'bullet'),
            ("• ACCEPT/SPOTS on hf/cw - Show only HF CW spots\n", 'bullet'),
            ("• REJECT/SPOTS on vhf - Reject VHF spots\n\n", 'bullet'),

            ("Spotting (when appropriate):\n", 'subheading'),
            ("• DX 14.250 W1AW - Spot W1AW on 14.250 MHz\n", 'bullet'),
            ("• DX 7.055 N4ABC SKCC - Spot with comment\n\n", 'bullet'),

            ("Important: Only spot stations you've actually heard!\n\n", 'italic'),

            ("Help Commands:\n", 'subheading'),
            ("• HELP - Show available commands\n", 'bullet'),
            ("• HELP SH/DX - Help for specific command\n\n", 'bullet'),

            ("Cluster-Specific Commands:\n", 'heading'),

            ("DX Spider Clusters:\n", 'subheading'),
            ("• SHOW/STATION - Your station info\n", 'bullet'),
            ("• SHOW/TIME - Current UTC time\n", 'bullet'),
            ("• SHOW/MOON - Moon position and phase\n\n", 'bullet'),

            ("AR-Cluster:\n", 'subheading'),
            ("• SHOW INFO - Cluster information\n", 'bullet'),
            ("• SHOW USERS - Currently connected users\n\n", 'bullet'),

            ("Command Syntax Notes:\n", 'heading'),
            ("• Commands are NOT case-sensitive\n", 'bullet'),
            ("• SH is short for SHOW\n", 'bullet'),
            ("• Most clusters support abbreviations\n", 'bullet'),
            ("• Parameters separated by spaces\n", 'bullet'),
            ("• Type HELP for cluster-specific commands\n\n", 'bullet'),

            ("App Command Input:\n", 'heading'),
            ("The command input field in the app:\n", ()),
            ("• Located below spot filters\n", 'bullet'),
            ("• Type command and press Enter\n", 'bullet'),
            ("• Response shown in cluster output area\n", 'bullet'),
            ("• Previous commands accessible with Up arrow\n\n", 'bullet'),

            ("Useful for SKCC:\n", 'heading'),
            ("• SH/DX on 40m - Find 40m activity\n", 'bullet'),
            ("• SH/DX SKCC - Find spots mentioning SKCC\n", 'bullet'),
            ("• DX 7.055 N1ABC SKCC 12345C - Spot SKCC member\n\n", 'bullet'),

            ("Command Etiquette:\n", 'heading'),
            ("• Only spot stations you've actually heard\n", 'bullet'),
            ("• Don't spam commands\n", 'bullet'),
            ("• Include helpful info in spot comments\n", 'bullet'),
            ("• Be courteous to other cluster users\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Connecting to Clusters", 'link', 'link_cluster_connect'), (" - Connection setup\n", ()),
            ("• ", ()), ("Reading Spots", 'link', 'link_cluster_spots'), (" - Understanding spots\n", ()),
            ("• ", ()), ("Commands Reference", 'link', 'link_cluster_commands_ref'), (" - Complete command list\n", ())
        ]

    @staticmethod
    def cluster_spots():
        return [
            ("Reading DX Spots\n", 'title'),
            ("\nUnderstand how to read and interpret DX spots from the cluster.\n\n", ()),

            ("Location: DX Clusters tab → Spots table\n\n", 'italic'),

            ("What is a DX Spot?\n", 'heading'),
            ("A DX spot is a real-time report that a station is active on a specific frequency. It includes:\n", ()),
            ("• Callsign of the station being spotted (DX station)\n", 'bullet'),
            ("• Frequency in kHz\n", 'bullet'),
            ("• Callsign of the spotter (who heard them)\n", 'bullet'),
            ("• Time of the spot (UTC)\n", 'bullet'),
            ("• Optional comment\n\n", 'bullet'),

            ("Spot Table Columns:\n", 'heading'),
            ("Time - UTC time when spot was posted (HH:MM)\n", 'bullet'),
            ("Frequency - Operating frequency in kHz\n", 'bullet'),
            ("DX Callsign - Station that was spotted\n", 'bullet'),
            ("Spotter - Who posted the spot\n", 'bullet'),
            ("Comment - Additional information\n\n", 'bullet'),

            ("Understanding RBN Spots:\n", 'heading'),
            ("Reverse Beacon Network (RBN) spots:\n", ()),
            ("• Automated CW spotting system\n", 'bullet'),
            ("• Very accurate frequencies\n", 'bullet'),
            ("• Shows callsigns heard by RBN receivers worldwide\n", 'bullet'),
            ("• Great for finding CW activity\n\n", 'bullet'),

            ("Color Coding:\n", 'heading'),
            ("• Cyan/Blue: SKCC members (C/T/S detected)\n", 'bullet'),
            ("• Standard: Regular spots\n\n", 'bullet'),

            ("Using Spots:\n", 'heading'),
            ("1. Watch spot table for activity\n", 'numbered'),
            ("2. Look for SKCC members (cyan highlights)\n", 'numbered'),
            ("3. Note the frequency\n", 'numbered'),
            ("4. Tune radio to that frequency\n", 'numbered'),
            ("5. Listen before calling\n\n", 'numbered'),

            ("Tips:\n", 'heading'),
            ("• Fresh spots (0-5 min) = station likely still there\n", 'bullet'),
            ("• Use band filters to show only desired bands\n", 'bullet'),
            ("• Sort by clicking column headers\n", 'bullet'),
            ("• Multiple spots of same call = strong signal\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("SKCC Highlighting", 'link', 'link_skcc_highlighting'), ("\n", ()),
            ("• ", ()), ("Connecting", 'link', 'link_cluster_connect'), ("\n", ())
        ]

    @staticmethod
    def skcc_highlighting():
        return [
            ("SKCC Member Highlighting\n", 'title'),
            ("\nAutomatic highlighting of SKCC Centurion, Tribune, and Senator members in DX spots.\n\n", ()),

            ("Location: DX Clusters tab → Spots table\n\n", 'italic'),

            ("What is SKCC Highlighting?\n", 'heading'),
            ("The app automatically detects and highlights SKCC members with achievement awards in the spot table, making them easy to find.\n\n", ()),

            ("How It Works:\n", 'heading'),
            ("The app scans each spot for SKCC suffixes:\n", ()),
            ("• Centurion (C) - Example: 12345C\n", 'bullet'),
            ("• Tribune (T) - Example: 12345T\n", 'bullet'),
            ("• Senator (S) - Example: 12345S\n\n", 'bullet'),

            ("When detected in comments, the entire spot row is highlighted in cyan/blue.\n\n", ()),

            ("Visual Indicators:\n", 'heading'),
            ("• Cyan/Blue background - SKCC member with C/T/S\n", 'bullet'),
            ("• Standard background - Regular spots\n\n", 'bullet'),

            ("Detection Methods:\n", 'heading'),
            ("The app looks for patterns like:\n", ()),
            ("• 'SKCC 12345C' in comment field\n", 'bullet'),
            ("• '12345T' anywhere in comment\n", 'bullet'),
            ("• Spots from SKCC roster members\n\n", 'bullet'),

            ("Why This Matters:\n", 'heading'),
            ("• Quickly find SKCC members for awards progress\n", 'bullet'),
            ("• Identify bonus-worthy contacts for contests\n", 'bullet'),
            ("• See who's active in SKCC community\n", 'bullet'),
            ("• Work toward Centurion/Tribune/Senator awards\n\n", 'bullet'),

            ("Best Practices:\n", 'heading'),
            ("• Check comments for SKCC numbers\n", 'bullet'),
            ("• Highlighted spots good for award QSOs\n", 'bullet'),
            ("• During contests, these earn bonus points\n", 'bullet'),
            ("• Log SKCC numbers when working these stations\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Reading Spots", 'link', 'link_cluster_spots'), ("\n", ()),
            ("• ", ()), ("SKCC Awards", 'link', 'link_skcc_awards'), ("\n", ()),
            ("• ", ()), ("Contests", 'link', 'link_contest_overview'), ("\n", ())
        ]

    @staticmethod
    def arrl_awards():
        return [
            ("ARRL Awards Tracking\n", 'title'),
            ("\nTrack your progress toward ARRL (American Radio Relay League) awards including WAS, DXCC, and WAC.\n\n", ()),

            ("Location: ARRL Awards tab\n\n", 'italic'),

            ("Supported ARRL Awards:\n", 'heading'),

            ("WAS - Worked All States:\n", 'subheading'),
            ("• Contact all 50 US states\n", 'bullet'),
            ("• Can be achieved on any band/mode\n", 'bullet'),
            ("• App tracks which states you've worked\n", 'bullet'),
            ("• Progress bar shows completion percentage\n", 'bullet'),
            ("• List shows confirmed states\n\n", 'bullet'),

            ("DXCC - DX Century Club:\n", 'subheading'),
            ("• Contact 100+ DXCC entities (countries/territories)\n", 'bullet'),
            ("• Prestigious international award\n", 'bullet'),
            ("• App tracks unique DXCC entities\n", 'bullet'),
            ("• Automatic entity detection from callsign\n", 'bullet'),
            ("• Shows progress toward 100\n\n", 'bullet'),

            ("WAC - Worked All Continents:\n", 'subheading'),
            ("• Contact all 6 continents\n", 'bullet'),
            ("• NA, SA, EU, AF, AS, OC\n", 'bullet'),
            ("• Simple but satisfying award\n", 'bullet'),
            ("• Great starter award\n\n", 'bullet'),

            ("Features:\n", 'heading'),
            ("• Real-time progress tracking\n", 'bullet'),
            ("• Visual progress bars\n", 'bullet'),
            ("• Lists of worked/needed entities\n", 'bullet'),
            ("• Automatic updates as you log QSOs\n", 'bullet'),
            ("• Export lists for ARRL applications\n\n", 'bullet'),

            ("Using the Tab:\n", 'heading'),
            ("1. Navigate to ARRL Awards tab\n", 'numbered'),
            ("2. Select award from dropdown\n", 'numbered'),
            ("3. View your progress\n", 'numbered'),
            ("4. See what you still need\n", 'numbered'),
            ("5. Export for award application\n\n", 'numbered'),

            ("Award Applications:\n", 'heading'),
            ("To apply for ARRL awards:\n", ()),
            ("• Visit arrl.org/awards\n", 'bullet'),
            ("• Most require QSL card confirmation\n", 'bullet'),
            ("• LOTW (Logbook of the World) accepted\n", 'bullet'),
            ("• Fees apply for most awards\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("SKCC Awards", 'link', 'link_skcc_awards'), ("\n", ()),
            ("• ", ()), ("Contact Logging", 'link', 'link_log_qso'), ("\n", ())
        ]

    @staticmethod
    def skcc_awards():
        return [
            ("SKCC Awards Tracking\n", 'title'),
            ("\nComprehensive tracking for all 11 Straight Key Century Club awards with automatic validation and progress monitoring.\n\n", ()),

            ("Location: SKCC Awards tab\n\n", 'italic'),

            ("All 11 SKCC Awards:\n", 'heading'),

            ("1. Centurion (C) Award:\n", 'subheading'),
            ("• Work 100+ unique SKCC members\n", 'bullet'),
            ("• Foundation award for SKCC\n", 'bullet'),
            ("• Endorsements: x2, x3, x4... up to x40+\n", 'bullet'),
            ("• Mechanical keys only\n\n", 'bullet'),

            ("2. Tribune (T) Award:\n", 'subheading'),
            ("• Work 50+ Tribune or Senator members\n", 'bullet'),
            ("• Requires Centurion first\n", 'bullet'),
            ("• Endorsements: x2 through x30\n", 'bullet'),
            ("• QSOs after earning Centurion\n\n", 'bullet'),

            ("3. Senator (S) Award:\n", 'subheading'),
            ("• Work 200+ Tribune/Senator members\n", 'bullet'),
            ("• Requires Tribune x8 first\n", 'bullet'),
            ("• Endorsements: x2 through x10\n", 'bullet'),
            ("• QSOs after Tribune x8 date\n\n", 'bullet'),

            ("4. Triple Key Award (TKA):\n", 'subheading'),
            ("• Work 100+ members with EACH key type:\n", 'bullet'),
            ("  - 100+ with straight key\n", ()),
            ("  - 100+ with bug\n", ()),
            ("  - 100+ with sideswiper\n", ()),
            ("• Endorsements: x2, x3, x5, x10\n", 'bullet'),
            ("• Effective date: Nov 10, 2018\n\n", 'bullet'),

            ("5. Rag Chew Award:\n", 'subheading'),
            ("• Complete 30+ QSOs of 30+ minutes each\n", 'bullet'),
            ("• Total = 900+ minutes (15 hours)\n", 'bullet'),
            ("• Encourages leisurely conversations\n", 'bullet'),
            ("• Endorsements based on total minutes\n\n", 'bullet'),

            ("6. SKCC WAS - Worked All States:\n", 'subheading'),
            ("• Work all 50 US states with SKCC members\n", 'bullet'),
            ("• Different from ARRL WAS\n", 'bullet'),
            ("• Only SKCC members count\n\n", 'bullet'),

            ("7. SKCC WAS-T:\n", 'subheading'),
            ("• Work all 50 states with Tribune/Senator\n", 'bullet'),
            ("• More challenging than basic WAS\n\n", 'bullet'),

            ("8. SKCC WAS-S:\n", 'subheading'),
            ("• Work all 50 states with Senators\n", 'bullet'),
            ("• Most challenging WAS variant\n\n", 'bullet'),

            ("9. Canadian Maple Leaf:\n", 'subheading'),
            ("• Work all 10 Canadian provinces\n", 'bullet'),
            ("• Plus 3 territories for endorsement\n", 'bullet'),
            ("• BC, AB, SK, MB, ON, QC, NB, NS, PE, NL\n\n", 'bullet'),

            ("10. SKCC DX Award:\n", 'subheading'),
            ("• Work SKCC members in DX countries\n", 'bullet'),
            ("• Endorsements for increasing country count\n\n", 'bullet'),

            ("11. PFX - Callsign Prefix Award:\n", 'subheading'),
            ("• Work unique callsign prefixes\n", 'bullet'),
            ("• W1, W2, K4, VE3, G, etc.\n", 'bullet'),
            ("• Endorsements for milestone counts\n\n", 'bullet'),

            ("Key Features:\n", 'heading'),
            ("• Real-time progress tracking\n", 'bullet'),
            ("• Automatic SKCC roster validation\n", 'bullet'),
            ("• Endorsement level calculation\n", 'bullet'),
            ("• Qualifying contact lists\n", 'bullet'),
            ("• Export applications in text format\n", 'bullet'),
            ("• Date-based validation (effective dates)\n\n", 'bullet'),

            ("Important Requirements:\n", 'heading'),
            ("• SKCC join date MUST be configured\n", 'bullet'),
            ("• Centurion date needed for Tribune/Senator\n", 'bullet'),
            ("• Tribune x8 date needed for Senator\n", 'bullet'),
            ("• Only mechanical keys valid (no keyers)\n", 'bullet'),
            ("• Special event calls may not count\n\n", 'bullet'),

            ("Configure in Settings → SKCC Award Configuration\n\n", 'italic'),

            ("Using the Awards Tab:\n", 'heading'),
            ("1. Go to SKCC Awards tab\n", 'numbered'),
            ("2. Select award from list\n", 'numbered'),
            ("3. View progress and endorsement level\n", 'numbered'),
            ("4. Review qualifying contacts\n", 'numbered'),
            ("5. Export application when ready\n", 'numbered'),
            ("6. Submit to SKCC for approval\n\n", 'numbered'),

            ("Award Applications:\n", 'heading'),
            ("• Visit skccgroup.com/awards\n", 'bullet'),
            ("• Most awards are free\n", 'bullet'),
            ("• No QSL cards required\n", 'bullet'),
            ("• Self-certify your contacts\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Settings", 'link', 'link_station_info'), (" - Configure dates\n", ()),
            ("• ", ()), ("ARRL Awards", 'link', 'link_arrl_awards'), ("\n", ())
        ]

    @staticmethod
    def adif_export():
        return [
            ("ADIF Export - Full Log\n", 'title'),
            ("\nExport your entire contact log in ADIF 3.x format for use with other logging software.\n\n", ()),

            ("Location: File menu → Export Log (ADIF)\n\n", 'italic'),

            ("What is ADIF?\n", 'heading'),
            ("Amateur Data Interchange Format - the universal standard for amateur radio logging data exchange. Compatible with:\n", ()),
            ("• LOTW (Logbook of the World)\n", 'bullet'),
            ("• QRZ.com Logbook\n", 'bullet'),
            ("• eQSL\n", 'bullet'),
            ("• Log4OM, N1MM, WSJT-X\n", 'bullet'),
            ("• All major logging software\n\n", 'bullet'),

            ("Export Process:\n", 'heading'),
            ("1. Click File → Export Log (ADIF)\n", 'numbered'),
            ("2. Choose save location\n", 'numbered'),
            ("3. Enter filename (e.g., mylog.adi)\n", 'numbered'),
            ("4. Click Save\n", 'numbered'),
            ("5. All contacts exported\n\n", 'numbered'),

            ("What's Included:\n", 'heading'),
            ("Every contact in your database with all fields:\n", ()),
            ("• Callsign, date, time, frequency, band, mode\n", 'bullet'),
            ("• RST sent/received\n", 'bullet'),
            ("• Name, QTH, grid, state, county, country\n", 'bullet'),
            ("• SKCC, POTA, SOTA, IOTA references\n", 'bullet'),
            ("• Notes and comments\n", 'bullet'),
            ("• All 25+ logged fields\n\n", 'bullet'),

            ("Use Cases:\n", 'heading'),
            ("• Backup your entire log\n", 'bullet'),
            ("• Transfer to another logging program\n", 'bullet'),
            ("• Submit to LOTW for confirmations\n", 'bullet'),
            ("• Upload to QRZ.com\n", 'bullet'),
            ("• Share with friends\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Date Range Export", 'link', 'link_adif_date_range'), (" - Export specific period\n", ()),
            ("• ", ()), ("SKCC Export", 'link', 'link_adif_skcc'), (" - SKCC contacts only\n", ()),
            ("• ", ()), ("Import", 'link', 'link_adif_import'), ("\n", ())
        ]

    @staticmethod
    def adif_date_range():
        return [
            ("ADIF Export - Date/Time Range\n", 'title'),
            ("\nExport contacts from a specific time period - perfect for contests or event logs.\n\n", ()),

            ("Location: File menu → Export by Date/Time Range\n\n", 'italic'),

            ("Why Use Date Range Export?\n", 'heading'),
            ("• Export contest logs only\n", 'bullet'),
            ("• Submit specific event periods\n", 'bullet'),
            ("• Share weekend operation\n", 'bullet'),
            ("• Isolate special activations\n\n", 'bullet'),

            ("Export Process:\n", 'heading'),
            ("1. Click File → Export by Date/Time Range\n", 'numbered'),
            ("2. Dialog opens with date/time selectors\n", 'numbered'),
            ("3. Enter start date and time (UTC)\n", 'numbered'),
            ("4. Enter end date and time (UTC)\n", 'numbered'),
            ("5. Click Export\n", 'numbered'),
            ("6. Choose filename and save\n\n", 'numbered'),

            ("Date/Time Format:\n", 'heading'),
            ("• Date: YYYY-MM-DD (e.g., 2024-01-15)\n", 'bullet'),
            ("• Time: HH:MM (24-hour UTC)\n", 'bullet'),
            ("• Always use UTC, not local time\n\n", 'bullet'),

            ("Example Use Cases:\n", 'heading'),

            ("Contest Export:\n", 'subheading'),
            ("WES runs Friday 1800 - Sunday 1800 UTC\n", ()),
            ("Start: 2024-01-05 18:00\n", ()),
            ("End: 2024-01-07 18:00\n\n", ()),

            ("Field Day:\n", 'subheading'),
            ("Start: 2024-06-22 18:00\n", ()),
            ("End: 2024-06-23 21:00\n\n", ()),

            ("What's Exported:\n", 'heading'),
            ("Only contacts within the specified time range, with all fields intact.\n\n", ()),

            ("Tips:\n", 'heading'),
            ("• Double-check UTC times\n", 'bullet'),
            ("• Include buffer time before/after\n", 'bullet'),
            ("• Use for contest submissions\n", 'bullet'),
            ("• Keep original exports as backup\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Full Export", 'link', 'link_adif_export'), ("\n", ()),
            ("• ", ()), ("Contest Export", 'link', 'link_contest_export'), ("\n", ())
        ]

    @staticmethod
    def adif_skcc():
        return [
            ("ADIF Export - SKCC Contacts Only\n", 'title'),
            ("\nExport only contacts with SKCC numbers - useful for SKCC-specific submissions.\n\n", ()),

            ("Location: File menu → Export SKCC Contacts\n\n", 'italic'),

            ("What Gets Exported:\n", 'heading'),
            ("Only contacts where you logged an SKCC number in the SKCC Number field.\n\n", ()),

            ("Export Process:\n", 'heading'),
            ("1. Click File → Export SKCC Contacts\n", 'numbered'),
            ("2. Choose save location\n", 'numbered'),
            ("3. Enter filename\n", 'numbered'),
            ("4. Click Save\n\n", 'numbered'),

            ("Use Cases:\n", 'heading'),
            ("• Submit to SKCC for awards\n", 'bullet'),
            ("• Analyze SKCC activity\n", 'bullet'),
            ("• Share with SKCC friends\n", 'bullet'),
            ("• Import to SKCC-specific software\n\n", 'bullet'),

            ("What's Included:\n", 'heading'),
            ("All fields for SKCC contacts:\n", ()),
            ("• Callsign and SKCC number\n", 'bullet'),
            ("• Date, time, frequency, mode\n", 'bullet'),
            ("• State/province/country\n", 'bullet'),
            ("• All other logged fields\n\n", 'bullet'),

            ("Filtering:\n", 'heading'),
            ("The app automatically filters to include only contacts with non-empty SKCC numbers.\n\n", ()),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Full Export", 'link', 'link_adif_export'), ("\n", ()),
            ("• ", ()), ("SKCC Awards", 'link', 'link_skcc_awards'), ("\n", ())
        ]

    @staticmethod
    def adif_import():
        return [
            ("ADIF Import\n", 'title'),
            ("\nImport contacts from other logging software via ADIF 3.x format.\n\n", ()),

            ("Location: File menu → Import Log (ADIF)\n\n", 'italic'),

            ("What Can You Import?\n", 'heading'),
            ("ADIF files from:\n", ()),
            ("• Other W4GNS Logger backups\n", 'bullet'),
            ("• Log4OM, N1MM, WSJT-X exports\n", 'bullet'),
            ("• QRZ.com logbook downloads\n", 'bullet'),
            ("• LOTW ADIF exports\n", 'bullet'),
            ("• Any ADIF 3.x compliant file\n\n", 'bullet'),

            ("Import Process:\n", 'heading'),
            ("1. Click File → Import Log (ADIF)\n", 'numbered'),
            ("2. Select ADIF file (.adi or .adif)\n", 'numbered'),
            ("3. App validates file format\n", 'numbered'),
            ("4. Progress bar shows import status\n", 'numbered'),
            ("5. Duplicate detection runs automatically\n", 'numbered'),
            ("6. Summary shows imported contacts\n\n", 'numbered'),

            ("Duplicate Detection:\n", 'heading'),
            ("The app checks for duplicates using:\n", ()),
            ("• Same callsign\n", 'bullet'),
            ("• Same date\n", 'bullet'),
            ("• Within 10 minutes of time\n", 'bullet'),
            ("• Skips true duplicates\n", 'bullet'),
            ("• Reports duplicate count\n\n", 'bullet'),

            ("Supported Fields:\n", 'heading'),
            ("All standard ADIF fields:\n", ()),
            ("• Call, QSO date, time on/off\n", 'bullet'),
            ("• Frequency, band, mode\n", 'bullet'),
            ("• RST sent/received\n", 'bullet'),
            ("• Name, QTH, grid, state, county\n", 'bullet'),
            ("• SKCC, POTA, SOTA, IOTA\n", 'bullet'),
            ("• And more\n\n", 'bullet'),

            ("Important Notes:\n", 'heading'),
            ("• Always backup before importing\n", 'bullet'),
            ("• Large imports may take time\n", 'bullet'),
            ("• Review import summary\n", 'bullet'),
            ("• Duplicates are skipped, not merged\n\n", 'bullet'),

            ("Troubleshooting:\n", 'heading'),
            ("• File won't import? Check ADIF format validity\n", 'bullet'),
            ("• Missing fields? Some data may not map\n", 'bullet'),
            ("• Many duplicates? Expected if re-importing\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Export", 'link', 'link_adif_export'), ("\n", ()),
            ("• ", ()), ("Troubleshooting", 'link', 'link_database_issues'), ("\n", ())
        ]

    @staticmethod
    def qrz_setup():
        return [
            ("QRZ.com Integration Setup\n", 'title'),
            ("\nConfigure QRZ.com integration for automatic callsign lookups and logbook uploads.\n\n", ()),

            ("Location: Settings tab → QRZ.com Integration\n\n", 'italic'),

            ("What You Need:\n", 'heading'),
            ("• QRZ.com account (free at qrz.com)\n", 'bullet'),
            ("• XML Subscription ($$$) for lookups\n", 'bullet'),
            ("• API Key (free) for logbook uploads\n\n", 'bullet'),

            ("Setup Steps:\n", 'heading'),

            ("1. Create QRZ Account:\n", 'subheading'),
            ("• Visit qrz.com\n", 'bullet'),
            ("• Click Register / Sign Up\n", 'bullet'),
            ("• Complete registration\n\n", 'bullet'),

            ("2. Get XML Subscription (for lookups):\n", 'subheading'),
            ("• Log into QRZ.com\n", 'bullet'),
            ("• Go to Account → Subscriptions\n", 'bullet'),
            ("• Purchase XML Subscription\n", 'bullet'),
            ("• Required for automatic name/QTH/grid lookups\n\n", 'bullet'),

            ("3. Get API Key (for uploads):\n", 'subheading'),
            ("• Log into QRZ.com\n", 'bullet'),
            ("• Go to Logbook → Settings → API\n", 'bullet'),
            ("• Copy your API key\n", 'bullet'),
            ("• Free for all users\n\n", 'bullet'),

            ("4. Configure in App:\n", 'subheading'),
            ("• Go to Settings → QRZ.com Integration\n", 'bullet'),
            ("• Enter QRZ username\n", 'bullet'),
            ("• Enter QRZ password\n", 'bullet'),
            ("• Paste API key\n", 'bullet'),
            ("• Enable 'Auto-lookup'\n", 'bullet'),
            ("• Enable 'Auto-upload' (optional)\n", 'bullet'),
            ("• Click 'Test QRZ Connection'\n", 'bullet'),
            ("• Verify success message\n\n", 'bullet'),

            ("Settings Explained:\n", 'heading'),

            ("Auto-lookup:\n", 'subheading'),
            ("• Automatically looks up callsigns when entered\n", 'bullet'),
            ("• Fills name, QTH, grid, state, county\n", 'bullet'),
            ("• Requires XML subscription\n\n", 'bullet'),

            ("Auto-upload:\n", 'subheading'),
            ("• Uploads contacts to QRZ immediately after logging\n", 'bullet'),
            ("• Keeps QRZ logbook in sync\n", 'bullet'),
            ("• Requires API key\n\n", 'bullet'),

            ("Testing Connection:\n", 'heading'),
            ("The 'Test QRZ Connection' button verifies:\n", ()),
            ("• Username/password correct\n", 'bullet'),
            ("• XML subscription active\n", 'bullet'),
            ("• Network connectivity\n", 'bullet'),
            ("• API key valid\n\n", 'bullet'),

            ("Troubleshooting:\n", 'heading'),
            ("• Connection fails? Check credentials\n", 'bullet'),
            ("• Lookup not working? Verify XML subscription active\n", 'bullet'),
            ("• Upload fails? Verify API key\n", 'bullet'),
            ("• See ", ()), ("QRZ Troubleshooting", 'link', 'link_qrz_issues'), ("\n\n", ()),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QRZ Lookups", 'link', 'link_qrz_lookup'), ("\n", ()),
            ("• ", ()), ("QRZ Upload", 'link', 'link_qrz_upload'), ("\n", ())
        ]

    @staticmethod
    def qrz_lookup():
        return [
            ("QRZ.com XML Lookups\n", 'title'),
            ("\nAutomatic callsign information retrieval from QRZ.com's database.\n\n", ()),

            ("Requirements:\n", 'heading'),
            ("• QRZ.com XML Subscription (paid)\n", 'bullet'),
            ("• Configured credentials in Settings\n", 'bullet'),
            ("• Auto-lookup enabled\n\n", 'bullet'),

            ("How It Works:\n", 'heading'),
            ("1. Enter callsign in Log Contacts tab\n", 'numbered'),
            ("2. Press Tab or click outside field\n", 'numbered'),
            ("3. App queries QRZ XML API\n", 'numbered'),
            ("4. Data auto-fills within 1-2 seconds\n\n", 'numbered'),

            ("What Gets Looked Up:\n", 'heading'),
            ("• Operator's first name\n", 'bullet'),
            ("• QTH (location)\n", 'bullet'),
            ("• Grid square\n", 'bullet'),
            ("• State (US stations)\n", 'bullet'),
            ("• County (US stations)\n", 'bullet'),
            ("• License class\n", 'bullet'),
            ("• Country, continent, zones\n\n", 'bullet'),

            ("Lookup Without Subscription:\n", 'heading'),
            ("Without XML subscription, you still get:\n", ()),
            ("• Country from built-in DXCC database\n", 'bullet'),
            ("• Continent\n", 'bullet'),
            ("• CQ/ITU zones\n", 'bullet'),
            ("• No name/QTH/grid\n\n", 'bullet'),

            ("Manual Lookup:\n", 'heading'),
            ("Even with auto-lookup disabled:\n", ()),
            ("• Click 'Lookup' button next to callsign\n", 'bullet'),
            ("• Performs one-time lookup\n\n", 'bullet'),

            ("Tips:\n", 'heading'),
            ("• Lookups use internet - require connection\n", 'bullet'),
            ("• Failed lookup? Station may not be in QRZ\n", 'bullet'),
            ("• Can manually override auto-filled data\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QRZ Setup", 'link', 'link_qrz_setup'), ("\n", ()),
            ("• ", ()), ("Auto-Lookup", 'link', 'link_auto_lookup'), ("\n", ())
        ]

    @staticmethod
    def qrz_upload():
        return [
            ("QRZ.com Logbook Upload\n", 'title'),
            ("\nAutomatically or manually upload contacts to your QRZ.com logbook.\n\n", ()),

            ("Requirements:\n", 'heading'),
            ("• QRZ.com account (free)\n", 'bullet'),
            ("• QRZ API key (free)\n", 'bullet'),
            ("• Configured in Settings\n\n", 'bullet'),

            ("Auto-Upload:\n", 'heading'),
            ("When enabled, contacts upload immediately after logging:\n", ()),
            ("1. Log contact (Ctrl+Enter)\n", 'numbered'),
            ("2. Contact saves to database\n", 'numbered'),
            ("3. Automatically uploads to QRZ\n", 'numbered'),
            ("4. Confirmation message appears\n\n", 'numbered'),

            ("Manual Upload:\n", 'heading'),
            ("If auto-upload disabled:\n", ()),
            ("• Click 'Upload to QRZ' button after logging\n", 'bullet'),
            ("• Uploads most recent contact\n", 'bullet'),
            ("• Good for selective uploads\n\n", 'bullet'),

            ("What Gets Uploaded:\n", 'heading'),
            ("All contact details:\n", ()),
            ("• Callsign, date, time\n", 'bullet'),
            ("• Frequency, band, mode\n", 'bullet'),
            ("• RST sent/received\n", 'bullet'),
            ("• Name, QTH, grid\n", 'bullet'),
            ("• Power, notes\n\n", 'bullet'),

            ("Benefits:\n", 'heading'),
            ("• Keep QRZ logbook synced automatically\n", 'bullet'),
            ("• Access log from anywhere via QRZ website\n", 'bullet'),
            ("• Share with QRZ users\n", 'bullet'),
            ("• Backup in cloud\n\n", 'bullet'),

            ("Troubleshooting:\n", 'heading'),
            ("• Upload fails? Check API key\n", 'bullet'),
            ("• Duplicate QSOs? Normal if re-uploading\n", 'bullet'),
            ("• See ", ()), ("QRZ Troubleshooting", 'link', 'link_qrz_issues'), ("\n\n", ()),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QRZ Setup", 'link', 'link_qrz_setup'), ("\n", ()),
            ("• ", ()), ("ADIF Export", 'link', 'link_adif_export'), (" - Bulk upload alternative\n", ())
        ]

    @staticmethod
    def space_weather_overview():
        return [
            ("Space Weather Overview\n", 'title'),
            ("\nReal-time solar and geomagnetic conditions for HF propagation forecasting.\n\n", ()),

            ("Location: Space Weather tab\n\n", 'italic'),

            ("What is Space Weather?\n", 'heading'),
            ("Space weather refers to solar activity that affects radio wave propagation on Earth. Key factors:\n", ()),
            ("• Solar flux - Sun's radio emissions\n", 'bullet'),
            ("• Sunspot numbers - Solar activity level\n", 'bullet'),
            ("• Geomagnetic indices (K/A) - Earth's magnetic field disturbances\n", 'bullet'),
            ("• Solar flares - Sudden radiation bursts\n", 'bullet'),
            ("• CMEs - Coronal Mass Ejections\n\n", 'bullet'),

            ("Data Sources:\n", 'heading'),
            ("The app integrates three data sources:\n", ()),
            ("• HamQSL.com (N0NBH) - Solar indices\n", 'bullet'),
            ("• NOAA SWPC - Space weather predictions\n", 'bullet'),
            ("• NASA DONKI - Event alerts and warnings\n\n", 'bullet'),

            ("Displayed Information:\n", 'heading'),
            ("• Solar Flux Index (SFI) - Higher = better propagation\n", 'bullet'),
            ("• Sunspot Number (SSN) - Solar activity indicator\n", 'bullet'),
            ("• A-Index - 24-hour geomagnetic activity (lower = better)\n", 'bullet'),
            ("• K-Index - 3-hour geomagnetic activity (0-9 scale)\n", 'bullet'),
            ("• Solar Wind speed\n", 'bullet'),
            ("• X-Ray flux\n\n", 'bullet'),

            ("NASA DONKI Alerts:\n", 'heading'),
            ("Real-time space weather events:\n", ()),
            ("• Solar flare alerts (M-class, X-class)\n", 'bullet'),
            ("• CME tracking and predictions\n", 'bullet'),
            ("• Geomagnetic storm warnings\n", 'bullet'),
            ("• Radio blackout predictions\n\n", 'bullet'),

            ("Band Conditions:\n", 'heading'),
            ("Forecast for day and night:\n", ()),
            ("• 80m-40m bands\n", 'bullet'),
            ("• 30m-20m bands\n", 'bullet'),
            ("• 17m-15m bands\n", 'bullet'),
            ("• 12m-10m bands\n", 'bullet'),
            ("• Color-coded: Good/Fair/Poor\n\n", 'bullet'),

            ("Auto-Refresh:\n", 'heading'),
            ("• Data refreshes every 5 minutes\n", 'bullet'),
            ("• 24-hour cache minimizes API calls\n", 'bullet'),
            ("• Manual refresh available\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("NASA API Setup", 'link', 'link_nasa_api'), ("\n", ()),
            ("• ", ()), ("Propagation", 'link', 'link_propagation'), ("\n", ())
        ]

    @staticmethod
    def nasa_api():
        return [
            ("NASA API Configuration\n", 'title'),
            ("\nGet space weather alerts and forecasts from NASA's DONKI system.\n\n", ()),

            ("Location: Settings tab → NASA Space Weather API\n\n", 'italic'),

            ("Getting Your API Key:\n", 'heading'),
            ("1. Visit https://api.nasa.gov/\n", 'numbered'),
            ("2. Click 'Get Your API Key' or 'Generate API Key'\n", 'numbered'),
            ("3. Fill out simple form (name and email)\n", 'numbered'),
            ("4. Receive API key instantly\n", 'numbered'),
            ("5. Copy the key\n\n", 'numbered'),

            ("Configuration:\n", 'heading'),
            ("1. Open Settings tab\n", 'numbered'),
            ("2. Find NASA Space Weather API section\n", 'numbered'),
            ("3. Paste your API key\n", 'numbered'),
            ("4. Set cache duration (default 24 hours)\n", 'numbered'),
            ("5. Save settings\n\n", 'numbered'),

            ("Default API Key:\n", 'heading'),
            ("A demo API key is included, but has strict rate limits. Getting your own key (free) provides:\n", ()),
            ("• Higher rate limits\n", 'bullet'),
            ("• More reliable access\n", 'bullet'),
            ("• Better performance\n\n", 'bullet'),

            ("Cache Duration:\n", 'heading'),
            ("Set how long to cache NASA data:\n", ()),
            ("• 24 hours (default) - Good balance\n", 'bullet'),
            ("• 12 hours - More frequent updates\n", 'bullet'),
            ("• 48 hours - Less API calls\n\n", 'bullet'),

            ("What You Get:\n", 'heading'),
            ("With NASA API configured:\n", ()),
            ("• Solar flare alerts\n", 'bullet'),
            ("• CME tracking\n", 'bullet'),
            ("• Geomagnetic storm forecasts\n", 'bullet'),
            ("• Solar Energetic Particle events\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Space Weather", 'link', 'link_space_weather_overview'), ("\n", ()),
            ("• ", ()), ("Settings", 'link', 'link_station_info'), ("\n", ())
        ]

    @staticmethod
    def propagation():
        return [
            ("HF Propagation Forecasts\n", 'title'),
            ("\nUnderstanding and using band condition forecasts.\n\n", ()),

            ("Location: Space Weather tab → Band Conditions\n\n", 'italic'),

            ("What Affects Propagation?\n", 'heading'),
            ("• Solar flux - Higher = better HF propagation\n", 'bullet'),
            ("• Sunspot number - More sunspots = better high bands\n", 'bullet'),
            ("• K-Index - Higher = worse propagation (geomagnetic storms)\n", 'bullet'),
            ("• A-Index - Magnetic field disturbances\n", 'bullet'),
            ("• Time of day - Day vs night propagation differs\n\n", 'bullet'),

            ("Reading Conditions:\n", 'heading'),
            ("The app shows forecast for each band:\n", ()),
            ("• Good (Green) - Excellent propagation expected\n", 'bullet'),
            ("• Fair (Yellow) - Moderate conditions\n", 'bullet'),
            ("• Poor (Red) - Difficult propagation\n\n", 'bullet'),

            ("Day vs Night:\n", 'heading'),

            ("Daytime Propagation:\n", 'subheading'),
            ("• Higher bands better (20m-10m)\n", 'bullet'),
            ("• 40m/80m limited to regional\n", 'bullet'),
            ("• 10m/15m can be amazing with high solar flux\n\n", 'bullet'),

            ("Nighttime Propagation:\n", 'subheading'),
            ("• Lower bands better (40m/80m/160m)\n", 'bullet'),
            ("• 20m transitions day/night\n", 'bullet'),
            ("• 10m/15m usually dead at night\n\n", 'bullet'),

            ("Solar Flux Index (SFI):\n", 'heading'),
            ("• < 70: Very poor, mainly 40m/80m\n", 'bullet'),
            ("• 70-100: Fair, 20m okay\n", 'bullet'),
            ("• 100-150: Good, 15m/20m excellent\n", 'bullet'),
            ("• 150+: Excellent, 10m/12m open\n\n", 'bullet'),

            ("K-Index (Geomagnetic):\n", 'heading'),
            ("• 0-1: Quiet, excellent propagation\n", 'bullet'),
            ("• 2-3: Unsettled, good propagation\n", 'bullet'),
            ("• 4-5: Active, degraded propagation\n", 'bullet'),
            ("• 6-7: Storm, poor propagation\n", 'bullet'),
            ("• 8-9: Severe storm, very poor\n\n", 'bullet'),

            ("Using Forecasts:\n", 'heading'),
            ("• Check before contests\n", 'bullet'),
            ("• Plan DX attempts for good conditions\n", 'bullet'),
            ("• Adjust band selection based on forecast\n", 'bullet'),
            ("• Watch for sudden changes (flares)\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Space Weather", 'link', 'link_space_weather_overview'), ("\n", ()),
            ("• ", ()), ("NASA API", 'link', 'link_nasa_api'), ("\n", ())
        ]

    @staticmethod
    def station_info():
        return [
            ("Station Information Settings\n", 'title'),
            ("\nConfigure your station details used throughout the application.\n\n", ()),

            ("Location: Settings tab → Station Information\n\n", 'italic'),

            ("Required Settings:\n", 'heading'),

            ("Your Callsign:\n", 'subheading'),
            ("• Your amateur radio call sign\n", 'bullet'),
            ("• Used for contest logging, DX cluster login\n", 'bullet'),
            ("• Example: W4GNS, N1ABC, K2XYZ\n\n", 'bullet'),

            ("Optional But Recommended:\n", 'heading'),

            ("Operator Name:\n", 'subheading'),
            ("• Your full name for award applications\n", 'bullet'),
            ("• Example: John Smith\n\n", 'bullet'),

            ("Grid Square:\n", 'subheading'),
            ("• Maidenhead grid locator\n", 'bullet'),
            ("• 4 or 6 character format\n", 'bullet'),
            ("• Example: EM73, FN20ab\n\n", 'bullet'),

            ("SKCC Number:\n", 'subheading'),
            ("• Your SKCC membership number if member\n", 'bullet'),
            ("• Include suffix (C/T/S) if earned\n", 'bullet'),
            ("• Example: 12345, 12345C, 12345T\n\n", 'bullet'),

            ("Default RST:\n", 'subheading'),
            ("• Signal report sent by default\n", 'bullet'),
            ("• 59 for phone, 599 for CW\n", 'bullet'),
            ("• Can be overridden per QSO\n\n", 'bullet'),

            ("Default Power:\n", 'subheading'),
            ("• Your typical transmit power in watts\n", 'bullet'),
            ("• Example: 100, 5, 1500\n\n", 'bullet'),

            ("Zip Code:\n", 'subheading'),
            ("• For local weather display\n", 'bullet'),
            ("• US zip codes only\n\n", 'bullet'),

            ("SKCC Award Dates:\n", 'heading'),
            ("Critical for award tracking:\n\n", ()),

            ("Join Date (YYYYMMDD):\n", 'subheading'),
            ("• When you joined SKCC\n", 'bullet'),
            ("• Required for ALL awards\n", 'bullet'),
            ("• Example: 20240115\n\n", 'bullet'),

            ("Centurion Date (YYYYMMDD):\n", 'subheading'),
            ("• When you earned Centurion\n", 'bullet'),
            ("• Required for Tribune/Senator tracking\n", 'bullet'),
            ("• QSOs before this don't count for T/S\n\n", 'bullet'),

            ("Tribune x8 Date (YYYYMMDD):\n", 'subheading'),
            ("• When you earned Tribune x8\n", 'bullet'),
            ("• Required for Senator tracking\n", 'bullet'),
            ("• QSOs before this don't count for Senator\n\n", 'bullet'),

            ("Saving Settings:\n", 'heading'),
            ("• Click 'Save Settings' button\n", 'bullet'),
            ("• Settings persist across sessions\n", 'bullet'),
            ("• Stored in config.json\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("First Time Setup", 'link', 'link_first_time_setup'), ("\n", ()),
            ("• ", ()), ("SKCC Awards", 'link', 'link_skcc_awards'), ("\n", ())
        ]

    @staticmethod
    def preferences():
        return [
            ("Logging Preferences\n", 'title'),
            ("\nCustomize how the logging interface behaves.\n\n", ()),

            ("Location: Settings tab → Logging Preferences\n\n", 'italic'),

            ("Available Preferences:\n", 'heading'),

            ("Auto-lookup:\n", 'subheading'),
            ("• Automatically lookup callsigns when entered\n", 'bullet'),
            ("• Requires QRZ XML subscription\n", 'bullet'),
            ("• Fills name, QTH, grid automatically\n", 'bullet'),
            ("• Recommended: Enabled\n\n", 'bullet'),

            ("Warn duplicates:\n", 'subheading'),
            ("• Show warning for duplicate contacts\n", 'bullet'),
            ("• Checks same call/band/mode/day\n", 'bullet'),
            ("• Prevents accidental re-logging\n", 'bullet'),
            ("• Recommended: Enabled\n\n", 'bullet'),

            ("Auto-fill Time OFF:\n", 'subheading'),
            ("• Automatically set end time when logging\n", 'bullet'),
            ("• Sets to current UTC time\n", 'bullet'),
            ("• Most contacts have same ON/OFF time\n", 'bullet'),
            ("• Recommended: Enabled\n\n", 'bullet'),

            ("DX Cluster Preferences:\n", 'heading'),

            ("Selected Cluster:\n", 'subheading'),
            ("• Choose default DX cluster\n", 'bullet'),
            ("• 20+ clusters available\n", 'bullet'),
            ("• Example: AE5E, W3LPL\n\n", 'bullet'),

            ("Auto-connect on startup:\n", 'subheading'),
            ("• Connect to cluster automatically\n", 'bullet'),
            ("• Saves time if you always use clusters\n\n", 'bullet'),

            ("Spot Filters:\n", 'subheading'),
            ("• Which bands to show\n", 'bullet'),
            ("• Which continents to include\n", 'bullet'),
            ("• Saved per session\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Station Info", 'link', 'link_station_info'), ("\n", ()),
            ("• ", ()), ("QRZ Setup", 'link', 'link_qrz_setup'), ("\n", ())
        ]

    @staticmethod
    def backup():
        return [
            ("Google Drive Auto-Backup\n", 'title'),
            ("\nAutomatic cloud backups of your log to Google Drive.\n\n", ()),

            ("Location: Settings tab → Google Drive Auto-Backup\n\n", 'italic'),

            ("Features:\n", 'heading'),
            ("• Automatic scheduled backups\n", 'bullet'),
            ("• Secure OAuth authentication\n", 'bullet'),
            ("• Configurable backup interval\n", 'bullet'),
            ("• Automatic backup rotation\n", 'bullet'),
            ("• Database and config backups\n\n", 'bullet'),

            ("Setup Process:\n", 'heading'),
            ("1. Click 'Authenticate with Google'\n", 'numbered'),
            ("2. Sign in to your Google account\n", 'numbered'),
            ("3. Grant permissions to app\n", 'numbered'),
            ("4. Set backup interval (hours)\n", 'numbered'),
            ("5. Set max backups to keep\n", 'numbered'),
            ("6. Enable 'Include config file'\n", 'numbered'),
            ("7. Save settings\n\n", 'numbered'),

            ("Configuration Options:\n", 'heading'),

            ("Backup Interval:\n", 'subheading'),
            ("• How often to backup (in hours)\n", 'bullet'),
            ("• Example: 24 = daily, 168 = weekly\n", 'bullet'),
            ("• Minimum: 1 hour\n\n", 'bullet'),

            ("Max Backups:\n", 'subheading'),
            ("• How many old backups to keep\n", 'bullet'),
            ("• Older backups automatically deleted\n", 'bullet'),
            ("• Example: 7 = keep last 7 backups\n\n", 'bullet'),

            ("Include Config:\n", 'subheading'),
            ("• Also backup config.json file\n", 'bullet'),
            ("• Includes all settings\n", 'bullet'),
            ("• Recommended: Enabled\n\n", 'bullet'),

            ("Manual Backup:\n", 'heading'),
            ("• Click 'Backup Now' for immediate backup\n", 'bullet'),
            ("• Useful before major changes\n\n", 'bullet'),

            ("Restore Process:\n", 'heading'),
            ("1. Download backup from Google Drive\n", 'numbered'),
            ("2. Close application\n", 'numbered'),
            ("3. Replace logger.db with backup\n", 'numbered'),
            ("4. Restart application\n\n", 'numbered'),

            ("Security:\n", 'heading'),
            ("• OAuth 2.0 secure authentication\n", 'bullet'),
            ("• App only accesses its own files\n", 'bullet'),
            ("• No password stored locally\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("ADIF Export", 'link', 'link_adif_export'), (" - Alternative backup\n", ())
        ]

    @staticmethod
    def themes():
        return [
            ("Themes and Appearance\n", 'title'),
            ("\nCustomize the visual appearance of the application.\n\n", ()),

            ("Location: Settings tab → Appearance\n\n", 'italic'),

            ("Available Themes:\n", 'heading'),

            ("Light Theme (Default):\n", 'subheading'),
            ("• Traditional light background\n", 'bullet'),
            ("• Dark text on light background\n", 'bullet'),
            ("• Good for daytime use\n", 'bullet'),
            ("• Easy on paper printouts\n\n", 'bullet'),

            ("Dark Theme:\n", 'subheading'),
            ("• Dark background\n", 'bullet'),
            ("• Light text on dark background\n", 'bullet'),
            ("• Easier on eyes at night\n", 'bullet'),
            ("• Reduces screen glare\n\n", 'bullet'),

            ("Changing Themes:\n", 'heading'),
            ("1. Go to Settings tab\n", 'numbered'),
            ("2. Find Appearance section\n", 'numbered'),
            ("3. Select Light or Dark\n", 'numbered'),
            ("4. Theme applies immediately\n", 'numbered'),
            ("5. Preference saved automatically\n\n", 'numbered'),

            ("Theme Affects:\n", 'heading'),
            ("• All tabs and windows\n", 'bullet'),
            ("• Buttons and controls\n", 'bullet'),
            ("• Tables and lists\n", 'bullet'),
            ("• Help dialog\n", 'bullet'),
            ("• All UI elements\n\n", 'bullet'),

            ("Tips:\n", 'heading'),
            ("• Use Dark theme for night logging\n", 'bullet'),
            ("• Use Light theme for daytime\n", 'bullet'),
            ("• Switch anytime without restart\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Settings", 'link', 'link_station_info'), ("\n", ())
        ]

    @staticmethod
    def monthly_brag_report():
        return [
            ("Monthly Brag Report\n", 'title'),
            ("\nSee ", ()), ("Using Monthly Brag Report", 'link', 'link_brag_usage'), (" for complete instructions.\n\n", ()),
            ("This is the same as the Monthly Brag feature.\n\n", ()),
            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Monthly Brag Overview", 'link', 'link_brag_overview'), ("\n", ()),
            ("• ", ()), ("Using the Report", 'link', 'link_brag_usage'), ("\n", ()),
            ("• ", ()), ("Submitting Results", 'link', 'link_brag_submission'), ("\n", ())
        ]

    @staticmethod
    def qrz_issues():
        return [
            ("QRZ Troubleshooting\n", 'title'),
            ("\nCommon QRZ.com integration issues and solutions.\n\n", ()),

            ("Problem: Connection Test Fails\n", 'heading'),
            ("Symptoms: 'Test QRZ Connection' shows error\n\n", ()),
            ("Solutions:\n", 'subheading'),
            ("• Verify username/password correct\n", 'bullet'),
            ("• Check XML subscription is active\n", 'bullet'),
            ("• Verify internet connection\n", 'bullet'),
            ("• Try logging into qrz.com website directly\n", 'bullet'),
            ("• Check subscription hasn't expired\n\n", 'bullet'),

            ("Problem: Lookups Not Working\n", 'heading'),
            ("Symptoms: Callsign lookup returns no data\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Verify XML subscription active (not just basic account)\n", 'bullet'),
            ("• Check credentials configured correctly\n", 'bullet'),
            ("• Enable 'Auto-lookup' in Settings\n", 'bullet'),
            ("• Some callsigns may not be in QRZ database\n", 'bullet'),
            ("• Try manual lookup button\n\n", 'bullet'),

            ("Problem: Upload Fails\n", 'heading'),
            ("Symptoms: 'Upload to QRZ' shows error\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Verify API key configured\n", 'bullet'),
            ("• Check API key is correct (copy/paste from QRZ)\n", 'bullet'),
            ("• Ensure internet connection active\n", 'bullet'),
            ("• Check QRZ logbook is accessible\n", 'bullet'),
            ("• Try uploading via ADIF export as alternative\n\n", 'bullet'),

            ("Problem: Slow Lookups\n", 'heading'),
            ("Symptoms: Lookups take 5+ seconds\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Check internet speed\n", 'bullet'),
            ("• QRZ servers may be busy\n", 'bullet'),
            ("• Try different time of day\n", 'bullet'),
            ("• Consider disabling auto-lookup for manual control\n\n", 'bullet'),

            ("Error Messages:\n", 'heading'),

            ("'Invalid username or password':\n", 'subheading'),
            ("• Double-check credentials\n", 'bullet'),
            ("• Password is case-sensitive\n", 'bullet'),
            ("• Try resetting password on QRZ website\n\n", 'bullet'),

            ("'Subscription required':\n", 'subheading'),
            ("• XML subscription needed for lookups\n", 'bullet'),
            ("• Purchase at qrz.com/i/subscriptions.html\n", 'bullet'),
            ("• Free accounts don't include XML access\n\n", 'bullet'),

            ("'Network error':\n", 'subheading'),
            ("• Check internet connection\n", 'bullet'),
            ("• Firewall may be blocking\n", 'bullet'),
            ("• Try ping qrz.com to verify connectivity\n\n", 'bullet'),

            ("Still Having Issues?\n", 'heading'),
            ("• Visit QRZ support at qrz.com/support\n", 'bullet'),
            ("• Check QRZ system status\n", 'bullet'),
            ("• Verify your subscription status on QRZ website\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QRZ Setup", 'link', 'link_qrz_setup'), ("\n", ()),
            ("• ", ()), ("Common Problems", 'link', 'link_common_problems'), ("\n", ())
        ]

    @staticmethod
    def cluster_issues():
        return [
            ("DX Cluster Troubleshooting\n", 'title'),
            ("\nSolve connection and performance issues with DX clusters.\n\n", ()),

            ("Problem: Can't Connect\n", 'heading'),
            ("Symptoms: Connection fails or times out\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Verify callsign entered correctly\n", 'bullet'),
            ("• Try different cluster from list\n", 'bullet'),
            ("• Check internet connection\n", 'bullet'),
            ("• Firewall may block ports 7300 or 7373\n", 'bullet'),
            ("• Some clusters may be down temporarily\n\n", 'bullet'),

            ("Problem: Connection Drops\n", 'heading'),
            ("Symptoms: Connected but then disconnects\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Network instability - check connection\n", 'bullet'),
            ("• Cluster may have kicked idle connections\n", 'bullet'),
            ("• Reconnect - it happens occasionally\n", 'bullet'),
            ("• Try cluster geographically closer\n\n", 'bullet'),

            ("Problem: No Spots Appearing\n", 'heading'),
            ("Symptoms: Connected but table empty\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Check band filters - may have all unchecked\n", 'bullet'),
            ("• Check continent filters\n", 'bullet'),
            ("• May be quiet time (middle of night)\n", 'bullet'),
            ("• Try different cluster with more activity\n\n", 'bullet'),

            ("Problem: Too Many Spots\n", 'heading'),
            ("Symptoms: Spot table overwhelmed\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Use band filters to show only desired bands\n", 'bullet'),
            ("• Use continent filters to reduce volume\n", 'bullet'),
            ("• RBN clusters generate many automated spots\n", 'bullet'),
            ("• Consider traditional cluster instead\n\n", 'bullet'),

            ("Problem: Commands Don't Work\n", 'heading'),
            ("Symptoms: Commands return errors or no response\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Different cluster software supports different commands\n", 'bullet'),
            ("• DX Spider uses SH/ prefix\n", 'bullet'),
            ("• AR-Cluster uses SHOW\n", 'bullet'),
            ("• Type HELP to see cluster-specific commands\n\n", 'bullet'),

            ("Firewall Configuration:\n", 'heading'),
            ("If firewall blocking:\n", ()),
            ("• Allow outbound TCP port 7300\n", 'bullet'),
            ("• Allow outbound TCP port 7373\n", 'bullet'),
            ("• Allow W4GNS Logger application\n\n", 'bullet'),

            ("Cluster Selection Tips:\n", 'heading'),
            ("• Choose cluster near your location\n", 'bullet'),
            ("• RBN clusters best for CW activity\n", 'bullet'),
            ("• Traditional clusters for all modes\n", 'bullet'),
            ("• If one doesn't work, try another\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Connecting to Clusters", 'link', 'link_cluster_connect'), ("\n", ()),
            ("• ", ()), ("Common Problems", 'link', 'link_common_problems'), ("\n", ())
        ]

    @staticmethod
    def database_issues():
        return [
            ("Database Troubleshooting\n", 'title'),
            ("\nResolve issues with the SQLite database.\n\n", ()),

            ("Problem: Database Locked Error\n", 'heading'),
            ("Symptoms: 'Database is locked' message\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Close other instances of the app\n", 'bullet'),
            ("• Check no other program accessing logger.db\n", 'bullet'),
            ("• Restart application\n", 'bullet'),
            ("• Reboot computer if persists\n\n", 'bullet'),

            ("Problem: Database Corruption\n", 'heading'),
            ("Symptoms: 'Database disk image is malformed'\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("1. Close application immediately\n", 'numbered'),
            ("2. Copy logger.db to backup location\n", 'numbered'),
            ("3. Try: sqlite3 logger.db '.dump' | sqlite3 new_logger.db\n", 'numbered'),
            ("4. Replace old database with new one\n", 'numbered'),
            ("5. If fails, restore from backup\n\n", 'numbered'),

            ("Problem: Missing Contacts\n", 'heading'),
            ("Symptoms: Contacts disappeared from log\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Check Contacts tab filters\n", 'bullet'),
            ("• Verify sorting - may be at bottom\n", 'bullet'),
            ("• Check date range if filtered\n", 'bullet'),
            ("• Restore from backup if actually deleted\n\n", 'bullet'),

            ("Problem: Import Fails\n", 'heading'),
            ("Symptoms: ADIF import shows errors\n\n", ()),

            ("Solutions:\n", 'subheading'),
            ("• Verify ADIF file format valid\n", 'bullet'),
            ("• Check file not corrupted\n", 'bullet'),
            ("• Try smaller batch imports\n", 'bullet'),
            ("• Examine error message for specific field\n\n", 'bullet'),

            ("Prevention:\n", 'heading'),
            ("Protect your database:\n", ()),
            ("• Regular ADIF exports\n", 'bullet'),
            ("• Enable Google Drive backup\n", 'bullet'),
            ("• Manual backups before major changes\n", 'bullet'),
            ("• Keep external backup drive copy\n", 'bullet'),
            ("• Never edit logger.db directly\n\n", 'bullet'),

            ("Backup Locations:\n", 'heading'),
            ("App creates automatic backups:\n", ()),
            ("• logs/ directory (last 5 backups)\n", 'bullet'),
            ("• Google Drive (if configured)\n", 'bullet'),
            ("• On shutdown\n\n", 'bullet'),

            ("Recovery Steps:\n", 'heading'),
            ("If database totally broken:\n", ()),
            ("1. Find most recent backup\n", 'numbered'),
            ("2. Close application\n", 'numbered'),
            ("3. Rename broken logger.db to logger.db.bad\n", 'numbered'),
            ("4. Copy backup to logger.db\n", 'numbered'),
            ("5. Restart application\n\n", 'numbered'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("ADIF Export", 'link', 'link_adif_export'), (" - Manual backups\n", ()),
            ("• ", ()), ("Google Drive Backup", 'link', 'link_backup'), ("\n", ())
        ]

    @staticmethod
    def common_problems():
        return [
            ("Common Problems and Solutions\n", 'title'),
            ("\nFrequently asked questions and quick fixes.\n\n", ()),

            ("Installation and Startup:\n", 'heading'),

            ("Q: Application won't start\n", 'subheading'),
            ("A: Check Python 3.12+ installed. Run: python3 --version\n\n", ()),

            ("Q: Missing tkinter error\n", 'subheading'),
            ("A: Install tkinter:\n", ()),
            ("  Ubuntu: sudo apt-get install python3-tk\n", 'bullet'),
            ("  macOS: Included with Python from python.org\n", 'bullet'),
            ("  Windows: Included with Python installer\n\n", 'bullet'),

            ("Q: Import errors on startup\n", 'subheading'),
            ("A: Install dependencies: pip install -r requirements.txt\n\n", ()),

            ("Logging Issues:\n", 'heading'),

            ("Q: Callsign lookup not working\n", 'subheading'),
            ("A: Requires QRZ XML subscription. See ", ()), ("QRZ Setup", 'link', 'link_qrz_setup'), ("\n\n", ()),

            ("Q: Duplicate warning but not duplicate\n", 'subheading'),
            ("A: Check band and mode. Same call different band/mode is valid.\n\n", ()),

            ("Q: Can't log contact\n", 'subheading'),
            ("A: Verify required fields filled: callsign, date, time, frequency, mode.\n\n", ()),

            ("Q: Time showing wrong\n", 'subheading'),
            ("A: All times are UTC. Convert your local time to UTC.\n\n", ()),

            ("Contest Questions:\n", 'heading'),

            ("Q: Score seems wrong\n", 'subheading'),
            ("A: Verify bonus values updated monthly from SKCC website.\n\n", ()),

            ("Q: Duplicate on different band\n", 'subheading'),
            ("A: Per-band dupes only. Can work same call on different bands.\n\n", ()),

            ("Q: SKCC number not recognized\n", 'subheading'),
            ("A: Roster downloads automatically. Wait for download or check Settings.\n\n", ()),

            ("Awards Questions:\n", 'heading'),

            ("Q: Contacts not counting\n", 'subheading'),
            ("A: Configure SKCC join date in Settings. QSOs before join don't count.\n\n", ()),

            ("Q: Tribune/Senator not tracking\n", 'subheading'),
            ("A: Set Centurion date (for Tribune) and Tribune x8 date (for Senator).\n\n", ()),

            ("Q: Wrong endorsement level\n", 'subheading'),
            ("A: Check effective dates configured correctly in Settings.\n\n", ()),

            ("Export/Import Questions:\n", 'heading'),

            ("Q: Where's my exported file?\n", 'subheading'),
            ("A: Check location you selected in save dialog. Default is application directory.\n\n", ()),

            ("Q: ADIF won't import into other software\n", 'subheading'),
            ("A: File is ADIF 3.x compliant. Check other software's import settings.\n\n", ()),

            ("Q: Duplicate contacts after import\n", 'subheading'),
            ("A: Normal if re-importing same file. App skips duplicates automatically.\n\n", ()),

            ("Performance Issues:\n", 'heading'),

            ("Q: App running slow\n", 'subheading'),
            ("A: Large database? Try ADIF export, create new database, re-import recent QSOs.\n\n", ()),

            ("Q: DX cluster laggy\n", 'subheading'),
            ("A: Try cluster geographically closer. Reduce spot filters.\n\n", ()),

            ("Miscellaneous:\n", 'heading'),

            ("Q: Can I edit logged contacts?\n", 'subheading'),
            ("A: Not currently in UI. Export ADIF, edit, delete from log, re-import.\n\n", ()),

            ("Q: Can I run on Mac/Linux/Windows?\n", 'subheading'),
            ("A: Yes! Python 3.12+ works on all platforms.\n\n", ()),

            ("Q: Is my data safe?\n", 'subheading'),
            ("A: Enable Google Drive backup. Regular ADIF exports recommended.\n\n", ()),

            ("Still Need Help?\n", 'heading'),
            ("• Check specific troubleshooting topics\n", 'bullet'),
            ("• Review relevant help sections\n", 'bullet'),
            ("• Export ADIF as backup before major changes\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QRZ Issues", 'link', 'link_qrz_issues'), ("\n", ()),
            ("• ", ()), ("Cluster Issues", 'link', 'link_cluster_issues'), ("\n", ()),
            ("• ", ()), ("Database Issues", 'link', 'link_database_issues'), ("\n", ())
        ]

    @staticmethod
    def keyboard_reference():
        return [
            ("Keyboard Shortcuts Reference\n", 'title'),
            ("\nComplete list of keyboard shortcuts for faster operation.\n\n", ()),

            ("Global Shortcuts:\n", 'heading'),
            ("Ctrl+H - Open Help\n", 'bullet'),
            ("Alt+1 through Alt+9 - Switch between tabs\n\n", 'bullet'),

            ("Logging Tab:\n", 'heading'),
            ("Ctrl+Enter - Log Contact\n", 'bullet'),
            ("Esc - Clear Form\n", 'bullet'),
            ("Tab - Next Field (triggers auto-lookup on callsign)\n", 'bullet'),
            ("Shift+Tab - Previous Field\n\n", 'bullet'),

            ("Contest Tab:\n", 'heading'),
            ("Ctrl+Enter - Log Contact\n", 'bullet'),
            ("Esc - Clear Form\n\n", 'bullet'),

            ("DX Cluster Tab:\n", 'heading'),
            ("Enter - Send Command (in command field)\n\n", 'bullet'),

            ("Standard Text Editing:\n", 'heading'),
            ("Ctrl+C - Copy\n", 'bullet'),
            ("Ctrl+V - Paste\n", 'bullet'),
            ("Ctrl+X - Cut\n", 'bullet'),
            ("Ctrl+A - Select All\n\n", 'bullet'),

            ("Tips:\n", 'heading'),
            ("• Ctrl+Enter is fastest way to log contacts\n", 'bullet'),
            ("• Use Alt+number for quick tab switching\n", 'bullet'),
            ("• Tab through fields during QSO\n", 'bullet'),
            ("• Esc clears form and prepares for next QSO\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Keyboard Shortcuts", 'link', 'link_keyboard_shortcuts'), ("\n", ()),
            ("• ", ()), ("Logging QSOs", 'link', 'link_log_qso'), ("\n", ())
        ]

    @staticmethod
    def field_reference():
        return [
            ("QSO Field Reference\n", 'title'),
            ("\nComplete list of all 25+ contact logging fields.\n\n", ()),

            ("Required Fields:\n", 'heading'),
            ("• Callsign - Station contacted\n", 'bullet'),
            ("• Date - QSO date (YYYY-MM-DD)\n", 'bullet'),
            ("• Time ON/OFF - Start/end time UTC\n", 'bullet'),
            ("• Frequency - Operating frequency (MHz)\n", 'bullet'),
            ("• Band - Ham band (auto-filled)\n", 'bullet'),
            ("• Mode - CW, SSB, FT8, etc.\n\n", 'bullet'),

            ("Signal Reports:\n", 'heading'),
            ("• RST Sent - Signal report you sent\n", 'bullet'),
            ("• RST Received - Report you received\n\n", 'bullet'),

            ("Station Information:\n", 'heading'),
            ("• Name - Operator's first name\n", 'bullet'),
            ("• QTH - Their location\n", 'bullet'),
            ("• Grid - Maidenhead grid square\n", 'bullet'),
            ("• State - US state\n", 'bullet'),
            ("• County - US county\n", 'bullet'),
            ("• Country - DXCC entity\n", 'bullet'),
            ("• Continent - NA, EU, AS, etc.\n", 'bullet'),
            ("• CQ Zone - CQ magazine zone\n", 'bullet'),
            ("• ITU Zone - ITU zone\n\n", 'bullet'),

            ("Special Activities:\n", 'heading'),
            ("• SKCC Number - Straight Key Century Club\n", 'bullet'),
            ("• POTA - Parks On The Air reference\n", 'bullet'),
            ("• SOTA - Summits On The Air reference\n", 'bullet'),
            ("• IOTA - Islands On The Air reference\n\n", 'bullet'),

            ("Technical:\n", 'heading'),
            ("• Power - Transmit power (watts)\n", 'bullet'),
            ("• Propagation Mode - How signal traveled\n", 'bullet'),
            ("• Operator - Who operated (multi-op)\n\n", 'bullet'),

            ("Notes:\n", 'heading'),
            ("• Notes - Free-form comments, key type, rig, etc.\n\n", 'bullet'),

            ("Auto-Fill Fields:\n", 'heading'),
            ("These fields auto-fill from QRZ lookup:\n", ()),
            ("• Name, QTH, Grid, State, County\n", 'bullet'),
            ("• Country, Continent, Zones (from prefix)\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("QSO Fields", 'link', 'link_fields'), (" - Detailed explanations\n", ()),
            ("• ", ()), ("Auto-Lookup", 'link', 'link_auto_lookup'), ("\n", ())
        ]

    @staticmethod
    def cluster_commands_ref():
        return [
            ("DX Cluster Commands Reference\n", 'title'),
            ("\nCommon DX cluster commands. Type HELP on cluster for full list.\n\n", ()),

            ("Show Commands:\n", 'heading'),
            ("• SH/DX - Show recent DX spots\n", 'bullet'),
            ("• SH/DX 25 - Show last 25 spots\n", 'bullet'),
            ("• SH/DX on 20m - Spots on 20 meters\n", 'bullet'),
            ("• SH/DX K1ABC - Spots for specific call\n", 'bullet'),
            ("• SH/WWV - Propagation bulletins\n", 'bullet'),
            ("• SH/WCY - WCY propagation data\n", 'bullet'),
            ("• SH/SUN - Solar data\n", 'bullet'),
            ("• SH/MOON - Moon position\n", 'bullet'),
            ("• SH/QRZ W1AW - Lookup callsign\n", 'bullet'),
            ("• SH/PREFIX VP2 - DXCC prefix info\n", 'bullet'),
            ("• SH/ANNOUNCE - Recent announcements\n\n", 'bullet'),

            ("User Commands:\n", 'heading'),
            ("• SET/NAME John - Set your name\n", 'bullet'),
            ("• SET/QTH Tampa, FL - Set location\n", 'bullet'),
            ("• SET/HOMENODE W3LPL - Set home node\n\n", 'bullet'),

            ("Spotting:\n", 'heading'),
            ("• DX 14.250 W1AW - Spot W1AW on 14.250\n", 'bullet'),
            ("• DX 7.055 K1ABC SKCC 12345C - With comment\n", 'bullet'),
            ("• Only spot stations you've heard!\n\n", 'bullet'),

            ("Filters (if supported):\n", 'heading'),
            ("• ACCEPT/SPOTS on hf/cw - Only HF CW\n", 'bullet'),
            ("• REJECT/SPOTS on vhf - No VHF\n\n", 'bullet'),

            ("Utility:\n", 'heading'),
            ("• HELP - Show available commands\n", 'bullet'),
            ("• HELP SH/DX - Help for command\n", 'bullet'),
            ("• TIME - Current UTC time\n\n", 'bullet'),

            ("Notes:\n", 'heading'),
            ("• Commands NOT case-sensitive\n", 'bullet'),
            ("• SH = SHOW (abbreviation)\n", 'bullet'),
            ("• Cluster software varies - type HELP\n\n", 'bullet'),

            ("Related Topics:\n", 'heading'),
            ("• ", ()), ("Cluster Commands", 'link', 'link_cluster_commands'), (" - How to use\n", ()),
            ("• ", ()), ("Connecting", 'link', 'link_cluster_connect'), ("\n", ())
        ]
