# Tribune Award Logic Verification

## Summary

I've thoroughly reviewed the Tribune award logic in this app and compared it with the official SKCC rules. **The logic is CORRECT** and matches the official requirements.

## Official SKCC Tribune Rules (Verified)

According to the official SKCC website (https://www.skccgroup.com/operating_awards/tribune/):

> "Tribune is achieved when a **Centurion** makes contact and exchanges SKCC number and name with **50 different SKCC Centurions, Tribunes, or Senators**, in any combination."

Key clarification from the rules:
> "For brevity, throughout the rest of this page the term Centurion refers to any member who is listed on the Centurion roster - they may hold a C, a T, or an S."

## Implementation Status

### ✅ Tribune Award Logic (src/skcc_awards/tribune.py)

**Status:** CORRECT - Fully aligned with official SKCC rules

The Tribune award validation correctly implements all requirements:

1. **✓ Counts Centurions, Tribunes, AND Senators**
   - Uses `was_centurion_or_higher_on_date()` method
   - Fixed in commit 22c97bf on 2025-11-08
   - Validates against official SKCC award rosters

2. **✓ Prerequisite Check**
   - Requires user to be Centurion first (100+ unique SKCC members)

3. **✓ Date Validation**
   - QSO must be on/after March 1, 2007 (Tribune effective date)
   - QSO must be on/after user's Centurion achievement date
   - Remote station must have held C/T/S status by QSO date

4. **✓ SKCC Membership Validation**
   - Both parties must be SKCC members at time of QSO
   - Validates against official SKCC roster with join dates

5. **✓ Mode & Key Requirements**
   - CW mode only
   - Mechanical key required (STRAIGHT, BUG, or SIDESWIPER)

6. **✓ Special Event Call Filtering**
   - Club/special event calls excluded after October 1, 2008

7. **✓ Roster Validation with Fallback**
   - Primary: Validates against downloaded official SKCC rosters
   - Fallback: Accepts C/T/S suffix if rosters not available

### ✅ Diagnostic Script (diagnose_tribune.py)

**Status:** FIXED - Was using outdated logic

**Issue Found:**
- Diagnostic script was using `was_tribune_or_senator_on_date()` (old logic)
- Actual award validation uses `was_centurion_or_higher_on_date()` (correct logic)
- This caused diagnostic to show incorrect rejection reasons

**Fix Applied:**
- Updated diagnostic to use `was_centurion_or_higher_on_date()`
- Updated output messages to show "Centurion/Tribune/Senator"
- Committed in this session

## Comparison with Official SKCCLogger

The logic in this app **matches** the official SKCC rules. Key differences from older implementations:

| Aspect | This App (Current) | Official SKCC Rules |
|--------|-------------------|-------------------|
| Eligible contacts | Centurion/Tribune/Senator (C/T/S) | ✓ Centurion/Tribune/Senator (C/T/S) |
| Prerequisite | Must be Centurion first | ✓ Must be Centurion first |
| Date validation | QSO ≥ user's Centurion date | ✓ QSO ≥ both Centurion dates |
| Roster validation | Uses official SKCC rosters | ✓ Based on official lists |
| Fallback | C/T/S suffix if rosters missing | ✓ Reasonable fallback |

## Validation Rules Implemented

The `tribune.py` validation checks (in order):

1. CW mode only
2. Mechanical key (STRAIGHT, BUG, or SIDESWIPER)
3. SKCC number present
4. Contact date ≥ March 1, 2007
5. Special event calls excluded after Oct 1, 2008
6. Both stations were SKCC members on QSO date
7. **Remote station was Centurion/Tribune/Senator on QSO date** ⭐
8. QSO date ≥ user's Centurion achievement date

## How Roster Validation Works

The app uses official SKCC rosters to validate award status:

```python
# Primary validation (accurate date checking)
is_valid = award_rosters.was_centurion_or_higher_on_date(skcc_num, qso_date)

# This checks:
# 1. Was the member a Centurion by the QSO date?
# 2. Was the member a Tribune by the QSO date?
# 3. Was the member a Senator by the QSO date?

# Fallback (if rosters not available)
if not is_valid and not rosters_loaded:
    if skcc_number has C/T/S suffix:
        is_valid = True  # Accept based on suffix
```

## Testing the Logic

To verify Tribune contacts in your database:

```bash
# 1. Download latest rosters (automatic on app startup, or manual)
python3 download_rosters.py

# 2. Run diagnostic to see which contacts qualify
python3 diagnose_tribune.py

# 3. Check roster status
# The diagnostic shows:
# - Total contacts with SKCC numbers
# - Valid Tribune contacts (with unique count)
# - Rejected contacts with reasons
# - Roster status (loaded/missing)
```

## Potential Discrepancies with Official SKCCLogger

If you're seeing different contact counts between this app and the official SKCCLogger, possible causes:

1. **Roster Data Differences**
   - Official SKCCLogger may have different roster dates
   - Solution: Download latest rosters with `python3 download_rosters.py`

2. **User Centurion Date Not Set**
   - Tribune contacts only count after YOU achieved Centurion
   - Check Settings → SKCC → Centurion Achievement Date
   - If not set, contacts before your Centurion date won't count

3. **Key Type Not Set**
   - Tribune requires mechanical key (STRAIGHT, BUG, or SIDESWIPER)
   - Contacts without key_type will be rejected
   - Set key types in the contact editor

4. **SKCC Join Date Not Set**
   - Contacts before your SKCC join date are invalid
   - Check Settings → SKCC → Join Date

5. **Database Differences**
   - Ensure you've imported all contacts from the same ADIF file
   - Check that SKCC numbers were imported correctly

## Next Steps

To compare with official SKCCLogger:

1. **Set Your SKCC Dates**
   - Open Settings → SKCC tab
   - Set SKCC Join Date (when you joined SKCC)
   - Set Centurion Achievement Date (when you earned Centurion)

2. **Import Contacts**
   - File → Import ADIF
   - Import the same file you use in SKCCLogger

3. **Download Rosters**
   - Happens automatically on app startup
   - Or run: `python3 download_rosters.py`

4. **Run Diagnostic**
   ```bash
   python3 diagnose_tribune.py
   ```

5. **Compare Results**
   - Check the unique contact count
   - Review rejected contacts and their reasons
   - Compare with SKCCLogger's Tribune count

## Files Modified in This Session

- `diagnose_tribune.py` - Fixed to use correct validation logic

## Conclusion

The Tribune award logic in this app is **CORRECT** and fully compliant with official SKCC rules as of November 2025. The recent fix (commit 22c97bf) properly changed the logic to count Centurion/Tribune/Senator contacts instead of just Tribune/Senator.

If you're still seeing discrepancies with the official SKCCLogger, please:
1. Run the diagnostic script to see which contacts are being rejected
2. Verify your SKCC dates are set correctly in Settings
3. Ensure rosters are downloaded and up-to-date
4. Share the diagnostic output for further analysis

---

**Date:** 2025-11-09
**Branch:** claude/app-development-011CUxS1KYXsbffHXeWNmx8L
**Commits:**
- 22c97bf - Fix Tribune award to count Centurion/Tribune/Senator contacts
- a772a6a - Fix diagnostic script to match Tribune award logic
