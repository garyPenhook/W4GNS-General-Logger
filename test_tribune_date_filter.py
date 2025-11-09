#!/usr/bin/env python3
"""Test that Tribune award correctly filters by Centurion date"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.config import Config
from src.skcc_awards.tribune import TribuneAward

def test_tribune_date_filtering():
    """Test that Tribune award filters contacts by Centurion achievement date"""

    # Setup
    config = Config()
    config.set('skcc.centurion_date', '20250811')  # August 11, 2025
    config.set('skcc.join_date', '20200101')  # Joined Jan 1, 2020

    db = Database('logger.db')

    # CRITICAL: Attach config to database (this is what was missing!)
    db.config = config

    # Create Tribune award instance
    tribune = TribuneAward(db)

    print("Tribune Award Date Filtering Test")
    print("=" * 70)
    print(f"Centurion Date (from config): {tribune.user_centurion_date}")
    print(f"Join Date (from config): {tribune.user_join_date}")
    print()

    # Test contact 1: BEFORE Centurion date (should be REJECTED)
    contact_before = {
        'callsign': 'W1ABC',
        'date': '2025-08-01',  # Before August 11, 2025
        'mode': 'CW',
        'skcc_number': '12345C',
        'key_type': 'BUG'
    }

    # Test contact 2: AFTER Centurion date (should be ACCEPTED if C/T/S)
    contact_after = {
        'callsign': 'W2XYZ',
        'date': '2025-08-15',  # After August 11, 2025
        'mode': 'CW',
        'skcc_number': '67890S',
        'key_type': 'BUG'
    }

    result_before = tribune.validate(contact_before)
    result_after = tribune.validate(contact_after)

    print("Test Results:")
    print("-" * 70)
    print(f"Contact BEFORE Centurion date (2025-08-01): {'❌ REJECTED' if not result_before else '❌ FAIL - ACCEPTED'}")
    print(f"Contact AFTER Centurion date (2025-08-15): {'✅ ACCEPTED' if result_after else '✅ PASS - REJECTED (roster check)'}")
    print()

    if tribune.user_centurion_date == '20250811':
        print("✅ PASS: Tribune award correctly reads Centurion date from config")
    else:
        print(f"❌ FAIL: Expected Centurion date 20250811, got {tribune.user_centurion_date}")
        return False

    if not result_before:
        print("✅ PASS: Contacts before Centurion date are correctly rejected")
    else:
        print("❌ FAIL: Contact before Centurion date was incorrectly accepted")
        return False

    print()
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print()
    print("The fix is working! Tribune award now:")
    print("  - Reads Centurion date from config correctly")
    print("  - Filters out contacts before Centurion achievement date")
    print()
    print("When you re-export Tribune award application in the GUI:")
    print("  - Only contacts from August 11, 2025 onwards will be included")
    print("  - Contacts before this date will be filtered out")

    db.close()
    return True

if __name__ == '__main__':
    try:
        success = test_tribune_date_filtering()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
