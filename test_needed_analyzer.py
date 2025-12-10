#!/usr/bin/env python3
"""
Test NeededContactsAnalyzer for completeness and correctness

Tests cover:
- Cache timeout logic
- Award-specific checking logic for each award type
- Edge cases like empty/null input data
- Prefix extraction logic
"""

import sqlite3
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, '.')

from src.needed_analyzer import NeededContactsAnalyzer, SpotAnalysis, NeededReason

print("="*70)
print("NeededContactsAnalyzer Unit Tests")
print("="*70)
print()

# Create an in-memory database for testing
def create_test_db():
    """Create an in-memory SQLite database with test data"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create contacts table
    cursor.execute("""
        CREATE TABLE contacts (
            id INTEGER PRIMARY KEY,
            callsign TEXT,
            band TEXT,
            mode TEXT,
            skcc_number TEXT,
            state TEXT,
            country TEXT,
            continent TEXT,
            gridsquare TEXT
        )
    """)

    # Create SKCC tables
    cursor.execute("""
        CREATE TABLE skcc_tribune_members (
            skcc_number TEXT PRIMARY KEY
        )
    """)

    cursor.execute("""
        CREATE TABLE skcc_senator_members (
            skcc_number TEXT PRIMARY KEY
        )
    """)

    conn.commit()
    return conn


# Test 1: Prefix Extraction Logic
print("1. WPX PREFIX EXTRACTION TEST")
print("-" * 70)

db = create_test_db()
analyzer = NeededContactsAnalyzer(db)

test_callsigns = [
    # (callsign, expected_prefix)
    ('W4GNS', 'W4'),          # Standard US call
    ('W4GNS/P', 'W4'),        # Portable indicator
    ('W4GNS/M', 'W4'),        # Mobile indicator
    ('W4GNS/MM', 'W4'),       # Maritime mobile
    ('W4GNS/QRP', 'W4'),      # QRP indicator
    ('W1AW/2', 'W2'),         # Operating from call area 2 (W + 2)
    ('KH6/W4GNS', 'KH6'),     # Operating from Hawaii (prefix before /)
    ('G4ABC', 'G4'),          # UK call
    ('DL1ABC', 'DL1'),        # German call
    ('JA1ABC', 'JA1'),        # Japanese call
    ('VE3ABC', 'VE3'),        # Canadian call
    ('VP9/K1ABC', 'VP9'),     # Bermuda prefix (short prefix before full call)
    ('K1ABC/VP9', 'VP9'),     # Same, different format
    ('HALLOWEEN', 'HALLOWEEN'),  # Special event (no number)
    ('', None),               # Empty string
]

prefix_issues = []
for callsign, expected_prefix in test_callsigns:
    result = analyzer._extract_prefix(callsign)
    if result == expected_prefix:
        print(f"  \u2713 {callsign:15} -> {result}")
    else:
        print(f"  \u2717 {callsign:15} -> {result:15} EXPECTED: {expected_prefix}")
        prefix_issues.append(callsign)

print()


# Test 2: Cache Timeout Logic
print("2. CACHE TIMEOUT LOGIC TEST")
print("-" * 70)

# Test that cache uses total_seconds correctly
db = create_test_db()
analyzer = NeededContactsAnalyzer(db)
analyzer.cache_timeout = 60  # 60 seconds

# First analysis should not be cached
result1 = analyzer.analyze_spot('W4GNS', '20M', 'CW')
print(f"  Initial analysis: is_needed={result1.is_needed}")

# Second analysis with same params should hit cache
result2 = analyzer.analyze_spot('W4GNS', '20M', 'CW')
cache_key = 'W4GNS_20M_CW'
if cache_key in analyzer._cache:
    print(f"  \u2713 Spot is cached as expected")
else:
    print(f"  \u2717 Spot should be cached but is not")
    prefix_issues.append('cache_test')

# Verify cache stats
stats = analyzer.get_cache_stats()
print(f"  Cache entries: {stats['entries']}")
print(f"  Cache timeout: {stats['timeout_seconds']}s")

# Test cache clearing
analyzer.clear_cache()
stats = analyzer.get_cache_stats()
if stats['entries'] == 0:
    print(f"  \u2713 Cache cleared successfully")
else:
    print(f"  \u2717 Cache not cleared: {stats['entries']} entries remain")
    prefix_issues.append('cache_clear')

print()


# Test 3: Already Worked Check
print("3. ALREADY WORKED CHECK TEST")
print("-" * 70)

db = create_test_db()
cursor = db.cursor()

# Add a worked contact
cursor.execute("""
    INSERT INTO contacts (callsign, band, mode)
    VALUES ('W1AW', '20M', 'CW')
