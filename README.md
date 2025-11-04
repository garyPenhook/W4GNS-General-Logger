# W4GNS General Logger

Amateur Radio Contact Logging Application with DX Cluster Integration

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 📝 Contact Logging
- Log amateur radio contacts with comprehensive details
- Store callsign, date/time, frequency, band, mode, RST reports
- Record operator name, QTH, grid square, and notes
- SQLite database for reliable local storage
- View complete contact history

### 📡 DX Cluster Integration
- Connect to 10+ worldwide DX cluster nodes
- Real-time DX spot monitoring
- Clusters from North America, Europe, and Oceania
- Support for DXSpider, AR-Cluster, and Skimmer networks
- Send cluster commands directly from the interface
- Automatic spot parsing and display
- Cache spots in local database

### ⚙️ Configuration
- Save your station information (callsign, grid square)
- Customize default RST reports
- Configure DX cluster preferences
- Filter spot types (CW, SSB, Digital)
- Persistent settings storage

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

1. Go to the **Settings** tab
2. Enter your callsign and grid square
3. Configure your preferences
4. Click "Save Settings"

### Logging Contacts

1. Go to the **Log Contacts** tab
2. Fill in contact details:
   - Callsign (required)
   - Date and time (auto-filled with current UTC)
   - Frequency, band, and mode
   - RST sent/received
   - Name, QTH, grid square
   - Optional notes
3. Click "Log Contact"
4. View all logged contacts in the table below

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

## Project Structure

```
W4GNS-General-Logger/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # MIT License
└── src/
    ├── __init__.py
    ├── config.py          # Configuration management
    ├── database.py        # SQLite database layer
    ├── dx_clusters.py     # DX cluster definitions
    ├── dx_client.py       # Telnet client for clusters
    └── gui/
        ├── __init__.py
        ├── logging_tab.py     # Contact logging interface
        ├── dx_cluster_tab.py  # DX cluster interface
        └── settings_tab.py    # Settings interface
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
  "dx_cluster": {
    "selected": "W3LPL",
    "auto_connect": false,
    "show_cw_spots": true,
    "show_ssb_spots": true,
    "show_digital_spots": true
  },
  "window": {
    "width": 1000,
    "height": 700
  }
}
```

## Development

Built with:
- Python 3.12
- tkinter for GUI
- sqlite3 for database
- telnetlib for cluster connections
- Standard library only!

## Future Enhancements

Potential features for future releases:
- [ ] ADIF import/export
- [ ] Rig control (CAT interface)
- [ ] QRZ.com lookups
- [ ] Contest logging modes
- [ ] Digital mode integration
- [ ] LOTW upload
- [ ] Logbook statistics and reports
- [ ] Multiple logbook support

## Troubleshooting

**Connection fails to DX cluster:**
- Check your internet connection
- Some clusters may be offline temporarily
- Try a different cluster from the list
- Ensure port is not blocked by firewall

**Application won't start:**
- Ensure Python 3.12+ is installed: `python3 --version`
- Check tkinter is available: `python3 -c "import tkinter"`

**Database errors:**
- Check write permissions in application directory
- Delete `logger.db` to start fresh (backs up your old file first!)

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