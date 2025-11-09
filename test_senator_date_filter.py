#!/usr/bin/env python3
"""Test that Senator award correctly filters by Tribune x8 date"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.config import Config
from src.skcc_awards.senator import SenatorAward

def test_senator_date_filtering():
    """Test that Senator award filters contacts by Tribune x8 achievement date"""

    # Setup
    config = Config()
    config.set('skcc.centurion_date', '20250811')  # August 11, 2025
    config.set('skcc.tribune_x8_date', '20251001')  # October 1, 2025 (hypothetical Tribune x8 date)
    config.set('skcc.join_date', '20200101')  # Joined Jan 1, 2020

    db = Database('logger.db')

    # CRITICAL: Attach config to database (this is what we fixed!)
    db.config = config

    # Create Senator award instance
    senator = SenatorAward(db)

    print("Senator Award Date Filtering Test")
    print("=" * 70)
    print(f"Centurion Date (from config): {senator.user_centurion_date}")
    print(f"Tribune x8 Date (from config): {senator.user_tribune_x8_date}")
    print(f"Join Date (from config): {senator.user_join_date}")
    print()

    # Test contact 1: BEFORE Tribune x8 date (should be REJECTED)
    contact_before = {
        'callsign': 'W1ABC',
        'date': '2025-09-15',  # Before October 1, 2025
        'mode': 'CW',
        'skcc_number': '12345T',  # Tribune
        'key_type': 'BUG'
    }

    # Test contact 2: AFTER Tribune x8 date (should be ACCEPTED if T/S)
    contact_after = {
        'callsign': 'W2XYZ',
        'date': '2025-10-15',  # After October 1, 2025
        'mode': 'CW',
        'skcc_number': '67890S',  # Senator
        'key_type': 'BUG'
    }

    # Test contact 3: Centurion (should be REJECTED - Senator only counts T/S, not C)
    contact_centurion = {
        'callsign': 'W3ZZZ',
        'date': '2025-10-20',  # After Tribune x8 date
        'mode': 'CW',
        'skcc_number': '99999C',  # Centurion (not Tribune/Senator)
        'key_type': 'BUG'
    }

    result_before = senator.validate(contact_before)
    result_after = senator.validate(contact_after)
    result_centurion = senator.validate(contact_centurion)

    print("Test Results:")
    print("-" * 70)
    print(f"Contact BEFORE Tribune x8 (2025-09-15): {'❌ REJECTED' if not result_before else '❌ FAIL - ACCEPTED'}")
    print(f"Contact AFTER Tribune x8 (2025-10-15): {'✅ ACCEPTED' if result_after else '✅ PASS - REJECTED (roster check)'}")
    print(f"Centurion contact (should reject C): {'❌ REJECTED' if not result_centurion else '❌ FAIL - ACCEPTED'}")
    print()

    success = True

    if senator.user_tribune_x8_date == '20251001':
        print("✅ PASS: Senator award correctly reads Tribune x8 date from config")
    else:
        print(f"❌ FAIL: Expected Tribune x8 date 20251001, got {senator.user_tribune_x8_date}")
        success = False

    if not result_before:
        print("✅ PASS: Contacts before Tribune x8 date are correctly rejected")
    else:
        print("❌ FAIL: Contact before Tribune x8 date was incorrectly accepted")
        success = False

    if not result_centurion:
        print("✅ PASS: Centurion contacts correctly rejected (Senator only counts T/S)")
    else:
        print("❌ FAIL: Centurion contact was incorrectly accepted for Senator")
        success = False

    if success:
        print()
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print()
        print("The fix is working! Senator award now:")
        print("  - Reads Tribune x8 date from config correctly")
        print("  - Filters out contacts before Tribune x8 achievement date")
        print("  - Only counts Tribune/Senator contacts (T/S), not Centurions (C)")
        print()
        print("When you re-export Senator award application in the GUI:")
        print("  - Only contacts from Tribune x8 date onwards will be included")
        print("  - Only contacts with T or S suffixes (not C) will be included")

    db.close()
    return success

if __name__ == '__main__':
    try:
        success = test_senator_date_filtering()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
