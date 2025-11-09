#!/usr/bin/env python3
"""
Test that ADIF export properly deduplicates contacts by SKCC base number.
This test verifies the fix for the awards manager processing issue.
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from skcc_awards.base import SKCCAwardBase
from typing import Dict, Any, List


class MockAward(SKCCAwardBase):
    """Mock award class that accepts all contacts for testing deduplication"""

    def __init__(self):
        super().__init__(name="TestAward", program_id="TEST", database=None)

    def validate(self, contact: Dict[str, Any]) -> bool:
        """Accept all contacts for testing"""
        return True

    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

    def get_requirements(self) -> Dict[str, Any]:
        return {}

    def get_endorsements(self) -> List[Dict[str, Any]]:
        return []


def test_adif_export_deduplication():
    """Test that ADIF export removes duplicate SKCC members."""

    # Create a mock award instance that accepts all contacts
    award = MockAward()

    # Create test contacts with duplicate SKCC base numbers
    # Per SKCC rules: 12345C, 12345T, 12345S are all the same member (base: 12345)
    test_contacts = [
        {
            'id': 1,
            'date': '20250101',
            'time_on': '1200',
            'callsign': 'W1ABC',
            'skcc_number': '12345C',  # First contact with base 12345
            'mode': 'CW',
            'key_type': 'STRAIGHT',
            'name': 'John',
            'state': 'MA',
            'band': '20M'
        },
        {
            'id': 2,
            'date': '20250102',
            'time_on': '1300',
            'callsign': 'W1ABC',
            'skcc_number': '12345T',  # Duplicate - same base number (12345)
            'mode': 'CW',
            'key_type': 'STRAIGHT',
            'name': 'John',
            'state': 'MA',
            'band': '40M'
        },
        {
            'id': 3,
            'date': '20250103',
            'time_on': '1400',
            'callsign': 'W2DEF',
            'skcc_number': '67890C',  # Different member
            'mode': 'CW',
            'key_type': 'BUG',
            'name': 'Jane',
            'state': 'NY',
            'band': '20M'
        },
        {
            'id': 4,
            'date': '20250104',
            'time_on': '1500',
            'callsign': 'W1ABC',
            'skcc_number': '12345S',  # Another duplicate - same base (12345)
            'mode': 'CW',
            'key_type': 'STRAIGHT',
            'name': 'John',
            'state': 'MA',
            'band': '15M'
        },
        {
            'id': 5,
            'date': '20250105',
            'time_on': '1600',
            'callsign': 'K3GHI',
            'skcc_number': '11111C',  # Third unique member
            'mode': 'CW',
            'key_type': 'SIDESWIPER',
            'name': 'Bob',
            'state': 'PA',
            'band': '20M'
        },
    ]

    # Create temporary file for ADIF export
    with tempfile.NamedTemporaryFile(mode='w', suffix='.adi', delete=False) as f:
        temp_filename = f.name

    try:
        # Export contacts to ADIF
        count = award.export_qualifying_contacts_to_adif(
            test_contacts,
            temp_filename,
            include_award_info=True
        )

        # Read the exported file
        with open(temp_filename, 'r') as f:
            adif_content = f.read()

        print("=" * 70)
        print("ADIF DEDUPLICATION TEST")
        print("=" * 70)
        print(f"\nInput: 5 contacts")
        print(f"  - 3 contacts with SKCC base number 12345 (12345C, 12345T, 12345S)")
        print(f"  - 1 contact with SKCC base number 67890 (67890C)")
        print(f"  - 1 contact with SKCC base number 11111 (11111C)")
        print(f"\nExpected: 3 unique contacts exported (one per unique SKCC member)")
        print(f"Actual: {count} contacts exported")

        # Verify deduplication worked
        assert count == 3, f"Expected 3 contacts, got {count}"

        # Verify the correct contacts were kept (first occurrence of each base number)
        assert 'W1ABC' in adif_content, "W1ABC should be in export"
        assert 'W2DEF' in adif_content, "W2DEF should be in export"
        assert 'K3GHI' in adif_content, "K3GHI should be in export"

        # Count occurrences of W1ABC (should only appear once, not three times)
        w1abc_count = adif_content.count('<CALL:5>W1ABC')
        assert w1abc_count == 1, f"W1ABC should appear once, found {w1abc_count} times"

        # Verify the first contact was kept (should have 12345C, not T or S)
        assert '12345C' in adif_content, "Should keep first contact (12345C)"
        assert '12345T' not in adif_content, "Should not include 12345T (duplicate)"
        assert '12345S' not in adif_content, "Should not include 12345S (duplicate)"

        print("\n" + "=" * 70)
        print("✓ TEST PASSED")
        print("=" * 70)
        print("\nVerification:")
        print(f"  ✓ Exported exactly 3 contacts (not 5)")
        print(f"  ✓ W1ABC appears only once (first QSO with 12345C kept)")
        print(f"  ✓ Duplicate contacts (12345T, 12345S) were removed")
        print(f"  ✓ All unique SKCC members included (12345, 67890, 11111)")
        print("\nADIF export now correctly deduplicates by SKCC base number!")
        print("Awards manager should be able to process the report.\n")

        return True

    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


if __name__ == '__main__':
    try:
        test_adif_export_deduplication()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
