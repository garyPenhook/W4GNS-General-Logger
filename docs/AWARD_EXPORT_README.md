# SKCC Award Application Export

This guide explains how to export qualifying contacts for SKCC award applications.

## Overview

SKCC award managers require ADIF files containing **only the contacts that qualify** for the specific award being applied for. This tool automatically filters your logbook and exports only the qualifying contacts in ADIF format.

## Features

- ✅ **Automatic Filtering**: Only exports contacts that meet all award requirements
- ✅ **SKCC-Specific Fields**: Includes SKCC number, key type, duration, and distance
- ✅ **Award Identification**: Adds award name to contact comments for easy identification
- ✅ **Batch Export**: Export multiple awards at once
- ✅ **Achievement Detection**: Automatically detect which awards are ready for submission

## Quick Start

### Export a Specific Award

```bash
python3 export_award_application.py --award centurion --callsign W4GNS
```

### Export All Achieved Awards (Recommended)

```bash
python3 export_award_application.py --all-achieved --callsign W4GNS
```

This will automatically:
1. Check which awards you've completed (100% progress)
2. Export only those awards that are ready for submission
3. Skip awards that aren't finished yet

### List Available Awards

```bash
python3 export_award_application.py --list-awards
```

## Available Awards

| Award Name | Command Option | Description |
|------------|----------------|-------------|
| Centurion | `centurion` | Contact 100 different SKCC members |
| Tribune | `tribune` | Contact 50 Tribune/Senator members |
| Senator | `senator` | Contact 200 Tribune/Senator members |
| Triple Key | `triple-key` | Contact 100 members with each key type |
| Rag Chew | `rag-chew` | Accumulate 300 minutes of conversations |
| Marathon | `marathon` | 100 QSOs of 60+ minutes each |
| Canadian Maple | `canadian-maple` | Contact members in Canadian provinces |
| DXQ | `dxq` | QSO-based DX contacts |
| DXC | `dxc` | Country-based DX contacts |
| PFX | `pfx` | 500,000 points from prefixes |
| QRP MPW | `qrp-mpw` | Miles per watt achievement |
| WAS | `was` | All 50 US states |
| WAS-T | `was-t` | All 50 US states (Tribune/Senator) |
| WAS-S | `was-s` | All 50 US states (Senator only) |
| WAC | `wac` | All 6 continents |

## Command Line Options

```
--database PATH        Path to logbook database (default: logbook.db)
--award NAME          Export specific award
--all                 Export all awards (including incomplete)
--all-achieved        Export only 100% complete awards
--callsign CALL       Your callsign (included in filename)
--output DIR          Output directory (default: exports)
--list-awards         List all available awards
```

## Examples

### Export WAS-T Award
```bash
python3 export_award_application.py --award was-t --callsign K4ABC
```

Output: `exports/K4ABC_SKCC_WAS-T_Application_20250106_143022.adi`

### Export All Awards to Custom Directory
```bash
python3 export_award_application.py --all --callsign W4GNS --output ~/awards
```

### Check Which Awards Are Ready
```bash
python3 export_award_application.py --all-achieved --callsign W4GNS
```

This will show:
```
Exporting all achieved awards...

Exported 3 awards:
  ✓ Centurion          -> exports/W4GNS_Centurion_Application_20250106.adi
  ✓ Triple Key         -> exports/W4GNS_Triple_Key_Application_20250106.adi
  ✓ WAS                -> exports/W4GNS_SKCC_WAS_Application_20250106.adi
```

## ADIF File Contents

Each exported ADIF file includes:

### Standard Fields
- `CALL` - Callsign
- `QSO_DATE` - Date (YYYYMMDD format)
- `TIME_ON` - Start time
- `TIME_OFF` - End time (if logged)
- `BAND` - Operating band
- `MODE` - Operating mode (CW)
- `RST_SENT` / `RST_RCVD` - Signal reports
- `STATE` - US state (if applicable)
- `COUNTRY` - Country
- `DXCC` - DXCC entity

### SKCC-Specific Fields
- `APP_SKCC_NUMBER` - Remote station's SKCC number
- `APP_SKCC_KEY_TYPE` - Key used (STRAIGHT, BUG, SIDESWIPER)
- `APP_SKCC_DURATION` - QSO duration in minutes (for Rag Chew/Marathon)
- `APP_SKCC_DISTANCE` - Distance in miles (for QRP MPW)

### Award Identification
- `COMMENT` - Includes award name (e.g., "[Centurion Award]")

## Programmatic Usage

You can also use the export functionality in your own Python scripts:

```python
from src.database import Database
from src.skcc_awards import CenturionAward
from src.award_export import export_award_for_submission

# Open database
db = Database('logbook.db')

# Create award instance
award = CenturionAward(db)

# Export qualifying contacts
filepath = export_award_for_submission(
    award,
    db,
    callsign='W4GNS',
    output_directory='my_exports'
)

print(f"Exported to: {filepath}")
```

### Export All Achieved Awards Programmatically

```python
from src.database import Database
from src.award_export import export_all_awards

db = Database('logbook.db')

# Export only achieved awards
results = export_all_awards(
    db,
    callsign='W4GNS',
    only_achieved=True
)

for award_name, filepath in results.items():
    if filepath:
        print(f"{award_name}: {filepath}")
```

## Submitting to Award Managers

After exporting:

1. **Review the ADIF file** - Open in any ADIF viewer to verify contacts
2. **Check the count** - Ensure you have enough qualifying contacts
3. **Email to Award Manager** - Send the `.adi` file to the appropriate SKCC award manager
4. **Subject Line Format** - Use: `[Your Callsign] Application [Award Name]`
   - Example: `W4GNS Application Centurion`

### Award Manager Contact Information

Visit the SKCC website for current award manager email addresses:
- https://www.skccgroup.com/operating_awards/

## Validation Rules

Each award has specific validation rules. Exported files include **only** contacts that meet ALL requirements:

- ✅ CW mode
- ✅ Mechanical key (STRAIGHT, BUG, or SIDESWIPER)
- ✅ Both parties were SKCC members at time of contact
- ✅ QSO date after award effective date
- ✅ Award-specific requirements (duration, distance, member status, etc.)

## Troubleshooting

### "No qualifying contacts found"
- Check that you have logged the required fields (SKCC number, key type, etc.)
- Verify contacts meet the award's specific requirements
- Ensure contacts are after the award's effective date

### "Database not found"
- Specify the correct database path: `--database /path/to/logbook.db`

### Empty export directory
- Check that awards are actually achieved
- Use `--all-achieved` to only export complete awards
- Use `--all` to export all awards (even incomplete ones)

## Field Requirements by Award

| Award | Required Fields |
|-------|----------------|
| Centurion | callsign, qso_date, skcc_number, key_type |
| Rag Chew | callsign, qso_date, skcc_number, key_type, duration_minutes (≥30) |
| Marathon | callsign, qso_date, skcc_number, key_type, duration_minutes (≥60) |
| QRP MPW | callsign, qso_date, skcc_number, key_type, power_watts (≤5), distance_miles |
| WAS/WAS-T/WAS-S | callsign, qso_date, skcc_number, key_type, state |
| WAC | callsign, qso_date, skcc_number, key_type, country/continent |

## Support

For issues with the export functionality:
1. Check this documentation
2. Verify your database has the required fields
3. Test with `--list-awards` to ensure the tool is working
4. Review the logbook database schema

For SKCC award rules questions:
- Visit: https://www.skccgroup.com/operating_awards/
