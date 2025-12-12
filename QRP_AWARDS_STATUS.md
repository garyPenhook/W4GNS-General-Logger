# SKCC QRP Awards Implementation Status

This document compares the official SKCC QRP award rules with the current implementation.

## QRP Miles Per Watt (MPW) Award

**Status**: ✅ **IMPLEMENTED** (with recent fixes)

### Official Rules (from skccgroup.com)

**Basic Qualification:**
- Formula: (Distance in miles) / (Power in watts) ≥ 1,000 MPW
- Only applying station must use QRP (≤5W)
- Power must be ≤5W for ENTIRE QSO (cannot reduce mid-contact)
- Eligible QSOs: September 1, 2014 or later

**Endorsement Levels:**
- First Award: 1,000 MPW
- Second Endorsement: 1,500 MPW
- Third Endorsement: 2,000 MPW
- **Additional endorsements continue in 500-mile increments with no upper limit**
  (2,500 MPW, 3,000 MPW, 3,500 MPW, etc.)

**Required Exchange:**
- RST (realistic values)
- QTH (state/province for US/Canada, IAAF country code for others)
- Operator name
- SKCC number
- Power output

**Equipment:**
- SKCC-approved keying devices: straight keys, side-swipers, semi-automatic keys
- Amateur satellite contacts ineligible

**Distance Calculation:**
- Must use "N9SSA's calculator" based on lat/lon or grid squares

### Current Implementation

✅ **Correctly Implemented:**
- Power validation (≤5W for entire QSO)
- Date validation (≥ Sept 1, 2014)
- Distance calculation from gridsquares (using haversine formula)
- Membership validation (both stations must be SKCC members at time of contact)
- Mode validation (CW only)
- Key type validation (STRAIGHT, BUG, SIDESWIPER)
- Base award: 1,000 MPW ✓
- Level 2: 1,500 MPW ✓
- Level 3: 2,000 MPW ✓
- **NEW**: Endorsements beyond 2,000 MPW at 500 MPW increments ✓

✅ **Recent Fixes Applied:**
- Fixed field name mismatch (distance_nm vs distance_miles)
- Fixed power field mismatch (power vs power_watts)
- Added gridsquare distance calculator
- Added automatic distance calculation from gridsquares
- Added database persistence for calculated distances
- Fixed endorsement calculation to continue beyond 2,000 MPW
- Improved gridsquare validation (length, field range A-R, subsquare range A-X)
- Updated to WGS84 Earth radius for accuracy

⚠️ **Minor Differences (Not Breaking):**
- Uses our gridsquare calculator instead of "N9SSA's calculator"
  - Our calculator is accurate (tested: FN31pr to CM87 = 2,655 miles, correct)
  - Uses WGS84 standard Earth radius (3,440.0691 NM)
  - Haversine formula for great circle distance
  - Should produce equivalent results to N9SSA's calculator

📝 **Implementation Notes:**
- Award validation: `src/skcc_awards/qrp_mpw.py`
- Distance calculator: `src/utils/gridsquare.py`
- Display logic: `src/gui/skcc_awards_tab.py`
- Power field fix: `fix_power_field.py` (run once to migrate data)

---

## QRP Awards (1xQRP / 2xQRP)

**Status**: ❌ **NOT IMPLEMENTED**

### Official Rules (from skccgroup.com)

**Two Award Levels:**

**1xQRP Award:**
- Minimum: 300 points
- Only applying station must operate QRP
- Contact same station once per band (across all bands)

**2xQRP Award:**
- Minimum: 150 points
- BOTH stations must operate QRP during exchange
- One station may initially transmit higher power but must reduce to QRP for exchange
- Must log other operator's power level for verification
- Contact same station once per band (across all bands)

**Point Distribution by Band:**
- 160m: 4 points
- 80m, 10m: 3 points
- 60m, 40m, 30m: 2 points
- 20m, 17m, 15m, 12m: 1 point
- 6m, 2m: 0.5 points

**Equipment Requirements:**
- Both operators must use straight key, sideswiper, or bug

**Logging Requirements:**
- Date and UTC time
- Band or frequency
- SKCC numbers from both stations
- Transmitting power level
- For 2xQRP: other operator's power level

### What Would Need to Be Implemented

1. **New Award Classes:**
   - Create `QRP1xAward` class (300 points, only applicant QRP)
   - Create `QRP2xAward` class (150 points, both stations QRP)

2. **Point Calculation:**
   - Implement band-based point system
   - 160m: 4, 80m/10m: 3, 60m/40m/30m: 2, 20m/17m/15m/12m: 1, 6m/2m: 0.5
   - Ensure same callsign counts once per band (not per-band duplicate tracking)

3. **Database Fields Needed:**
   - `their_power_watts` - Other station's power (for 2xQRP validation)

4. **Validation Logic:**
   - 1xQRP: Check only applicant power ≤5W
   - 2xQRP: Check both applicant and other station power ≤5W
   - Both: Verify mechanical key type (STRAIGHT, BUG, SIDESWIPER)
   - Both: Verify SKCC membership at time of contact
   - Both: CW mode only

5. **UI Display:**
   - Add to Specialty Awards tab
   - Show points progress toward 300 (1xQRP) or 150 (2xQRP)
   - Display breakdown by band
   - List qualifying contacts

6. **Award Application:**
   - Generate report listing contacts with band/points
   - Show total points calculation
   - For 2xQRP: include other operator power levels

### Priority

**LOW** - While these are legitimate SKCC awards, they are:
- Less commonly pursued than QRP/MPW
- Require additional database schema changes (their_power_watts field)
- Require significant new code for point calculation system
- User's primary concern (QRP/MPW) is now working

### Recommendation

Defer implementation of QRP Awards (1xQRP/2xQRP) to a future enhancement. Current focus should be on:
1. Testing the fixed QRP/MPW award with user's VK4TJ contact
2. Ensuring all existing awards work correctly
3. Only implement QRP Awards if user specifically requests this feature

---

## Submission Information

**QRP/MPW Award Applications:**
Submit to:
- Bill Nixon (W0EJ)
- Kevin Miller (KI4DEF)
- Subject line: "Application"

**Award Application Generator:**
The app has a "📄 Generate Award Application" button in the SKCC Awards tab that will generate a properly formatted report for submission.

---

## Testing Your QRP/MPW Award

With the recent fixes, your VK4TJ contact should now qualify:

**Expected Award Status:**
```
✅ ACHIEVED! - Best: 1883.1 MPW - Level: 1,500 MPW

≥1,000 MPW: 1 | ≥1,500 MPW: 1 | ≥2,000 MPW: 0
```

**Next Threshold:**
- Current: 1,500 MPW level
- Next: 2,000 MPW (need 117 more MPW)
- To achieve at 5W: Need 10,000 mile contact
- To achieve with VK4TJ distance: Need to reduce power to 4.7W or less

**Contact Details:**
- Callsign: VK4TJ
- Date: 2025-08-05
- Distance: 9,415.7 miles
- Power: 5.0 watts
- MPW: 1,883.1
- SKCC#: 4474S (Senator)
- Key: BUG
- Mode: CW

All requirements met! ✅
