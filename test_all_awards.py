#!/usr/bin/env python3
"""
Test all awards implementations for completeness and correctness
"""

from src.dxcc import lookup_dxcc
from src.awards_calculator import AwardsCalculator

print("="*70)
print("Awards Implementation Completeness Test")
print("="*70)
print()

# Test 1: DXCC Country Lookup
print("1. DXCC COUNTRY LOOKUP TEST")
print("-" * 70)

test_calls_dxcc = [
    ('W4GNS', 'United States', 'NA'),
    ('W4GNS/P', 'United States', 'NA'),
    ('KH6/W4GNS', 'Hawaii', 'OC'),  # Operating FROM Hawaii
    ('G4ABC', 'England', 'EU'),
    ('ZS1ABC', 'South Africa', 'AF'),
    ('PY2ABC', 'Brazil', 'SA'),
    ('JA1ABC', 'Japan', 'AS'),
]

dxcc_issues = []
for call, expected_country, expected_continent in test_calls_dxcc:
    info = lookup_dxcc(call)
    if info:
        country = info['country']
        continent = info['continent']
        if country == expected_country and continent == expected_continent:
            print(f"  ✓ {call:15} -> {country:20} ({continent})")
        else:
            print(f"  ✗ {call:15} -> {country:20} ({continent}) EXPECTED: {expected_country} ({expected_continent})")
            dxcc_issues.append(call)
    else:
        print(f"  ✗ {call:15} -> NO MATCH")
        dxcc_issues.append(call)

print()

# Test 2: WPX Prefix Extraction
print("2. WPX PREFIX EXTRACTION TEST")
print("-" * 70)

calc = AwardsCalculator(None)

test_calls_wpx = [
    ('W4GNS', 'W4'),
    ('W4GNS/P', 'W4'),           # Portable indicator should be ignored
    ('W4GNS/M', 'W4'),           # Mobile indicator should be ignored
    ('W4GNS/MM', 'W4'),          # Maritime mobile
    ('KH6/W4GNS', 'KH6'),        # Operating from Hawaii - use location prefix
    ('W4GNS/KH6', 'KH6'),        # Same thing, different format
    ('VP9/K1ABC', 'VP9'),        # Operating from Bermuda
    ('K1ABC/VP9', 'VP9'),        # Same thing
    ('G4ABC', 'G4'),
    ('DL1ABC', 'DL1'),
    ('VE3ABC', 'VE3'),
]

wpx_issues = []
for call, expected_prefix in test_calls_wpx:
    prefix = calc._extract_prefix(call)
    if prefix == expected_prefix:
        print(f"  ✓ {call:15} -> {prefix}")
    else:
        print(f"  ✗ {call:15} -> {prefix:10} EXPECTED: {expected_prefix}")
        wpx_issues.append(call)

print()

# Test 3: WAS State Detection
print("3. WAS STATE DETECTION TEST")
print("-" * 70)

# Check if country name matching will work
test_country_names = ['United States', 'USA', 'US']
dxcc_us = lookup_dxcc('W4GNS')
if dxcc_us:
    us_country = dxcc_us['country']
    if us_country in test_country_names:
        print(f"  ✓ US country name '{us_country}' matches WAS filter")
    else:
        print(f"  ✗ US country name '{us_country}' does NOT match WAS filter")
        print(f"    WAS looks for: {test_country_names}")
        print(f"    This will cause WAS tracking to FAIL!")
else:
    print("  ✗ Cannot lookup US callsign")

print()

# Test 4: Mode Normalization
print("4. MODE NORMALIZATION TEST")
print("-" * 70)

test_modes = [
    ('SSB', 'PHONE'),
    ('USB', 'PHONE'),
    ('LSB', 'PHONE'),
    ('FM', 'PHONE'),
    ('CW', 'CW'),
    ('FT8', 'DIGITAL'),
    ('FT4', 'DIGITAL'),
    ('RTTY', 'DIGITAL'),
    ('PSK31', 'DIGITAL'),
]

mode_issues = []
for mode, expected in test_modes:
    normalized = calc._normalize_mode(mode)
    if normalized == expected:
        print(f"  ✓ {mode:10} -> {normalized}")
    else:
        print(f"  ✗ {mode:10} -> {normalized:10} EXPECTED: {expected}")
        mode_issues.append(mode)

print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print()

all_issues = {
    'DXCC Lookup': dxcc_issues,
    'WPX Prefix Extraction': wpx_issues,
    'Mode Normalization': mode_issues
}

total_issues = sum(len(issues) for issues in all_issues.values())

if total_issues == 0:
    print("✓ All awards implementations are COMPLETE and CORRECT!")
else:
    print(f"⚠  Found {total_issues} issue(s):")
    print()
    for category, issues in all_issues.items():
        if issues:
            print(f"  {category}:")
            for issue in issues:
                print(f"    - {issue}")
    print()

print("="*70)
