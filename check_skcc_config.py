#!/usr/bin/env python3
"""Check user's SKCC configuration dates"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config

def check_skcc_config():
    """Check SKCC configuration settings"""

    config = Config()

    print("SKCC Configuration Check")
    print("=" * 60)

    callsign = config.get('callsign', '')
    print(f"Callsign: {callsign}")

    skcc_number = config.get('skcc.my_number', '')
    print(f"SKCC Number: {skcc_number}")

    join_date = config.get('skcc.join_date', '')
    print(f"SKCC Join Date: {join_date if join_date else 'NOT SET ⚠️'}")

    centurion_date = config.get('skcc.centurion_date', '')
    print(f"Centurion Date: {centurion_date if centurion_date else 'NOT SET ⚠️'}")

    tribune_date = config.get('skcc.tribune_date', '')
    print(f"Tribune Date: {tribune_date if tribune_date else 'NOT SET (optional)'}")

    print("\n" + "=" * 60)

    if not centurion_date:
        print("\n⚠️  WARNING: Centurion Date is not set!")
        print("\nThis is why contacts before you earned Centurion are being included")
        print("in your Tribune award report.")
        print("\nThe Tribune award requires:")
        print("  - You must be a Centurion first")
        print("  - Contacts only count AFTER you earned Centurion")
        print("\nWithout your Centurion date set, the app cannot filter out")
        print("contacts from before you achieved Centurion status.")
        print("\nTo fix this:")
        print("  1. Open the app")
        print("  2. Go to Settings → SKCC tab")
        print("  3. Set your 'Centurion Achievement Date'")
        print("  4. Re-export your Tribune award application")
        return False
    else:
        print("\n✓ All required dates are configured")
        return True

if __name__ == '__main__':
    try:
        check_skcc_config()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