""")
db.commit()

analyzer = NeededContactsAnalyzer(db)

# Check worked contact
result = analyzer._already_worked('W1AW', '20M', 'CW')
if result:
    print(f"  \u2713 W1AW on 20M CW correctly marked as worked")
else:
    print(f"  \u2717 W1AW on 20M CW should be marked as worked")
    prefix_issues.append('already_worked_1')

# Check same call, different band
result = analyzer._already_worked('W1AW', '40M', 'CW')
if not result:
    print(f"  \u2713 W1AW on 40M CW correctly marked as NOT worked")
else:
    print(f"  \u2717 W1AW on 40M CW should NOT be marked as worked")
    prefix_issues.append('already_worked_2')

# Check unworked call
result = analyzer._already_worked('K1ABC', '20M', 'CW')
if not result:
    print(f"  \u2713 K1ABC on 20M CW correctly marked as NOT worked")
else:
    print(f"  \u2717 K1ABC should NOT be marked as worked")
    prefix_issues.append('already_worked_3')

print()


# Test 4: WPX Awards Check
print("4. WPX AWARDS CHECK TEST")
print("-" * 70)

db = create_test_db()
cursor = db.cursor()

# Add some worked prefixes
cursor.execute("INSERT INTO contacts (callsign) VALUES ('W4ABC')")
cursor.execute("INSERT INTO contacts (callsign) VALUES ('K1XYZ')")
cursor.execute("INSERT INTO contacts (callsign) VALUES ('VE3TEST')")
db.commit()

analyzer = NeededContactsAnalyzer(db)

# Check for new prefix
reasons = analyzer._check_wpx_awards('DL1ABC', '20M', 'CW')
if len(reasons) > 0 and 'DL1' in reasons[0].reason:
    print(f"  \u2713 DL1ABC correctly identified as new prefix: {reasons[0].reason}")
else:
    print(f"  \u2717 DL1ABC should be identified as new prefix")
    prefix_issues.append('wpx_new_prefix')

# Check for already worked prefix
reasons = analyzer._check_wpx_awards('W4XYZ', '20M', 'CW')
if len(reasons) == 0:
    print(f"  \u2713 W4XYZ correctly NOT identified (W4 already worked)")
else:
    print(f"  \u2717 W4XYZ should NOT be needed (W4 prefix already worked)")
    prefix_issues.append('wpx_worked_prefix')

print()


# Test 5: Edge Cases with Empty/Null Input
print("5. EDGE CASES TEST")
print("-" * 70)

db = create_test_db()
analyzer = NeededContactsAnalyzer(db)

# Test with empty callsign
result = analyzer.analyze_spot('', '20M', 'CW')
if isinstance(result, SpotAnalysis):
    print(f"  \u2713 Empty callsign handled gracefully")
else:
    print(f"  \u2717 Empty callsign caused error")
    prefix_issues.append('edge_empty_callsign')

# Test with None values
result = analyzer.analyze_spot('W4GNS', '20M', 'CW',
                               state=None, country=None,
                               continent=None, gridsquare=None)
if isinstance(result, SpotAnalysis):
    print(f"  \u2713 None optional params handled gracefully")
else:
    print(f"  \u2717 None params caused error")
    prefix_issues.append('edge_none_params')

# Test WAS with invalid state
reasons = analyzer._check_was_awards('W4GNS', '20M', 'CW', 'INVALID')
if len(reasons) == 0:
    print(f"  \u2713 Invalid state correctly rejected")
else:
    print(f"  \u2717 Invalid state should be rejected")
    prefix_issues.append('edge_invalid_state')

# Test VUCC with invalid gridsquare
reasons = analyzer._check_vucc_awards('W4GNS', '6M', 'CW', 'AB')
if len(reasons) == 0:
    print(f"  \u2713 Invalid gridsquare (too short) correctly rejected")
else:
    print(f"  \u2717 Invalid gridsquare should be rejected")
    prefix_issues.append('edge_invalid_grid')

print()


# Test 6: SKCC Awards Check
print("6. SKCC AWARDS CHECK TEST")
print("-" * 70)

db = create_test_db()
cursor = db.cursor()

# Add a tribune member
cursor.execute("INSERT INTO skcc_tribune_members (skcc_number) VALUES ('12345')")
# Add a senator member
cursor.execute("INSERT INTO skcc_senator_members (skcc_number) VALUES ('99999')")
db.commit()

analyzer = NeededContactsAnalyzer(db)

# Test with SKCC member (non-CW mode should return empty)
reasons = analyzer._check_skcc_awards('W4GNS', '20M', 'SSB', '12345')
if len(reasons) == 0:
    print(f"  \u2713 SSB mode correctly returns no SKCC reasons")
else:
    print(f"  \u2717 SSB mode should return no SKCC reasons")
    prefix_issues.append('skcc_mode')

# Test with CW mode and tribune member
reasons = analyzer._check_skcc_awards('W4GNS', '20M', 'CW', '12345')
tribune_found = any('Tribune' in r.award_name for r in reasons)
if tribune_found:
    print(f"  \u2713 Tribune member correctly identified")
else:
    print(f"  \u2717 Tribune member should be identified")
    prefix_issues.append('skcc_tribune')

# Test with senator member
reasons = analyzer._check_skcc_awards('K1ABC', '20M', 'CW', '99999')
senator_found = any('Senator' in r.award_name for r in reasons)
if senator_found:
    print(f"  \u2713 Senator member correctly identified")
else:
    print(f"  \u2717 Senator member should be identified")
    prefix_issues.append('skcc_senator')

print()


# Test 7: SpotAnalysis Properties
print("7. SPOT ANALYSIS PROPERTIES TEST")
print("-" * 70)

# Test priority labels
analysis = SpotAnalysis(callsign='W4GNS', is_needed=True,
                        reasons=[NeededReason('WAS', 'New state', 1, 40, 50)],
                        highest_priority=1)
if analysis.priority_label == 'HIGH':
    print(f"  \u2713 Priority 1 correctly labeled as HIGH")
else:
    print(f"  \u2717 Priority 1 should be HIGH, got {analysis.priority_label}")
    prefix_issues.append('priority_high')

analysis = SpotAnalysis(callsign='W4GNS', is_needed=True,
                        reasons=[NeededReason('WAS', 'New state', 2, 20, 50)],
                        highest_priority=2)
if analysis.priority_label == 'MEDIUM':
    print(f"  \u2713 Priority 2 correctly labeled as MEDIUM")
else:
    print(f"  \u2717 Priority 2 should be MEDIUM, got {analysis.priority_label}")
    prefix_issues.append('priority_medium')

analysis = SpotAnalysis(callsign='W4GNS', is_needed=True,
                        reasons=[NeededReason('WPX', 'New prefix', 3, 100, 300)],
                        highest_priority=3)
if analysis.priority_label == 'LOW':
    print(f"  \u2713 Priority 3 correctly labeled as LOW")
else:
    print(f"  \u2717 Priority 3 should be LOW, got {analysis.priority_label}")
    prefix_issues.append('priority_low')

analysis = SpotAnalysis(callsign='W4GNS', is_needed=False, reasons=[], highest_priority=99)
if analysis.priority_label == 'Not Needed':
    print(f"  \u2713 Not needed correctly labeled")
else:
    print(f"  \u2717 Not needed label incorrect, got {analysis.priority_label}")
    prefix_issues.append('priority_not_needed')

# Test reason summary
reasons = [
    NeededReason('WAS', 'New state: TX', 1, 40, 50),
    NeededReason('DXCC', 'New country: USA', 2, 80, 100),
]
analysis = SpotAnalysis(callsign='W4GNS', is_needed=True, reasons=reasons, highest_priority=1)
summary = analysis.get_reason_summary()
if 'WAS' in summary and 'DXCC' in summary:
    print(f"  \u2713 Reason summary correctly includes multiple reasons")
else:
    print(f"  \u2717 Reason summary should include multiple reasons")
    prefix_issues.append('reason_summary')

print()


# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print()

if len(prefix_issues) == 0:
    print("\u2713 All NeededContactsAnalyzer tests PASSED!")
else:
    print(f"\u2717 Found {len(prefix_issues)} issue(s):")
    for issue in prefix_issues:
        print(f"  - {issue}")

print()
print("="*70)
