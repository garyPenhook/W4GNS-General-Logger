"""
Award Export Utility

Provides utilities for exporting qualifying contacts for SKCC award applications.
Award managers require ADIF files containing only the contacts that qualify for
the specific award being applied for.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AwardExporter:
    """Export qualifying contacts for SKCC awards"""

    def __init__(self, database):
        """
        Initialize award exporter

        Args:
            database: Database instance
        """
        self.database = database

    def export_award_application(
        self,
        award_instance,
        output_directory: str = "exports",
        callsign: Optional[str] = None,
        include_award_info: bool = True
    ) -> str:
        """
        Export an award application ADIF file with qualifying contacts.

        Args:
            award_instance: Instance of an SKCC award (e.g., CenturionAward)
            output_directory: Directory to save export files
            callsign: Optional callsign to include in filename
            include_award_info: Add award name to contact comments

        Returns:
            str: Path to exported ADIF file

        Raises:
            ValueError: If no qualifying contacts found
            IOError: If file cannot be written
        """
        # Get all contacts from database
        contacts = self._get_all_contacts()

        if not contacts:
            raise ValueError("No contacts found in database")

        # Generate filename
        award_name = award_instance.name.replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if callsign:
            filename = f"{callsign}_{award_name}_Application_{timestamp}.adi"
        else:
            filename = f"{award_name}_Application_{timestamp}.adi"

        # Create output directory if needed
        os.makedirs(output_directory, exist_ok=True)

        filepath = os.path.join(output_directory, filename)

        # Export qualifying contacts
        try:
            count = award_instance.export_qualifying_contacts_to_adif(
                contacts,
                filepath,
                include_award_info=include_award_info
            )

            logger.info(
                f"Exported {count} qualifying contacts for {award_instance.name} "
                f"award to {filepath}"
            )

            return filepath

        except Exception as e:
            logger.error(f"Failed to export {award_instance.name} award: {e}")
            raise

    def export_multiple_awards(
        self,
        award_instances: List,
        output_directory: str = "exports",
        callsign: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export application files for multiple awards.

        Args:
            award_instances: List of SKCC award instances
            output_directory: Directory to save export files
            callsign: Optional callsign to include in filenames

        Returns:
            Dict[str, str]: Mapping of award names to exported file paths

        Note:
            Awards with no qualifying contacts will be skipped with a warning
        """
        results = {}

        for award in award_instances:
            try:
                filepath = self.export_award_application(
                    award,
                    output_directory=output_directory,
                    callsign=callsign
                )
                results[award.name] = filepath

            except ValueError as e:
                logger.warning(
                    f"Skipping {award.name} award - no qualifying contacts: {e}"
                )
                results[award.name] = None

            except Exception as e:
                logger.error(f"Error exporting {award.name} award: {e}")
                results[award.name] = None

        return results

    def export_all_ready_awards(
        self,
        output_directory: str = "exports",
        callsign: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export application files for all awards that have been achieved.

        Checks progress for each award and only exports those that are
        marked as achieved (100% progress).

        Args:
            output_directory: Directory to save export files
            callsign: Optional callsign to include in filenames

        Returns:
            Dict[str, str]: Mapping of award names to exported file paths
        """
        # Import all award classes
        from src.skcc_awards import (
            CenturionAward, TribuneAward, SenatorAward,
            TripleKeyAward, RagChewAward, MarathonAward,
            CanadianMapleAward, SKCCDXQAward, SKCCDXCAward,
            PFXAward, QRPMPWAward,
            SKCCWASAward, SKCCWASTAward, SKCCWASSAward, SKCCWACAward
        )

        # Instantiate all awards
        all_awards = [
            CenturionAward(self.database),
            TribuneAward(self.database),
            SenatorAward(self.database),
            TripleKeyAward(self.database),
            RagChewAward(self.database),
            MarathonAward(self.database),
            CanadianMapleAward(self.database),
            SKCCDXQAward(self.database),
            SKCCDXCAward(self.database),
            PFXAward(self.database),
            QRPMPWAward(self.database),
            SKCCWASAward(self.database),
            SKCCWASTAward(self.database),
            SKCCWASSAward(self.database),
            SKCCWACAward(self.database)
        ]

        # Get all contacts
        contacts = self._get_all_contacts()

        # Check which awards are achieved
        ready_awards = []
        for award in all_awards:
            try:
                progress = award.calculate_progress(contacts)
                if progress.get('achieved', False):
                    ready_awards.append(award)
                    logger.info(f"{award.name} award is achieved - ready for export")
                else:
                    logger.debug(
                        f"{award.name} award not yet achieved "
                        f"({progress.get('progress_pct', 0):.1f}%)"
                    )
            except Exception as e:
                logger.warning(f"Error checking {award.name} progress: {e}")

        if not ready_awards:
            logger.info("No awards are ready for submission yet")
            return {}

        # Export ready awards
        logger.info(f"Exporting {len(ready_awards)} ready awards")
        return self.export_multiple_awards(
            ready_awards,
            output_directory=output_directory,
            callsign=callsign
        )

    def _get_all_contacts(self) -> List[Dict[str, Any]]:
        """
        Get all contacts from the database.

        Returns:
            List of contact dictionaries
        """
        # Check if database has a method to get all contacts
        if hasattr(self.database, 'get_all_contacts'):
            return self.database.get_all_contacts()

        # Otherwise, query directly
        if hasattr(self.database, 'conn'):
            cursor = self.database.conn.cursor()
            cursor.execute("SELECT * FROM contacts")
            rows = cursor.fetchall()

            # Convert Row objects to dictionaries
            contacts = []
            for row in rows:
                contact = {key: row[key] for key in row.keys()}
                contacts.append(contact)

            return contacts

        raise NotImplementedError("Database does not support contact retrieval")


def export_award_for_submission(
    award_instance,
    database,
    output_directory: str = "exports",
    callsign: Optional[str] = None
) -> str:
    """
    Convenience function to export a single award application.

    Args:
        award_instance: Instance of an SKCC award
        database: Database instance
        output_directory: Directory to save export file
        callsign: Optional callsign to include in filename

    Returns:
        str: Path to exported ADIF file

    Example:
        >>> from src.database import Database
        >>> from src.skcc_awards import CenturionAward
        >>> db = Database('logbook.db')
        >>> award = CenturionAward(db)
        >>> filepath = export_award_for_submission(award, db, callsign='W4GNS')
        >>> print(f"Exported to: {filepath}")
    """
    exporter = AwardExporter(database)
    return exporter.export_award_application(
        award_instance,
        output_directory=output_directory,
        callsign=callsign
    )


def export_all_awards(
    database,
    output_directory: str = "exports",
    callsign: Optional[str] = None,
    only_achieved: bool = False
) -> Dict[str, str]:
    """
    Export all SKCC awards (or only achieved ones).

    Args:
        database: Database instance
        output_directory: Directory to save export files
        callsign: Optional callsign to include in filenames
        only_achieved: If True, only export awards that are 100% complete

    Returns:
        Dict[str, str]: Mapping of award names to exported file paths

    Example:
        >>> from src.database import Database
        >>> db = Database('logbook.db')
        >>> results = export_all_awards(db, callsign='W4GNS', only_achieved=True)
        >>> for award_name, filepath in results.items():
        ...     if filepath:
        ...         print(f"{award_name}: {filepath}")
    """
    exporter = AwardExporter(database)

    if only_achieved:
        return exporter.export_all_ready_awards(
            output_directory=output_directory,
            callsign=callsign
        )

    # Export all awards (will skip those with no qualifying contacts)
    from src.skcc_awards import (
        CenturionAward, TribuneAward, SenatorAward,
        TripleKeyAward, RagChewAward, MarathonAward,
        CanadianMapleAward, SKCCDXQAward, SKCCDXCAward,
        PFXAward, QRPMPWAward,
        SKCCWASAward, SKCCWASTAward, SKCCWASSAward, SKCCWACAward
    )

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

    return exporter.export_multiple_awards(
        all_awards,
        output_directory=output_directory,
        callsign=callsign
    )
