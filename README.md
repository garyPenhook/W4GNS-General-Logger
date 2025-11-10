# W4GNS General Logger

Amateur Radio Contact Logging Application with DX Cluster Integration

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 📝 **Log4OM-Style Contact Logging**
- **Professional QSO entry interface** inspired by Log4OM
- **25+ fields supported**: Call, Date/Time, Freq, Band, Mode, RST, Power, Name, QTH, Grid, County, State, Country, Continent, CQ/ITU Zones, IOTA, SOTA, POTA, and more
- **Auto-lookup callsign information** using DXCC prefix database and QRZ.com
- **Duplicate contact detection** with real-time warnings
- **Frequency/band auto-correlation** - enter frequency, band auto-fills
- **Keyboard shortcuts**: Ctrl+Enter to log, Esc to clear
- **Smart auto-fill**: Date/time (UTC), power, RST from settings
- **ADIF 3.x import/export** compatible with LOTW, QRZ, eQSL, and other logging software
- **Date/Time range export** - Export contacts from specific time periods (perfect for contest logs and special events)
- SQLite database for fast, reliable local storage
- View 100 most recent contacts in sortable table

### 🔍 **QRZ.com Integration**
- **QRZ XML Lookup**: Auto-populate name, QTH, grid, state, county, zones
- **QRZ Logbook Upload**: Automatically or manually upload contacts
- **Test connection** from settings before use
- Requires QRZ username/password (XML subscription) and API key (for uploads)
- Full ADIF field support for uploads
- Upload status feedback

### 🌍 **DXCC Auto-Lookup**
- Automatic country/continent/zone lookup from callsign prefix
- Covers 40+ major DXCC entities worldwide
- Instant population of country, continent, CQ zone, ITU zone
- Works offline - no internet required
- Handles portable/mobile suffixes (/P, /M, /MM)

### 📡 **DX Cluster Integration**
- Connect to 10+ worldwide DX cluster nodes
- Real-time DX spot monitoring
- Clusters from North America, Europe, and Oceania
- Support for DXSpider, AR-Cluster, and Skimmer networks
- Send cluster commands directly from the interface
- Automatic spot parsing and display
- Cache spots in local database
- **SKCC member highlighting**: Spots for SKCC members with **Centurion (C)**, **Tribune (T)**, or **Senator (S)** suffixes are highlighted in **cyan** on the Logging tab

### ☀️ **Space Weather Integration**
- **Real-time solar and geomagnetic conditions** affecting HF propagation
- **NASA DONKI integration** for space weather event alerts:
  - Solar flare alerts (M-class and X-class)
  - Coronal Mass Ejection (CME) tracking
  - Geomagnetic storm warnings
  - Solar Energetic Particle (SEP) events
- **HF band condition forecasts** for day and night
- **Solar metrics**: Solar Flux Index, Sunspot Number, K-Index, A-Index, Solar Wind, X-Ray Flux
- **Configurable NASA API key** with 24-hour caching to minimize API calls
- Data from HamQSL.com (N0NBH), NOAA SWPC, and NASA DONKI
- Auto-refresh every 5 minutes

### ⚙️ **Configuration & Preferences**
- **Station Information**: Callsign, grid square, default power, default RST
- **QRZ Integration**: Username, password, API key, auto-upload toggle
- **NASA Space Weather**: API key configuration for DONKI event alerts
- **Logging Preferences**: Auto-lookup, duplicate warnings, auto time-off
- **DX Cluster Preferences**: Auto-connect, spot filtering (CW/SSB/Digital)
- **Google Drive Auto-Backup**: Automatic cloud backups with OAuth authentication
- All settings persist across sessions
- Test QRZ connection before saving credentials

## Available DX Clusters

