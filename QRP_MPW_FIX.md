# QRP Miles Per Watt Award - Fix Documentation

## Problem Identified

The QRP/MPW award was not calculating correctly due to two issues:

### 1. Database Field Mismatch
- **Database stores**: `distance_nm` (nautical miles)
- **Award code was looking for**: `distance_miles` (statute miles)
- **Result**: Award validation always failed because it couldn't find the distance field

### 2. Missing Distance Data
- The `distance_nm` field in the database was NULL for all contacts
- No automatic calculation of distance from gridsquares was happening
- **Result**: Even with field name fix, no contacts would qualify without distance data

## Fixes Implemented

### 1. Fixed Field Name Mismatch (`src/skcc_awards/qrp_mpw.py`)
- Changed code to read `distance_nm` from database
- Added conversion from nautical miles to statute miles (1 NM = 1.15078 miles)
- Both `validate()` and `calculate_progress()` methods updated

### 2. Created Gridsquare Distance Calculator (`src/utils/gridsquare.py`)
- New utility module for Maidenhead gridsquare calculations
- Converts gridsquares to lat/lon coordinates
- Uses haversine formula for great circle distance
- Supports 4, 6, and 8 character gridsquares (e.g., FM06, FM06EW, FM06EW79)
- Returns distance in both nautical miles and statute miles

### 3. Integrated Distance Calculation (`src/gui/skcc_awards_tab.py`)
- When refreshing awards, automatically calculates distance from gridsquares
- Only calculates if `distance_nm` is not already set
- Requires both `my_gridsquare` and `gridsquare` fields to be populated
- Gracefully handles missing or invalid gridsquares

## Requirements for QRP/MPW Award

To qualify for QRP/MPW award, contacts must meet ALL these criteria:

### Critical Requirements
1. **QRP Power**: Must use ≤5 watts for entire QSO
2. **Distance**: Must achieve at least 1,000 miles per watt (MPW)
3. **SKCC Members**: Both stations must be SKCC members at time of contact
4. **Date**: QSO must be on or after September 1, 2014
5. **Mode**: CW only
6. **Key Type**: Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)

### Data Requirements in Logbook
For the award to calculate properly, each contact must have:
- `power_watts`: Power in watts (≤5W for QRP)
- `my_gridsquare`: Your gridsquare locator
- `gridsquare`: Their gridsquare locator
- `skcc_number`: Their SKCC number
- `mode`: CW
- `key_type`: STRAIGHT, BUG, or SIDESWIPER

### Endorsement Levels
- **Base Award**: 1,000 MPW
- **Level 2**: 1,500 MPW
- **Level 3**: 2,000 MPW (no upper limit)

## Example Calculations

### Not Qualifying
- Distance: 630 miles
- Power: 5 watts
- MPW: 630 / 5 = 126 MPW
- **Result**: Does NOT qualify (needs 1000 MPW minimum)

### Qualifying for Base Award
- Distance: 5000 miles
- Power: 5 watts
- MPW: 5000 / 5 = 1,000 MPW
- **Result**: Qualifies for base award (1,000 MPW)

### Qualifying for Level 2
- Distance: 7500 miles
- Power: 5 watts
- MPW: 7500 / 5 = 1,500 MPW
- **Result**: Qualifies for Level 2 endorsement (1,500 MPW)

### Alternative: Lower Power
- Distance: 2500 miles
- Power: 2 watts
- MPW: 2500 / 2 = 1,250 MPW
- **Result**: Qualifies for base award (1,250 MPW)

## What You Need To Do

### For Existing Contacts

The award will now automatically calculate distance from gridsquares when you refresh the awards tab. However, you need to ensure your contacts have gridsquare data:

1. **Check Your Gridsquare**: Go to Settings tab and verify "My Gridsquare" is set
2. **Review Contacts**: Check that your SKCC contacts have their gridsquare populated
   - This usually comes from QRZ lookups or ADIF imports
3. **Refresh Awards**: Click "Refresh Awards" button in SKCC Awards tab

### For Future Contacts

When logging new QRP contacts:
1. Set power to ≤5W in the logging form
2. Make sure gridsquare is populated (use QRZ lookup)
3. Record SKCC number and key type
4. The distance will be automatically calculated from gridsquares

## Testing Your Setup

Run this command to check your QRP contacts with gridsquare data:

```bash
sqlite3 ./logs/w4gns_log_*.db "SELECT callsign, my_gridsquare, gridsquare,
skcc_number, power_watts, distance_nm FROM contacts
WHERE skcc_number IS NOT NULL AND power_watts <= 5
AND my_gridsquare IS NOT NULL AND gridsquare IS NOT NULL
LIMIT 10;"
```

After the fix, `distance_nm` should be calculated automatically when viewing awards.

## Files Modified

- `src/skcc_awards/qrp_mpw.py` - Fixed field name and added NM to miles conversion
- `src/utils/gridsquare.py` - New gridsquare distance calculator
- `src/gui/skcc_awards_tab.py` - Added automatic distance calculation on award refresh

## Next Steps

1. Launch the app
2. Go to SKCC Awards tab → Specialty Awards
3. Scroll down to "QRP Miles Per Watt Award" section
4. Click "Refresh Awards" button
5. You should now see calculated MPW values if you have qualifying contacts

The award will now correctly show your progress toward the 1,000/1,500/2,000 MPW thresholds!
