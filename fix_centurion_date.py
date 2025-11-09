#!/usr/bin/env python3
"""Fix Centurion date to correct value (August 11, 2025)"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config

def fix_centurion_date():
    """Update Centurion date to correct value"""

    config = Config()

    print("Updating SKCC Centurion Date")
    print("=" * 60)

    old_date = config.get('skcc.centurion_date', '')
    print(f"Current Centurion Date: {old_date}")

    new_date = '20250811'  # August 11, 2025
    print(f"New Centurion Date: {new_date} (August 11, 2025)")

    config.set('skcc.centurion_date', new_date)
    config.save()

    print("\n✓ Centurion date updated successfully!")
    print("\nNow when you export Tribune award application:")
    print("  - Only contacts from August 11, 2025 onwards will be included")
    print("  - Contacts before this date will be filtered out")
    print("\nRe-export your Tribune award application to see the correct contacts.")

if __name__ == '__main__':
    try:
        fix_centurion_date()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
