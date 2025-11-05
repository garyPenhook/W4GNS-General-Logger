"""
SKCC Award Base Class

Abstract base class for all SKCC award programs.
Defines common interface and validation logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.skcc_awards.constants import VALID_KEY_TYPES


class SKCCAwardBase(ABC):
    """Abstract base class for SKCC award programs"""

    def __init__(self, name: str, program_id: str, database):
        """
        Initialize SKCC award program

        Args:
            name: Human-readable award name (e.g., "Centurion")
            program_id: Unique program identifier (e.g., "SKCC_CENTURION")
            database: Database instance for querying contacts and member lists
        """
        self.name = name
        self.program_id = program_id
        self.database = database

    @abstractmethod
    def validate(self, contact: Dict[str, Any]) -> bool:
        """
        Check if a contact qualifies for this award

        CRITICAL RULES (enforced by all SKCC awards):
        1. CW mode only
        2. Mechanical key policy (STRAIGHT, BUG, or SIDESWIPER)
        3. SKCC membership (both operators)
        4. Award-specific date restrictions

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact qualifies, False otherwise
        """
        pass

    @abstractmethod
    def calculate_progress(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate current progress toward award

        Args:
            contacts: List of contact records

        Returns:
            Dictionary with progress information:
            {
                'current': int,      # Current count/points
                'required': int,     # Required count/points
                'achieved': bool,    # Whether award is achieved
                'progress_pct': float,  # Progress percentage
                'endorsement': str,  # Current endorsement level
                ...  # Award-specific fields
            }
        """
        pass

    @abstractmethod
    def get_requirements(self) -> Dict[str, Any]:
        """
        Return award requirements

        Returns:
            Dictionary with award requirements
        """
        pass

    @abstractmethod
    def get_endorsements(self) -> List[Dict[str, Any]]:
        """
        Return list of endorsement levels

        Returns:
            List of endorsement level dictionaries
        """
        pass

    def get_name(self) -> str:
        """Get award name"""
        return self.name

    def get_program_id(self) -> str:
        """Get program ID"""
        return self.program_id

    def validate_common_rules(self, contact: Dict[str, Any]) -> bool:
        """
        Validate common SKCC award rules

        CRITICAL: All SKCC awards require:
        1. CW mode only
        2. Mechanical key (STRAIGHT, BUG, or SIDESWIPER)
        3. SKCC number present

        Args:
            contact: Contact record dictionary

        Returns:
            True if contact meets common SKCC requirements
        """
        # Must be CW mode
        if contact.get('mode', '').upper() != 'CW':
            return False

        # Must have SKCC number
        if not contact.get('skcc_number'):
            return False

        # CRITICAL RULE: SKCC Mechanical Key Policy
        # Contact must use mechanical key (STRAIGHT, BUG, or SIDESWIPER)
        # Electronic keyers are NOT allowed
        key_type = contact.get('key_type', '').upper()
        if key_type and key_type not in VALID_KEY_TYPES:
            return False

        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.program_id}, name={self.name})>"
