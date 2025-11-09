#!/usr/bin/env python3
"""Test that award application uses correct applicant callsign"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.skcc_awards.award_application import AwardApplicationGenerator
from src.config import Config

def test_applicant_callsign():
    """Test that the certification line uses the user's callsign, not the last contact's"""

    # Create a mock config
    config = Config()
    config.set('callsign', 'W4GNS')
    config.set('operator_name', 'Gary')
    config.set('skcc.my_number', '12345C')
    config.set('skcc.centurion_date', '20230101')

    # Create generator
    generator = AwardApplicationGenerator(database=None, config=config)

    # Create test contacts - last one is NQ2W
    contacts = [
        {
            'date': '2025-11-08',
            'callsign': 'KA0WKG',
            'skcc_number': '22368S',
            'name': 'DANIEL K KAFKA',
            'state': 'CO',
            'band': '15M'
        },
        {
            'date': '2025-11-09',
            'callsign': 'NQ2W',
            'skcc_number': '25403S',
            'name': 'ANTHONY W JAACKS',
            'state': 'NY',
            'band': '40M'
        }
    ]

    # Generate report
    report = generator.generate_tribune_report(contacts)

    print("Generated Report:")
    print("=" * 80)
    print(report)
    print("=" * 80)
    print()

    # Check certification line
    if "I, Gary, certify" in report:
        print("✅ PASS: Certification uses operator name (Gary)")
        return True
    elif "I, W4GNS, certify" in report:
        print("✅ PASS: Certification uses user callsign (W4GNS)")
        return True
    elif "I, NQ2W, certify" in report:
        print("❌ FAIL: Certification incorrectly uses last contact's callsign (NQ2W)")
        return False
    else:
        print("❌ FAIL: Could not find certification line")
        return False

if __name__ == '__main__':
    try:
        success = test_applicant_callsign()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
