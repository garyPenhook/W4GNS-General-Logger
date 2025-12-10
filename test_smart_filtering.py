#!/usr/bin/env python3
"""
Test script to verify smart log processing integration
"""

import sqlite3
from src.needed_analyzer import NeededContactsAnalyzer, SpotAnalysis

# Create test database with some contacts
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create contacts table (simplified)
cursor.execute('''
    CREATE TABLE contacts (
        id INTEGER PRIMARY KEY,
        callsign TEXT,
        band TEXT,
        mode TEXT,
        skcc_number TEXT,
        state TEXT,
        country TEXT,
        continent TEXT,
        gridsquare TEXT,
        date TEXT,
        time_on TEXT
    )
''')

# Add some test contacts
test_contacts = [
    ('K1ABC', '20M', 'CW', None, 'MA', 'USA', 'NA', 'FN42', '2024-01-01', '1200'),
    ('W2XYZ', '40M', 'CW', '12345C', 'NY', 'USA', 'NA', 'FN30', '2024-01-01', '1300'),
    ('K3DEF', '20M', 'CW', None, 'PA', 'USA', 'NA', 'FN20', '2024-01-01', '1400'),
]

for call, band, mode, skcc, state, country, cont, grid, date, time in test_contacts:
    cursor.execute('''
        INSERT INTO contacts (callsign, band, mode, skcc_number, state, country, continent, gridsquare, date, time_on)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (call, band, mode, skcc, state, country, cont, grid, date, time))

conn.commit()

# Create analyzer
analyzer = NeededContactsAnalyzer(conn)

print("=" * 70)
print("SMART LOG PROCESSING TEST")
print("=" * 70)
print()

# Test various spots
test_spots = [
    {
        'callsign': 'K1ABC',
        'band': '20M',
        'mode': 'CW',
        'state': 'MA',
        'country': 'USA',
        'description': 'Already worked on 20M CW'
    },
    {
        'callsign': 'K1ABC',
        'band': '40M',
        'mode': 'CW',
        'state': 'MA',
        'country': 'USA',
        'description': 'Same call, different band (should be needed for WPX)'
    },
    {
        'callsign': 'W4ZZZ',
        'band': '20M',
        'mode': 'CW',
        'state': 'NC',
        'country': 'USA',
        'description': 'New state NC (needed for WAS)'
    },
    {
        'callsign': 'G3XYZ',
        'band': '20M',
        'mode': 'CW',
        'state': None,
        'country': 'England',
        'continent': 'EU',
        'description': 'European station (needed for DXCC/WAC)'
    },
    {
        'callsign': 'W5AAA',
        'band': '20M',
        'mode': 'CW',
        'state': 'TX',
        'country': 'USA',
        'skcc_number': '54321T',
        'description': 'SKCC Tribune member (high priority)'
    },
]

for spot in test_spots:
    print(f"Testing: {spot['callsign']} - {spot['description']}")
    print("-" * 70)

    analysis = analyzer.analyze_spot(
        callsign=spot['callsign'],
        band=spot['band'],
        mode=spot['mode'],
        frequency='14.050',
        skcc_number=spot.get('skcc_number'),
        state=spot.get('state'),
        country=spot.get('country'),
        continent=spot.get('continent'),
        gridsquare=spot.get('gridsquare')
    )

    print(f"  Is Needed: {'YES' if analysis.is_needed else 'NO'}")
    print(f"  Priority: {analysis.priority_label}")

    if analysis.is_needed:
        print(f"  Reasons ({len(analysis.reasons)}):")
        for reason in analysis.reasons:
            print(f"    - {reason}")

    print()

print("=" * 70)
print("TEST COMPLETED")
print("=" * 70)
print()
print("If you see the analysis above, the smart filtering is working!")
print()
print("In the GUI, you should see:")
print("  - Spots highlighted in GREEN (high priority), AMBER (medium), or GRAY (low)")
print("  - The 'Needed For' column showing why you need each station")
print("  - Audio alerts for high-priority contacts (if enabled)")
print()
print("To test in the app:")
print("  1. Go to 'DX Clusters' tab")
print("  2. Connect to a cluster")
print("  3. Watch the 'DX Spots' section on the 'Log Contacts' tab")
print("  4. Spots should be color-coded based on whether you need them")
