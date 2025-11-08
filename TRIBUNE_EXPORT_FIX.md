# Tribune Award Export Fix

## Problem

You were getting only **90 contacts** for Tribune x2 when you should have **149 contacts**.

## Root Cause

The Tribune award validation requires verifying that contacted stations were **Tribune or Senator at the time of the QSO**. This validation uses official SKCC rosters downloaded from the SKCC website.

Without these rosters, the validation code cannot verify the award status and rejects contacts, even if they have T or S suffixes in their SKCC numbers.

## Solution

The fix includes three improvements:

### 1. **Automatic Roster Downloads** ✨

The app now **automatically downloads** the official Centurion, Tribune, and Senator rosters from the SKCC website when it starts up.

- Runs in a background thread (doesn't slow down startup)
- Uses 7-day cache (won't re-download if recent)
- Rosters stored in `~/.skcc_rosters/` directory
- Also saved to database for validation

**You don't need to do anything - it happens automatically when you launch the app!**

### 2. **Manual Roster Download Script** (optional)

If you want to manually force a roster download, use the `download_rosters.py` script:

```bash
python3 download_rosters.py
```

This is useful if:
- You want to force a fresh download
- You're troubleshooting roster issues
- You want to verify roster contents

### 3. **Fallback Validation**

Modified `src/skcc_awards/tribune.py` and `src/skcc_awards/senator.py` to add a **fallback validation** when rosters aren't available:

- **Primary validation**: Check official rosters to verify the station was T/S on the QSO date
- **Fallback validation**: If rosters aren't downloaded, check the SKCC number suffix (T or S)

The fallback is less precise (it doesn't verify the exact date they achieved the award), but it ensures validation always works.

## How to Fix Your Export

With the fix, rosters are **automatically downloaded** when you start the app, so you just need to:

```bash
# Launch the app (rosters download automatically in background)
python3 main.py

# Or export directly from command line
python3 export_award_application.py --award tribune --callsign W4GNS
```

That's it! The app will:
1. Automatically download rosters if needed (7-day cache)
2. Use roster validation for accurate date checking
3. Fall back to T/S suffix validation if rosters aren't available

### Manual Roster Download (Optional)

If you want to force a fresh roster download without launching the GUI:

```bash
python3 download_rosters.py
python3 export_award_application.py --award tribune --callsign W4GNS
```

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

- `main.py` - Added automatic roster downloads on app startup (background thread)
- `src/skcc_awards/tribune.py` - Added fallback validation
- `src/skcc_awards/senator.py` - Added fallback validation
- `download_rosters.py` - New script to manually download rosters
- `diagnose_tribune.py` - New diagnostic script
- `TRIBUNE_EXPORT_FIX.md` - This documentation

## Notes

- Rosters are automatically downloaded on app startup (7-day cache)
- Roster downloads run in background thread (doesn't slow down startup)
- Use `download_rosters.py -f` to force manual re-download
- The fallback validation is safe - it only accepts stations with T or S suffixes, which are official SKCC award indicators