The application includes connections to these DX clusters (sourced from [ng3k.com](https://www.ng3k.com/Misc/cluster.html) and [dxcluster.info](https://www.dxcluster.info/telnet/index.php)):

### USA RBN/Skimmer Clusters (Reverse Beacon Network)
These clusters provide automated CW spot detection via remote receivers.

| Callsign | Location | Type | Host | Port |
|----------|----------|------|------|------|
| AE5E | Thief River Falls, MN | DX Spider (+RBN) | dxspots.com | 7300 |
| K1AX-11 | N. Virginia | DX Spider (+RBN) | dxdata.io | 7300 |
| AI9T | Marshall, IL | DX Spider (+RBN) | dxc.ai9t.com | 7300 |
| K7TJ-1 | Spokane, WA | DX Spider (+RBN) | k7tj.ewarg.org | 7300 |
| AI6W-1 | Newcastle, CA | DX Spider (+RBN) | ai6w.net | 7300 |
| KB8PMY-3 | Hamilton, OH | DX Spider (+RBN) | kb8pmy.net | 7300 |
| K9LC | Rockford, IL | DX Spider (+RBN) | k9lc.ddns.net | 7300 |
| AE3N-2 | Virginia | DX Spider (+RBN) | dxc.ae3n.us | 7300 |
| K4GSO-2 | Ocala, FL | AR-Cluster (+RBN) | dxc.k4gso.com | 7373 |
| K2CAN | Oswego, NY | AR-Cluster (+RBN) | k2can.us | 7373 |
| NC7J | Syracuse, UT | CW/RTTY Skimmer | dxc.nc7j.com | 7373 |

### International RBN Clusters

| Callsign | Location | Type | Host | Port |
|----------|----------|------|------|------|
| G6NHU-2 | Essex, UK | DX Spider (RBN) | dxspider.co.uk | 7300 |
| DL8LAS | Kiel, Germany | Skimmer Server | dl8las.dyndns.org | 7300 |
| S50CLX | Slovenia | Multi-mode Skimmer | s50clx.infrax.si | 41112 |

### Traditional USA DX Clusters

| Callsign | Location | Type | Host | Port |
|----------|----------|------|------|------|
| W1NR | Marlborough, MA | DXSpider | dx.w1nr.net | 7300 |
| W1NR-9 | Marlborough, MA | DXSpider | usdx.w1nr.net | 7300 |
| K1TTT | Peru, MA | AR-Cluster | k1ttt.net | 7373 |
| W3LPL | Glenwood, MD | AR-Cluster v.6 | w3lpl.net | 7373 |
| W6RFU | Santa Barbara, CA | DX Spider | ucsbdx.ece.ucsb.edu | 7300 |

### International Traditional Clusters

| Callsign | Location | Type | Host | Port |
|----------|----------|------|------|------|
| ZL2ARN-10 | New Zealand | DXSpider | zl2arn.ddns.net | 7300 |

> **Note:** If you see "No RBN spots are available on this node" when connecting to a cluster, try one of the RBN/Skimmer clusters listed above. The application will automatically suggest alternatives when this occurs.

## Requirements

- Python 3.12 or higher
- tkinter (included with Python)
- External dependencies (see requirements.txt):
  - `requests` - For POTA API and NASA space weather data
  - `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client` - For Google Drive auto-backup (optional)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/garyPenhook/W4GNS-General-Logger.git
   cd W4GNS-General-Logger
   ```

2. **Install dependencies:**
   ```bash
   # Recommended: Use a virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # OR on Windows: venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python3 main.py
   ```

   Or make it executable:
   ```bash
   chmod +x main.py
   ./main.py
   ```

## Usage

### First Time Setup

**Station Information:**
1. Go to the **Settings** tab
2. Enter your callsign and grid square
3. Set default power and RST
4. Click "Save Settings"

**QRZ.com Setup (Optional but Recommended):**
1. Go to **Settings** → **QRZ.com Integration**
2. Enter your QRZ username and password (for XML lookups)
3. Enter your QRZ API key (get from QRZ.com → Logbook → Settings → API)
4. Enable "Auto-lookup" if you want automatic callsign lookups
5. Enable "Auto-upload" if you want contacts automatically uploaded to QRZ Logbook
6. Click "Test QRZ Connection" to verify credentials
7. Click "Save Settings"

**NASA Space Weather Setup (Optional):**
1. Go to **Settings** → **NASA Space Weather API**
2. Get a free API key from [https://api.nasa.gov/](https://api.nasa.gov/) (no rate limits)
3. Enter your NASA API key
4. Adjust cache duration if desired (default: 24 hours)
5. Click "Save Settings"
6. View real-time space weather in the **Space Weather** tab

**Note:** The app includes a default API key, but getting your own is recommended for best performance.

**Logging Preferences:**
1. Toggle "Auto-lookup" for automatic callsign information retrieval
2. Toggle "Warn duplicates" for duplicate contact warnings
3. Toggle "Auto-fill Time OFF" to automatically set end time when logging

### Logging Contacts (Log4OM-Style Interface)

**Quick Logging Workflow:**
1. Go to the **Log Contacts** tab
2. Enter **Callsign** - information auto-populates if lookup is enabled:
   - Country, continent, and zones from DXCC prefix
   - Name, QTH, grid, state, county from QRZ (if configured)
   - Duplicate warning if same call/band/mode today
3. Enter **Frequency** - band auto-selects (e.g., 14.250 → 20m)
4. Select **Mode** (SSB, CW, FT8, etc.)
5. Adjust **Time ON** if needed (auto-filled with UTC)
6. Fill optional fields:
   - **Power** (defaults from settings)
   - **RST Sent/Rcvd** (defaults from settings)
   - **Name, QTH, Grid** (may be pre-filled from QRZ)
   - **State, County** (US stations)
   - **IOTA, SOTA, POTA** (awards programs)
   - **Notes** (any additional info)
7. Click **"Log Contact"** or press **Ctrl+Enter**
8. Contact is saved and optionally uploaded to QRZ

**Keyboard Shortcuts:**
- **Ctrl+Enter**: Log the contact
- **Esc**: Clear the form
- **Tab**: Move between fields

**Features During Logging:**
- 🔴 **Duplicate Warning**: "⚠️ DUPLICATE - Worked on HH:MM" appears in red if dupe detected
- 🔍 **Manual Lookup**: Click "Lookup" button to force callsign lookup
- 📤 **QRZ Upload**: Click "Upload to QRZ" after logging (if not auto-uploading)
- 🔄 **Auto-Fill**: Date/time updates to current UTC, Time OFF auto-fills on log

**Contact Log Display:**
- View 100 most recent contacts
- Columns: Call, Date, Time, Freq, Mode, RST, Name, Country, Grid
- Scrollable list with all logged QSOs

### Using DX Clusters

1. Go to the **DX Clusters** tab
2. Ensure your callsign is entered in Settings first
3. Select a cluster from the dropdown
4. View cluster information (type, host, port, region)
5. Click "Connect"
6. Watch for real-time DX spots in the spots table
7. View cluster messages in the console window
8. Send commands using the command input:
   - `SH/DX` - Show recent DX spots
   - `SH/DX 14000-14350` - Show 20m spots
   - `SH/DX/20` - Show last 20 spots
   - Many other commands supported by your cluster

**SKCC Member Highlighting:**
On the **Log Contacts** tab, DX spots for SKCC members with special achievements are automatically highlighted:
- **Cyan background** = SKCC member with **Centurion (C)**, **Tribune (T)**, or **Senator (S)** award suffix
- This helps identify high-achievement SKCC operators at a glance
- Requires SKCC roster to be downloaded (Settings → SKCC Awards tab)

### Common DX Cluster Commands

- `SH/DX` - Show DX spots
- `SH/DX [band]` - Show spots for specific band
- `SH/WWV` - Show WWV propagation data
- `SH/WCY` - Show WCY propagation data
- `SH/SUN` - Show sunrise/sunset times
- `SH/MUF <prefix>` - Show MUF to location
- `BYE` or `QUIT` - Disconnect (or use Disconnect button)

### ADIF Import/Export

**Exporting Your Entire Log:**
1. Go to **File** menu → **Export Log (ADIF)...**
2. Choose a location and filename (`.adi` or `.adif` extension)
3. Click Save
4. All contacts will be exported in ADIF 3.x format
5. Use the exported file with:
   - LOTW (Logbook of the World)
   - QRZ.com logbook
   - eQSL
   - Other logging software (Log4OM, N1MM, etc.)

**Exporting by Date/Time Range (NEW!):**
Perfect for contest logs, special events, and field days:
1. Go to **File** menu → **Export by Date/Time Range (ADIF)...**
2. Select your date range using the dialog:
   - Enter start and end dates (YYYY-MM-DD format)
   - Optionally specify exact times (HH:MM format)
   - Or use quick presets: **Today**, **Yesterday**, **This Week**, **This Month**
3. Click **Export**
4. Choose a location and filename
5. Only contacts within the specified range will be exported

**Examples:**
- Export a weekend contest: Select Saturday 00:00 to Sunday 23:59
- Export a special event: Select the event date range
- Export SKCC WES weekend: Select the weekend dates
- Export monthly activity: Use "This Month" preset

**Exporting SKCC Contacts:**
1. Go to **File** menu → **Export SKCC Contacts (ADIF)...**
2. Only contacts with SKCC numbers will be exported
3. Includes SKCC-specific fields for award applications

**Importing a Log:**
1. Go to **File** menu → **Import Log (ADIF)...**
2. Select an ADIF file (`.adi` or `.adif`)
3. The file will be validated automatically
4. Review the number of contacts found
5. Click "Yes" to confirm import
6. Contacts will be added to your database
7. The log display will refresh automatically

**Note:** Duplicate checking (10-minute window) is performed during import to avoid duplicate contacts.

## Project Structure

```
W4GNS-General-Logger/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── LICENSE                          # MIT License
├── docs/                            # Documentation
│   └── GOOGLE_DRIVE_BACKUP_SETUP.md # Google Drive setup guide
└── src/
    ├── __init__.py
    ├── config.py                    # Configuration management
    ├── database.py                  # SQLite database layer (25+ fields)
    ├── adif.py                      # ADIF 3.x import/export
    ├── dxcc.py                      # DXCC prefix lookup (40+ entities)
    ├── qrz.py                       # QRZ.com API integration
    ├── space_weather.py             # NASA DONKI & NOAA space weather
    ├── google_drive_backup.py       # Google Drive OAuth backup
    ├── dx_clusters.py               # DX cluster definitions
    ├── dx_client.py                 # Telnet client for clusters
    └── gui/
        ├── __init__.py
        ├── logging_tab_enhanced.py  # Log4OM-style logging interface
        ├── contacts_tab.py          # Contact log viewer
        ├── dx_cluster_tab.py        # DX cluster interface
        ├── awards_tab.py            # ARRL awards tracking
        ├── skcc_awards_tab.py       # SKCC awards tracking
        ├── settings_tab.py          # Settings interface
        ├── date_range_dialog.py     # Date/time range selection dialog
        ├── space_weather_tab.py     # Space weather information
        └── weather_tab.py           # Weather information
```

## Database

The application uses SQLite to store:
- **Contacts**: All logged QSOs with full details
- **DX Spots**: Cached DX cluster spots

Database file: `logger.db` (created automatically in the application directory)

## Configuration

Settings are stored in `config.json` (created automatically).

Example configuration:
```json
{
  "callsign": "W4GNS",
  "gridsquare": "EM73",
  "default_rst": "59",
  "default_power": "100",
  "qrz": {
    "username": "YOUR_QRZ_USERNAME",
    "password": "YOUR_QRZ_PASSWORD",
    "api_key": "YOUR_QRZ_API_KEY",
    "auto_upload": false,
    "enable_lookup": true
  },
  "nasa": {
    "api_key": "YOUR_NASA_API_KEY",
    "donki_cache_hours": 24
  },
  "logging": {
    "auto_lookup": true,
    "warn_duplicates": true,
    "auto_time_off": true
  },
  "dx_cluster": {
    "selected": "W3LPL",
    "auto_connect": false,
    "show_cw_spots": true,
    "show_ssb_spots": true,
    "show_digital_spots": true
  },
  "google_drive": {
    "enabled": false,
    "backup_interval_hours": 24,
    "max_backups": 30,
    "include_config": true,
    "last_backup": null
  },
  "window": {
    "width": 1200,
    "height": 750
  }
}
```

## Development

Built with:
- **Python 3.12** - Modern Python features
- **tkinter** - Native cross-platform GUI
- **sqlite3** - Fast local database with 25+ fields
- **telnetlib** - DX cluster telnet connections
- **urllib** - QRZ.com API integration
- **requests** - HTTP client for NASA and POTA APIs
- **Google Drive API** - Optional cloud backup integration

**Modules:**
- `dxcc.py` - 40+ DXCC entities with prefix matching
- `qrz.py` - QRZ XML API and Logbook upload
- `adif.py` - Complete ADIF 3.x parser/generator
- `database.py` - SQLite ORM with duplicate detection
- `space_weather.py` - NASA DONKI and NOAA space weather integration
- `google_drive_backup.py` - OAuth-based cloud backup system
- `logging_tab_enhanced.py` - Log4OM-inspired interface

## Future Enhancements

Completed features:
- [x] ADIF 3.x import/export ✅
- [x] Date/time range export ✅
- [x] QRZ.com XML lookups ✅
- [x] QRZ.com Logbook upload ✅
- [x] DXCC prefix lookup ✅
- [x] Duplicate contact detection ✅
- [x] Log4OM-style interface ✅
- [x] SKCC awards tracking (all 11 awards) ✅
- [x] ARRL awards tracking ✅
- [x] Space weather integration with NASA DONKI ✅
- [x] Google Drive automatic backups ✅
- [x] Dark/Light themes ✅

Potential future features:
- [ ] Rig control (CAT interface via Hamlib)
- [ ] Contest logging modes (field day, sweepstakes, etc.)
- [ ] Digital mode integration (WSJT-X, JTDX, Fldigi)
- [ ] LOTW direct upload
- [ ] Logbook statistics and reports (DXCC progress, WAS, etc.)
- [ ] Multiple logbook support
- [ ] Duplicate contact detection on ADIF import
- [ ] HamQTH lookups (alternative to QRZ)
- [ ] eQSL integration
- [ ] Spot alerts and notifications
- [ ] Map display of worked countries/grids

## Troubleshooting

**QRZ lookups not working:**
- Verify QRZ username/password are correct
- Click "Test QRZ Connection" in Settings
- XML lookups require QRZ XML subscription ($)
- Check QRZ.com website is accessible
- Ensure "Enable lookup" is checked in Settings

**QRZ Logbook upload fails:**
- Verify API key is correct (get from QRZ.com → Logbook → Settings)
- API key is different from XML password
- Check you have QRZ Logbook access
- Test connection before uploading
- Check error message for specific reason

**Duplicate warnings not appearing:**
- Enable "Warn duplicates" in Settings → Logging Preferences
- Duplicate detection checks: call + band + mode + date
- Different modes on same band = not a duplicate
- Contact must have been logged today to show warning

**Auto-lookup not working:**
- Enable "Auto-lookup" in Settings → Logging Preferences
- Enter QRZ credentials for XML lookups
- DXCC lookup always works (offline, no credentials needed)
- Tab out of callsign field to trigger lookup

**Connection fails to DX cluster:**
- Check your internet connection
- Some clusters may be offline temporarily
- Try a different cluster from the list
- Ensure port is not blocked by firewall

**Application won't start:**
- Ensure Python 3.12+ is installed: `python3 --version`
- Check tkinter is available: `python3 -c "import tkinter"`
- Delete `config.json` if corrupted

**Database errors:**
- Check write permissions in application directory
- Existing databases will auto-upgrade to new schema
- Delete `logger.db` to start fresh (backup first!)
- Export to ADIF before deleting for safety

**Space weather not loading / NASA API errors:**
- Check your internet connection
- Verify NASA API key is configured in Settings
- Get a free API key at [https://api.nasa.gov/](https://api.nasa.gov/)
- Default DEMO_KEY has strict rate limits (30 requests/hour)
- Personal API key has higher limits (1000 requests/hour)
- Data is cached for 24 hours to minimize API calls
- Check console for specific error messages

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## Credits

- DX Cluster list sourced from [NG3K](https://www.ng3k.com/Misc/cluster.html)
- Built for the amateur radio community

## Contact

For questions or support, please open an issue on GitHub.

73! 📻