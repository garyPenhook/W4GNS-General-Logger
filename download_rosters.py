#!/usr/bin/env python3
"""
Download SKCC Award Rosters

Downloads the official Centurion, Tribune, and Senator rosters from SKCC website
and saves them to the database for validating award contacts.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.skcc_award_rosters import get_award_roster_manager

def download_all_rosters(db_path=None):
    """Download all SKCC award rosters"""

    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)

    print(f"{'='*80}")
    print(f"DOWNLOADING SKCC AWARD ROSTERS")
    print(f"{'='*80}\n")

    # Get roster manager
    roster_mgr = get_award_roster_manager(database=db)

    # Download all rosters
    results = roster_mgr.download_all_rosters(force=True)

    print(f"\n{'='*80}")
    print(f"DOWNLOAD RESULTS")
    print(f"{'='*80}")

    for award_type, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        count = len(roster_mgr.rosters.get(award_type, {}))
        print(f"{award_type.title():12s}: {status:12s} ({count} members)")

    # Show roster info
    print(f"\n{'='*80}")
    print(f"ROSTER INFORMATION")
    print(f"{'='*80}")

    roster_info = roster_mgr.get_roster_info()
    for award_type, info in roster_info.items():
        print(f"\n{award_type.title()} Roster:")
        print(f"  Loaded: {info['loaded']}")
        print(f"  Count: {info['count']} members")
        print(f"  Age: {info['age_days']} days")
        print(f"  Status: {info['status']}")

    db.close()

    print(f"\n{'='*80}")
    print(f"Rosters downloaded successfully!")
    print(f"You can now export Tribune award contacts.")
    print(f"{'='*80}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Download SKCC award rosters')
    parser.add_argument('-d', '--database', help='Path to database file')
    parser.add_argument('-f', '--force', action='store_true',
                       help='Force download even if cached files are recent')

    args = parser.parse_args()

    try:
        download_all_rosters(args.database)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
