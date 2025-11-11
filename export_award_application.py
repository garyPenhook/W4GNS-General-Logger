#!/usr/bin/env python3
"""
Export SKCC Award Applications

This script exports qualifying contacts for SKCC awards to ADIF files
for submission to award managers.

Usage:
    # Export a specific award
    python3 export_award_application.py --award centurion --callsign W4GNS

    # Export all achieved awards
    python3 export_award_application.py --all-achieved --callsign W4GNS

    # Export all awards (including incomplete)
    python3 export_award_application.py --all --callsign W4GNS
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import Database
from award_export import AwardExporter
from text_award_export import TextAwardExporter
from skcc_awards import (
    CenturionAward, TribuneAward, SenatorAward,
    TripleKeyAward, RagChewAward, MarathonAward,
    CanadianMapleAward, SKCCDXQAward, SKCCDXCAward,
    PFXAward, QRPMPWAward,
    SKCCWASAward, SKCCWASTAward, SKCCWASSAward, SKCCWACAward
)


# Map award names to classes
AWARD_MAP = {
    'centurion': CenturionAward,
    'tribune': TribuneAward,
    'senator': SenatorAward,
    'triplekey': TripleKeyAward,
    'triple-key': TripleKeyAward,
    'ragchew': RagChewAward,
    'rag-chew': RagChewAward,
    'marathon': MarathonAward,
    'maple': CanadianMapleAward,
    'canadian-maple': CanadianMapleAward,
    'dxq': SKCCDXQAward,
    'dxc': SKCCDXCAward,
    'pfx': PFXAward,
    'qrp': QRPMPWAward,
    'qrp-mpw': QRPMPWAward,
    'was': SKCCWASAward,
    'was-t': SKCCWASTAward,
    'was-s': SKCCWASSAward,
    'wac': SKCCWACAward
}


def _export_all_text_awards(
    text_exporter,
    database,
    output_directory: str = "exports",
    callsign: str = None,
    applicant_name: str = None,
    applicant_address: str = None,
    user_skcc_number: str = None,
    only_achieved: bool = False
) -> dict:
    """
    Export all awards as text applications.

    Args:
        text_exporter: TextAwardExporter instance
        database: Database instance
        output_directory: Output directory
        callsign: Applicant's callsign
        applicant_name: Applicant's name
        applicant_address: Applicant's address
        user_skcc_number: Applicant's SKCC number
        only_achieved: If True, only export achieved awards

    Returns:
        Dict mapping award names to export paths
    """
    # Instantiate all awards
    all_awards = [
        CenturionAward(database),
        TribuneAward(database),
        SenatorAward(database),
        TripleKeyAward(database),
        RagChewAward(database),
        MarathonAward(database),
        CanadianMapleAward(database),
        SKCCDXQAward(database),
        SKCCDXCAward(database),
        PFXAward(database),
        QRPMPWAward(database),
        SKCCWASAward(database),
        SKCCWASTAward(database),
        SKCCWASSAward(database),
        SKCCWACAward(database)
    ]

    # Filter for achieved awards if requested
    if only_achieved:
        contacts = text_exporter._get_all_contacts()
        awards_to_export = []
        for award in all_awards:
            try:
                progress = award.calculate_progress(contacts)
                if progress.get('achieved', False):
                    awards_to_export.append(award)
            except Exception as e:
                print(f"  Warning: Could not check progress for {award.name}: {e}")
    else:
        awards_to_export = all_awards

    # Export each award
    results = {}
    for award in awards_to_export:
        try:
            filepath = text_exporter.export_award_application_as_text(
                award,
                output_directory=output_directory,
                callsign=callsign,
                applicant_name=applicant_name,
                applicant_address=applicant_address,
                user_skcc_number=user_skcc_number
            )
            results[award.name] = filepath
        except ValueError:
            # No qualifying contacts
            results[award.name] = None
        except Exception as e:
            print(f"  Error exporting {award.name}: {e}")
            results[award.name] = None

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Export SKCC award application files in ADIF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Export Centurion award:
    python3 export_award_application.py --award centurion --callsign W4GNS

  Export all achieved awards:
    python3 export_award_application.py --all-achieved --callsign W4GNS

  Export specific award to custom directory:
    python3 export_award_application.py --award was-t --callsign W4GNS --output /path/to/dir

Available awards:
  centurion, tribune, senator, triple-key, rag-chew, marathon,
  canadian-maple, dxq, dxc, pfx, qrp-mpw, was, was-t, was-s, wac
        '''
    )

    parser.add_argument(
        '--database',
        default='logbook.db',
        help='Path to logbook database (default: logbook.db)'
    )

    parser.add_argument(
        '--award',
        choices=list(AWARD_MAP.keys()),
        help='Specific award to export'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Export all awards (including incomplete)'
    )

    parser.add_argument(
        '--all-achieved',
        action='store_true',
        help='Export only awards that are 100%% complete'
    )

    parser.add_argument(
        '--callsign',
        help='Your callsign (included in filename)'
    )

    parser.add_argument(
        '--output',
        default='exports',
        help='Output directory for ADIF files (default: exports)'
    )

    parser.add_argument(
        '--list-awards',
        action='store_true',
        help='List all available awards and exit'
    )

    parser.add_argument(
        '--format',
        choices=['adif', 'text'],
        default='text',
        help='Export format: adif (ADIF file) or text (formatted text application) (default: text)'
    )

    parser.add_argument(
        '--applicant-name',
        help='Applicant\'s full name (for text format)'
    )

    parser.add_argument(
        '--applicant-address',
        help='Applicant\'s address (e.g., "Penhook, VA") (for text format)'
    )

    parser.add_argument(
        '--skcc-number',
        help='Applicant\'s SKCC number (for text format)'
    )

    args = parser.parse_args()

    # List awards and exit
    if args.list_awards:
        print("Available SKCC Awards:")
        print("=" * 50)
        for key, award_class in sorted(AWARD_MAP.items()):
            # Create temporary instance to get name
            try:
                db = Database(args.database)
                award = award_class(db)
                print(f"  {key:20s} - {award.name}")
            except Exception as e:
                print(f"  {key:20s} - (error loading)")
        return 0

    # Validate arguments
    if not args.award and not args.all and not args.all_achieved:
        parser.error("Must specify --award, --all, or --all-achieved")

    if sum([bool(args.award), args.all, args.all_achieved]) > 1:
        parser.error("Can only specify one of --award, --all, or --all-achieved")

    # Connect to database
    if not os.path.exists(args.database):
        print(f"Error: Database not found: {args.database}")
        return 1

    try:
        db = Database(args.database)
        exporter = AwardExporter(db)
    except Exception as e:
        print(f"Error opening database: {e}")
        return 1

    # Export specific award
    if args.award:
        award_class = AWARD_MAP[args.award]
        award = award_class(db)

        try:
            print(f"Exporting {award.name} award ({args.format.upper()} format)...")

            if args.format == 'text':
                text_exporter = TextAwardExporter(db)
                filepath = text_exporter.export_award_application_as_text(
                    award,
                    output_directory=args.output,
                    callsign=args.callsign,
                    applicant_name=args.applicant_name,
                    applicant_address=args.applicant_address,
                    user_skcc_number=args.skcc_number
                )
            else:  # ADIF format
                filepath = exporter.export_award_application(
                    award,
                    output_directory=args.output,
                    callsign=args.callsign
                )

            print(f"✓ Exported to: {filepath}")

            # Get count of qualifying contacts
            contacts = exporter._get_all_contacts()
            qualifying = [c for c in contacts if award.validate(c)]
            print(f"  {len(qualifying)} qualifying contacts")

            return 0

        except ValueError as e:
            print(f"✗ {e}")
            return 1
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1

    # Export all achieved awards
    elif args.all_achieved:
        print(f"Exporting all achieved awards ({args.format.upper()} format)...")
        try:
            if args.format == 'text':
                text_exporter = TextAwardExporter(db)
                results = _export_all_text_awards(
                    text_exporter,
                    db,
                    output_directory=args.output,
                    callsign=args.callsign,
                    applicant_name=args.applicant_name,
                    applicant_address=args.applicant_address,
                    user_skcc_number=args.skcc_number,
                    only_achieved=True
                )
            else:  # ADIF format
                results = exporter.export_all_ready_awards(
                    output_directory=args.output,
                    callsign=args.callsign
                )

            if not results:
                print("No awards are ready for submission yet.")
                return 0

            success_count = sum(1 for path in results.values() if path)
            print(f"\nExported {success_count} awards:")

            for award_name, filepath in results.items():
                if filepath:
                    print(f"  ✓ {award_name:20s} -> {filepath}")
                else:
                    print(f"  ✗ {award_name:20s} (no qualifying contacts)")

            return 0

        except Exception as e:
            print(f"✗ Error: {e}")
            return 1

    # Export all awards
    elif args.all:
        print(f"Exporting all awards ({args.format.upper()} format)...")

        all_awards = [award_class(db) for award_class in AWARD_MAP.values()]

        try:
            if args.format == 'text':
                text_exporter = TextAwardExporter(db)
                results = _export_all_text_awards(
                    text_exporter,
                    db,
                    output_directory=args.output,
                    callsign=args.callsign,
                    applicant_name=args.applicant_name,
                    applicant_address=args.applicant_address,
                    user_skcc_number=args.skcc_number,
                    only_achieved=False
                )
            else:  # ADIF format
                results = exporter.export_multiple_awards(
                    all_awards,
                    output_directory=args.output,
                    callsign=args.callsign
                )

            success_count = sum(1 for path in results.values() if path)
            print(f"\nExported {success_count} awards:")

            for award_name, filepath in results.items():
                if filepath:
                    print(f"  ✓ {award_name:20s} -> {filepath}")
                else:
                    print(f"  - {award_name:20s} (no qualifying contacts)")

            return 0

        except Exception as e:
            print(f"✗ Error: {e}")
            return 1


if __name__ == '__main__':
    sys.exit(main())
