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

### ⚙️ **Configuration & Preferences**
- **Station Information**: Callsign, grid square, default power, default RST
- **QRZ Integration**: Username, password, API key, auto-upload toggle
- **Logging Preferences**: Auto-lookup, duplicate warnings, auto time-off
- **DX Cluster Preferences**: Auto-connect, spot filtering (CW/SSB/Digital)
- All settings persist across sessions
- Test QRZ connection before saving credentials

## Available DX Clusters

The application includes connections to these DX clusters (sourced from [ng3k.com](https://www.ng3k.com/Misc/cluster.html)):

| Callsign | Location | Type | Host | Port |
|----------|----------|------|------|------|
| NC7J | Syracuse, UT | CW/RTTY Skimmer | dxc.nc7j.com | 7373 |
| DL8LAS | Kiel, Germany | Skimmer Server | dl8las.dyndns.org | 7300 |
| W1NR | Marlborough, MA | DXSpider | dx.w1nr.net | 7300 |
| W1NR-9 | Marlborough, MA | DXSpider | usdx.w1nr.net | 7300 |
| K1TTT | Peru, MA | AR-Cluster | k1ttt.net | 7373 |
| W3LPL | Glenwood, MD | AR-Cluster v.6 | w3lpl.net | 7373 |
| W6RFU | Santa Barbara, CA | DX Spider | ucsbdx.ece.ucsb.edu | 7300 |
| G6NHU-2 | Essex, UK | DX Spider (RBN) | dxspider.co.uk | 7300 |
| S50CLX | Slovenia | Multi-mode Skimmer | s50clx.infrax.si | 41112 |
| ZL2ARN-10 | New Zealand | DXSpider | zl2arn.ddns.net | 7300 |

## Requirements

- Python 3.12 or higher
- tkinter (included with Python)
- Standard Python library only - no external dependencies!

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/garyPenhook/W4GNS-General-Logger.git
   cd W4GNS-General-Logger
   ```

2. **Run the application:**
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

### Common DX Cluster Commands

- `SH/DX` - Show DX spots
- `SH/DX [band]` - Show spots for specific band
- `SH/WWV` - Show WWV propagation data
- `SH/WCY` - Show WCY propagation data
- `SH/SUN` - Show sunrise/sunset times
- `SH/MUF <prefix>` - Show MUF to location
- `BYE` or `QUIT` - Disconnect (or use Disconnect button)

### ADIF Import/Export

**Exporting Your Log:**
1. Go to **File** menu → **Export Log (ADIF)...**
2. Choose a location and filename (`.adi` or `.adif` extension)
3. Click Save
4. All contacts will be exported in ADIF 3.x format
5. Use the exported file with:
   - LOTW (Logbook of the World)
   - QRZ.com logbook
   - eQSL
   - Other logging software (Log4OM, N1MM, etc.)

**Importing a Log:**
1. Go to **File** menu → **Import Log (ADIF)...**
2. Select an ADIF file (`.adi` or `.adif`)
3. The file will be validated automatically
4. Review the number of contacts found
5. Click "Yes" to confirm import
6. Contacts will be added to your database
7. The log display will refresh automatically

**Note:** Duplicate checking is not currently performed during import. Be careful not to import the same file multiple times.

## Project Structure

```
W4GNS-General-Logger/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── LICENSE                          # MIT License
└── src/
    ├── __init__.py
    ├── config.py                    # Configuration management
    ├── database.py                  # SQLite database layer (25+ fields)
    ├── adif.py                      # ADIF 3.x import/export
    ├── dxcc.py                      # DXCC prefix lookup (40+ entities)
    ├── qrz.py                       # QRZ.com API integration
    ├── dx_clusters.py               # DX cluster definitions
    ├── dx_client.py                 # Telnet client for clusters
    └── gui/
        ├── __init__.py
        ├── logging_tab_enhanced.py  # Log4OM-style logging interface
        ├── dx_cluster_tab.py        # DX cluster interface
        └── settings_tab.py          # Settings interface
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
- **Standard library only** - No external dependencies!

**Modules:**
- `dxcc.py` - 40+ DXCC entities with prefix matching
- `qrz.py` - QRZ XML API and Logbook upload
- `adif.py` - Complete ADIF 3.x parser/generator
- `database.py` - SQLite ORM with duplicate detection
- `logging_tab_enhanced.py` - Log4OM-inspired interface

## Future Enhancements

Completed features:
- [x] ADIF 3.x import/export ✅
- [x] QRZ.com XML lookups ✅
- [x] QRZ.com Logbook upload ✅
- [x] DXCC prefix lookup ✅
- [x] Duplicate contact detection ✅
- [x] Log4OM-style interface ✅

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