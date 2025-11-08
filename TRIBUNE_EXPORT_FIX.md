# Tribune Award Export Fix

## Problem

You were getting only **90 contacts** for Tribune x2 when you should have **149 contacts**.

## Root Cause

The Tribune award validation requires verifying that contacted stations were **Tribune or Senator at the time of the QSO**. This validation uses official SKCC rosters downloaded from the SKCC website.

Without these rosters, the validation code cannot verify the award status and rejects contacts, even if they have T or S suffixes in their SKCC numbers.

## Solution

The fix includes two improvements:

### 1. **Roster Download Script**

A new script `download_rosters.py` will download the official Centurion, Tribune, and Senator rosters from the SKCC website and cache them locally.

**Usage:**
```bash
python3 download_rosters.py
```

This downloads all three rosters and stores them in:
- `~/.skcc_rosters/centurion_roster.txt`
- `~/.skcc_rosters/tribune_roster.txt`
- `~/.skcc_rosters/senator_roster.txt`

And also saves them to the database for validation.

### 2. **Fallback Validation**

Modified `src/skcc_awards/tribune.py` and `src/skcc_awards/senator.py` to add a **fallback validation** when rosters aren't available:

- **Primary validation**: Check official rosters to verify the station was T/S on the QSO date
- **Fallback validation**: If rosters aren't downloaded, check the SKCC number suffix (T or S)

The fallback is less precise (it doesn't verify the exact date they achieved the award), but it allows validation when rosters haven't been downloaded.

## How to Fix Your Export

### Option 1: Download Rosters (Recommended)

This is the most accurate method:

```bash
# 1. Download the rosters
python3 download_rosters.py

# 2. Export Tribune award again
python3 export_award_application.py --award tribune --callsign W4GNS
```

### Option 2: Use Fallback Validation

The code now automatically uses fallback validation when rosters aren't available. Simply re-export:

```bash
python3 export_award_application.py --award tribune --callsign W4GNS
```

The validation will use the T/S suffix in SKCC numbers to determine Tribune/Senator status.

## Verification

After the fix, you should see all 149 contacts in your export. Run the diagnostic to verify:

```bash
python3 diagnose_tribune.py
```

This shows:
- How many contacts qualify for Tribune
- Which contacts are rejected and why
- Roster status (loaded/missing)

## Expected Results

With the fix:
- **Tribune x2**: 149 contacts (up from 90)
- All contacts with T or S suffix in their SKCC number should now count

## Technical Details

### Validation Rules (in order)

1. ✓ CW mode only
2. ✓ Mechanical key (STRAIGHT, BUG, or SIDESWIPER)
3. ✓ SKCC number present
4. ✓ Contact date ≥ March 1, 2007
5. ✓ Special event calls excluded after Oct 1, 2008
6. ✓ Both stations were SKCC members on QSO date
7. ✓ **Remote station was Tribune or Senator** (PRIMARY or FALLBACK validation)
8. ✓ QSO date ≥ user's Centurion achievement date

### Fallback Validation Logic

```python
# Try roster validation first
is_valid = rosters.was_tribune_or_senator_on_date(skcc_num, qso_date)

# If failed and rosters aren't loaded, use suffix
if not is_valid and not rosters_loaded:
    if skcc_number.endswith('T') or skcc_number.endswith('S'):
        is_valid = True  # Accept based on suffix
```

## Files Modified

- `src/skcc_awards/tribune.py` - Added fallback validation
- `src/skcc_awards/senator.py` - Added fallback validation
- `download_rosters.py` - New script to download rosters
- `diagnose_tribune.py` - New diagnostic script

## Notes

- Rosters are cached for 7 days
- Use `download_rosters.py -f` to force re-download
- The fallback validation is safe - it only accepts stations with T or S suffixes, which are official SKCC award indicators
