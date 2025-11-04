"""
DXCC Entity Lookup
Provides country, continent, CQ zone, and ITU zone information from callsign prefixes
"""

# DXCC entities with prefix patterns, country info, and zones
# This is a subset of common DXCC entities - can be expanded as needed
DXCC_DATA = {
    # United States
    'K': {'country': 'United States', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 8, 'entity': 291},
    'W': {'country': 'United States', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 8, 'entity': 291},
    'N': {'country': 'United States', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 8, 'entity': 291},
    'A': {'country': 'United States', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 8, 'entity': 291},

    # Canada
    'VE': {'country': 'Canada', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 9, 'entity': 1},
    'VA': {'country': 'Canada', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 9, 'entity': 1},
    'VO': {'country': 'Canada', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 9, 'entity': 1},
    'VY': {'country': 'Canada', 'continent': 'NA', 'cq_zone': 2, 'itu_zone': 75, 'entity': 1},

    # Mexico
    'XE': {'country': 'Mexico', 'continent': 'NA', 'cq_zone': 6, 'itu_zone': 10, 'entity': 50},
    'XF': {'country': 'Mexico', 'continent': 'NA', 'cq_zone': 6, 'itu_zone': 10, 'entity': 50},

    # United Kingdom
    'G': {'country': 'England', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 223},
    'M': {'country': 'England', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 223},
    '2E': {'country': 'England', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 223},

    # Germany
    'DL': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DA': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DB': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DC': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DD': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DE': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DF': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DG': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DH': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DI': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DJ': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DK': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DM': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DN': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},
    'DO': {'country': 'Fed. Rep. of Germany', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 230},

    # France
    'F': {'country': 'France', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 227},

    # Italy
    'I': {'country': 'Italy', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 248},

    # Spain
    'EA': {'country': 'Spain', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 281},
    'AM': {'country': 'Spain', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 281},

    # Russia
    'R': {'country': 'Russia', 'continent': 'EU/AS', 'cq_zone': 16, 'itu_zone': 29, 'entity': 15},
    'U': {'country': 'Russia', 'continent': 'EU/AS', 'cq_zone': 16, 'itu_zone': 29, 'entity': 15},
    'RA': {'country': 'Russia', 'continent': 'EU/AS', 'cq_zone': 16, 'itu_zone': 29, 'entity': 15},
    'UA': {'country': 'Russia', 'continent': 'EU/AS', 'cq_zone': 16, 'itu_zone': 29, 'entity': 15},
    'RZ': {'country': 'Russia', 'continent': 'EU/AS', 'cq_zone': 16, 'itu_zone': 29, 'entity': 15},

    # Japan
    'JA': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JE': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JF': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JG': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JH': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JI': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JJ': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JK': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JL': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JM': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JN': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JO': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JP': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JQ': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JR': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    'JS': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '7J': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '7K': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '7L': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '7M': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '7N': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '8J': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},
    '8N': {'country': 'Japan', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 45, 'entity': 339},

    # Australia
    'VK': {'country': 'Australia', 'continent': 'OC', 'cq_zone': 30, 'itu_zone': 59, 'entity': 150},

    # New Zealand
    'ZL': {'country': 'New Zealand', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 170},
    'ZM': {'country': 'New Zealand', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 170},

    # Brazil
    'PY': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'PP': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'PT': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'ZV': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'ZW': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'ZX': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'ZY': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},
    'ZZ': {'country': 'Brazil', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 15, 'entity': 108},

    # Argentina
    'LU': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'AY': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'AZ': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L2': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L3': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L4': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L5': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L6': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L7': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L8': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},
    'L9': {'country': 'Argentina', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 100},

    # South Africa
    'ZS': {'country': 'South Africa', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 462},
    'ZR': {'country': 'South Africa', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 462},
    'ZT': {'country': 'South Africa', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 462},
    'ZU': {'country': 'South Africa', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 462},
}


def lookup_dxcc(callsign):
    """
    Lookup DXCC information from callsign

    Args:
        callsign: Amateur radio callsign (string)

    Returns:
        dict with keys: country, continent, cq_zone, itu_zone, entity
        or None if not found
    """
    if not callsign:
        return None

    # Clean up callsign - remove /P, /M, /MM, etc.
    call = callsign.upper().strip()
    call = call.split('/')[0]  # Take first part before any slash

    # Try matching from longest to shortest prefix
    for length in range(min(len(call), 4), 0, -1):
        prefix = call[:length]
        if prefix in DXCC_DATA:
            return DXCC_DATA[prefix].copy()

    # Try single character (for K, W, N, A, etc.)
    if len(call) > 0 and call[0] in DXCC_DATA:
        return DXCC_DATA[call[0]].copy()

    return None


def get_country_from_callsign(callsign):
    """Get just the country name from callsign"""
    info = lookup_dxcc(callsign)
    return info['country'] if info else None


def get_continent_from_callsign(callsign):
    """Get continent abbreviation from callsign"""
    info = lookup_dxcc(callsign)
    return info['continent'] if info else None


def get_zones_from_callsign(callsign):
    """Get CQ and ITU zones from callsign"""
    info = lookup_dxcc(callsign)
    if info:
        return info['cq_zone'], info['itu_zone']
    return None, None
