"""
SKCC Awards Module

Implements all Straight Key Century Club (SKCC) award programs with exact rule compliance.

Awards Implemented:
- Centurion: Contact 100 different SKCC members
- Tribune: Contact 50 Tribune/Senator members (requires Centurion)
- Senator: Contact 200 Tribune/Senator members (requires Tribune x8)
- Triple Key: Contact 100 members with each key type
- Rag Chew: Accumulate 300 minutes of conversations
- Marathon: 100 QSOs of 60+ minutes each with different members
- Canadian Maple: 4 levels (Yellow, Orange, Red, Gold)
- SKCC DXQ: QSO-based DX contacts
- SKCC DXC: Country-based DX contacts
- PFX: 500,000 points from prefixes
- QRP MPW: Miles per watt achievement (1,000/1,500/2,000 MPW)
- QRP 1x/2x: Points-based QRP awards (300/150 points)
- SKCC WAS: All 50 US states
- SKCC WAS-T: All 50 US states (Tribune/Senator only)
- SKCC WAS-S: All 50 US states (Senator only)
- SKCC WAC: All 6 continents

All awards enforce:
- CW mode only
- Mechanical key policy (STRAIGHT, BUG, SIDESWIPER)
- SKCC membership requirements
- Date-specific validations
"""

__version__ = '1.0.0'
__author__ = 'W4GNS General Logger'

from .base import SKCCAwardBase
from .centurion import CenturionAward
from .tribune import TribuneAward
from .senator import SenatorAward
from .triple_key import TripleKeyAward
from .rag_chew import RagChewAward
from .marathon import MarathonAward
from .canadian_maple import CanadianMapleAward
from .skcc_dx import SKCCDXQAward, SKCCDXCAward
from .pfx import PFXAward
from .qrp_awards import QRP1xAward, QRP2xAward
from .qrp_mpw import QRPMPWAward
from .was import SKCCWASAward
from .was_t import SKCCWASTAward
from .was_s import SKCCWASSAward
from .wac import SKCCWACAward

__all__ = [
    'SKCCAwardBase',
    'CenturionAward',
    'TribuneAward',
    'SenatorAward',
    'TripleKeyAward',
    'RagChewAward',
    'MarathonAward',
    'CanadianMapleAward',
    'SKCCDXQAward',
    'SKCCDXCAward',
    'PFXAward',
    'QRP1xAward',
    'QRP2xAward',
    'QRPMPWAward',
    'SKCCWASAward',
    'SKCCWASTAward',
    'SKCCWASSAward',
    'SKCCWACAward',
]
