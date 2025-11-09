#!/usr/bin/env python3
"""
Diagnose Tribune Award Contact Validation

Shows which contacts qualify vs. which are rejected and why.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import Database
from src.skcc_awards.tribune import TribuneAward
from src.utils.skcc_number import extract_base_skcc_number

def diagnose_tribune_contacts(db_path=None):
    """Diagnose Tribune award contact validation"""

    # Initialize database
    if db_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "logger.db")

    db = Database(db_path)
    tribune = TribuneAward(db)

    # Get all contacts
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT
            callsign, date, time_on, mode, skcc_number, key_type
        FROM contacts
        WHERE skcc_number IS NOT NULL AND skcc_number != ''
        ORDER BY date, time_on
    ''')

    contacts = cursor.fetchall()

    print(f"{'='*80}")
    print(f"TRIBUNE AWARD CONTACT VALIDATION DIAGNOSTIC")
    print(f"{'='*80}\n")

    # Convert to dictionaries
    contact_dicts = []
    for row in contacts:
        contact_dicts.append({
            'callsign': row[0],
            'date': row[1],
            'time_on': row[2],
            'mode': row[3],
            'skcc_number': row[4],
            'key_type': row[5]
        })

    # Track validation results
    valid_contacts = []
    invalid_contacts = []
    unique_valid = set()
    unique_invalid = set()

    reasons = {}

    for contact in contact_dicts:
        # Test validation
        is_valid = tribune.validate(contact)

        skcc_num = contact.get('skcc_number', '').strip()
        base_num = extract_base_skcc_number(skcc_num)

        if is_valid:
            valid_contacts.append(contact)
            if base_num:
                unique_valid.add(base_num)
        else:
            invalid_contacts.append(contact)
            if base_num:
                unique_invalid.add(base_num)

            # Determine rejection reason
            reason = get_rejection_reason(tribune, contact)
            reasons[f"{contact['callsign']}_{contact['date']}"] = reason

    # Show summary
    print(f"Total contacts with SKCC numbers: {len(contact_dicts)}")
    print(f"Valid for Tribune award: {len(valid_contacts)} ({len(unique_valid)} unique)")
    print(f"Invalid for Tribune award: {len(invalid_contacts)} ({len(unique_invalid)} unique)")
    print()

    # Show roster status
    roster_info = tribune.award_rosters.get_roster_info()
    print(f"Roster Status:")
    for award_type, info in roster_info.items():
        print(f"  {award_type.title()}: {info['count']} members, "
              f"age={info['age_days']} days, status={info['status']}")
    print()

    # Show rejection reasons summary
    if reasons:
        print(f"\nREJECTION REASONS (showing first 20):")
        print(f"{'-'*80}")
        for i, (key, reason) in enumerate(list(reasons.items())[:20]):
            call, date = key.rsplit('_', 1)
            print(f"{i+1}. {call} on {date}: {reason}")

        if len(reasons) > 20:
            print(f"\n... and {len(reasons) - 20} more rejected contacts")

    print(f"\n{'='*80}")
    print(f"UNIQUE CENTURION/TRIBUNE/SENATOR MEMBERS CONTACTED: {len(unique_valid)}")
    print(f"{'='*80}")

    db.close()


def get_rejection_reason(tribune, contact):
    """Determine why a contact was rejected"""

    # Check common rules
    if contact.get('mode', '').upper() != 'CW':
        return f"Not CW mode (mode={contact.get('mode')})"

    key_type = contact.get('key_type', '').upper()
    if key_type not in ['STRAIGHT', 'BUG', 'SIDESWIPER']:
        return f"Not mechanical key (key_type={key_type})"

    skcc_num = contact.get('skcc_number', '').strip()
    if not skcc_num:
        return "No SKCC number"

    # Check date
    qso_date = contact.get('date', '').replace('-', '')
    if qso_date < '20070301':
        return f"Before Tribune effective date (date={qso_date})"

    # Check special event calls after Oct 1, 2008
    callsign = contact.get('callsign', '').upper()
    base_call = callsign.split('/')[0]

    from src.skcc_awards.constants import SPECIAL_EVENT_CALLS, TRIBUNE_SPECIAL_EVENT_CUTOFF
    if qso_date >= TRIBUNE_SPECIAL_EVENT_CUTOFF and base_call in SPECIAL_EVENT_CALLS:
        return "Special event call after Oct 1, 2008"

    # Check SKCC membership
    if not tribune.roster_manager.was_member_on_date(base_call, qso_date):
        return f"Not SKCC member on {qso_date}"

    # Check user's join date
    if tribune.user_join_date and qso_date < tribune.user_join_date:
        return f"QSO before user join date ({tribune.user_join_date})"

    # Check if contact was Centurion/Tribune/Senator at time of QSO
    if not tribune.award_rosters.was_centurion_or_higher_on_date(skcc_num, qso_date):
        return f"NOT Centurion/Tribune/Senator on {qso_date} (SKCC#{skcc_num})"

    # Check user's Centurion date
    if tribune.user_centurion_date and qso_date < tribune.user_centurion_date:
        return f"QSO before user Centurion date ({tribune.user_centurion_date})"

    return "Unknown reason"


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Diagnose Tribune award validation')
    parser.add_argument('-d', '--database', help='Path to database file')

    args = parser.parse_args()

    try:
        diagnose_tribune_contacts(args.database)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
