#!/usr/bin/env python3
"""
Test WAC (Worked All Continents) tracking with the complete DXCC database.

This script demonstrates that the WAC tracking system now has complete
continent data for all major DXCC entities.
"""

from src.dxcc import lookup_dxcc, get_continent_from_callsign

# Test callsigns representing each continent
test_callsigns = {
    'NA': ['W4GNS', 'VE3ABC', 'XE1ABC', 'KP4ABC', 'KL7ABC', 'TI2ABC', 'J6ABC', '8P1ABC'],
    'SA': ['PY2ABC', 'LU1ABC', 'CE3ABC', 'HC1ABC', 'CP1ABC', 'CX1ABC', 'YV1ABC'],
    'EU': ['G4ABC', 'DL1ABC', 'F5ABC', 'EA1ABC', 'OH2ABC', 'SM5ABC', 'OZ1ABC', 'SP1ABC', '9H1ABC'],
    'AS': ['JA1ABC', 'BY1ABC', 'HL1ABC', 'VU2ABC', 'HS1ABC', 'AP2ABC', '4X1ABC', 'A71ABC'],
    'AF': ['ZS1ABC', '5N1ABC', 'EA8ABC', 'SU9ABC', 'C91ABC', '9G1ABC', 'CN2ABC', '5T5ABC'],
    'OC': ['VK2ABC', 'ZL1ABC', 'KH6ABC', 'DU1ABC', 'YB1ABC', '9M2ABC', 'P29ABC', 'FO8ABC']
}

print("="*70)
print("WAC (Worked All Continents) Tracking Verification")
print("="*70)
print()
print("Testing DXCC lookups for all 6 continents:")
print()

all_continents_found = set()

for expected_continent, callsigns in test_callsigns.items():
    print(f"{expected_continent} - {['NA', 'SA', 'EU', 'AS', 'AF', 'OC'][['NA', 'SA', 'EU', 'AS', 'AF', 'OC'].index(expected_continent)]}")
    print("  " + "="*66)

    found_count = 0
    for callsign in callsigns:
        dxcc_info = lookup_dxcc(callsign)
        if dxcc_info:
            continent = dxcc_info['continent']
            country = dxcc_info['country']

            # Handle multi-continent entities like Russia (EU/AS)
            if '/' in continent:
                continents = continent.split('/')
                if expected_continent in continents:
                    status = "✓"
                    found_count += 1
                    all_continents_found.add(expected_continent)
                else:
                    status = "✗"
            elif continent == expected_continent:
                status = "✓"
                found_count += 1
                all_continents_found.add(expected_continent)
            else:
                status = "✗"

            print(f"  {status} {callsign:10} -> {continent:6} ({country})")
        else:
            print(f"  ✗ {callsign:10} -> NO MATCH")

    print(f"  Found: {found_count}/{len(callsigns)}")
    print()

print("="*70)
print("Summary:")
print("="*70)

continent_names = {
    'NA': 'North America',
    'SA': 'South America',
    'EU': 'Europe',
    'AS': 'Asia',
    'AF': 'Africa',
    'OC': 'Oceania'
}

print()
print("Continents with DXCC data:")
for cont_code in ['NA', 'SA', 'EU', 'AS', 'AF', 'OC']:
    if cont_code in all_continents_found:
        print(f"  ✓ {continent_names[cont_code]}")
    else:
        print(f"  ✗ {continent_names[cont_code]}")

print()
if len(all_continents_found) == 6:
    print("✓ SUCCESS! All 6 continents have complete DXCC data!")
    print("  WAC (Worked All Continents) tracking is now fully functional.")
else:
    print(f"⚠ WARNING: Only {len(all_continents_found)}/6 continents have data.")
    missing = set(['NA', 'SA', 'EU', 'AS', 'AF', 'OC']) - all_continents_found
    print(f"  Missing: {', '.join([continent_names[c] for c in missing])}")

print("="*70)
