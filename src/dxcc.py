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

    # More Europe
    'OH': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OF': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OG': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OI': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'SM': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SA': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    '7S': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'LA': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LB': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LC': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LD': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LG': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LI': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LJ': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LN': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'OZ': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OX': {'country': 'Greenland', 'continent': 'NA', 'cq_zone': 40, 'itu_zone': 5, 'entity': 237},
    'OY': {'country': 'Faroe Islands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 222},
    'PA': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PB': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PC': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PD': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PE': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PH': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PI': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'ON': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OO': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OP': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OQ': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OR': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OS': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OT': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'HB': {'country': 'Switzerland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 287},
    'HB0': {'country': 'Liechtenstein', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 251},
    'OE': {'country': 'Austria', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 206},
    'CT': {'country': 'Portugal', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 272},
    'CU': {'country': 'Azores', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 36, 'entity': 149},
    'HA': {'country': 'Hungary', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 239},
    'HG': {'country': 'Hungary', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 239},
    'LY': {'country': 'Lithuania', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 146},
    'LZ': {'country': 'Bulgaria', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 212},
    'OK': {'country': 'Czech Republic', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 503},
    'OL': {'country': 'Czech Republic', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 503},
    'OM': {'country': 'Slovakia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 504},
    'SP': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SN': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SO': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SQ': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SR': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SV': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SW': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SX': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SY': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SZ': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'YO': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},
    'YR': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},
    'YU': {'country': 'Serbia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 296},
    'YT': {'country': 'Serbia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 296},
    'YZ': {'country': 'Serbia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 296},
    'Z3': {'country': 'North Macedonia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 502},
    '9A': {'country': 'Croatia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 497},
    'S5': {'country': 'Slovenia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 499},
    'GW': {'country': 'Wales', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 294},
    'GM': {'country': 'Scotland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 279},
    'GI': {'country': 'Northern Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 265},
    'GD': {'country': 'Isle of Man', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 246},
    'GJ': {'country': 'Jersey', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 285},
    'GU': {'country': 'Guernsey', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 285},
    'EI': {'country': 'Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 245},
    'UR': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UU': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UW': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UX': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'EM': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'EN': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'EO': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'YL': {'country': 'Latvia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 145},
    'ES': {'country': 'Estonia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 52},

    # More Asia
    'VU': {'country': 'India', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 324},
    'BY': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BA': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BD': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BG': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BH': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BI': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'BJ': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'HL': {'country': 'South Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'DS': {'country': 'South Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'DU': {'country': 'Philippines', 'continent': 'AS', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},
    '4D': {'country': 'Philippines', 'continent': 'AS', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},
    '4E': {'country': 'Philippines', 'continent': 'AS', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},
    '4F': {'country': 'Philippines', 'continent': 'AS', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},
    '4I': {'country': 'Philippines', 'continent': 'AS', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},
    'HS': {'country': 'Thailand', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 387},
    'E2': {'country': 'Thailand', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 387},
    'YB': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YC': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YD': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YE': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YF': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YG': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YH': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    '9M': {'country': 'Malaysia', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 328},
    '9V': {'country': 'Singapore', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 381},
    'S2': {'country': 'Singapore', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 381},
    'XV': {'country': 'Vietnam', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 293},
    '3W': {'country': 'Vietnam', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 293},

    # More Caribbean/Central America (North America)
    'HI': {'country': 'Dominican Republic', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 72},
    'HH': {'country': 'Haiti', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 78},
    '6Y': {'country': 'Jamaica', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 82},
    'CO': {'country': 'Cuba', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 70},
    'CM': {'country': 'Cuba', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 70},
    'TI': {'country': 'Costa Rica', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 308},
    'HP': {'country': 'Panama', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 88},
    'HK': {'country': 'Colombia', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 116},
    'YV': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    'YW': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    'YX': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    'YY': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    '4V': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},

    # More Africa
    'CN': {'country': 'Morocco', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 446},
    '5V': {'country': 'Togo', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 483},
    '5U': {'country': 'Niger', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 436},
    '5T': {'country': 'Mauritania', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 444},
    'ET': {'country': 'Ethiopia', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 197},
    '7Q': {'country': 'Malawi', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 362},
    '5Z': {'country': 'Kenya', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 430},
    '5H': {'country': 'Tanzania', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 470},
    '5X': {'country': 'Uganda', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 167},
    '7P': {'country': 'Lesotho', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 432},
    'A2': {'country': 'Botswana', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 402},

    # More Oceania
    'P2': {'country': 'Papua New Guinea', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 163},
    'T3': {'country': 'Kiribati', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 62, 'entity': 296},
    'FO': {'country': 'French Polynesia', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 63, 'entity': 175},
    'ZK': {'country': 'New Zealand', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 170},
    'KH0': {'country': 'Mariana Islands', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 64, 'entity': 166},
    'KH2': {'country': 'Guam', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 64, 'entity': 103},
    'KH6': {'country': 'Hawaii', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 61, 'entity': 110},
    'KH8': {'country': 'American Samoa', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 101},
    'T8': {'country': 'Palau', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 64, 'entity': 22},
    'V7': {'country': 'Marshall Islands', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 65, 'entity': 168},
    'V6': {'country': 'Micronesia', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 64, 'entity': 173},
    'T2': {'country': 'Tuvalu', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 65, 'entity': 282},
    '3D2': {'country': 'Fiji', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 176},
    'YJ': {'country': 'Vanuatu', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 158},
    'FK': {'country': 'New Caledonia', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 162},
    'E5': {'country': 'Cook Islands', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 234},
    'ZL7': {'country': 'Chatham Islands', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 171},
    'ZL8': {'country': 'Kermadec Islands', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 122},
    'ZL9': {'country': 'Auckland & Campbell Islands', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 60, 'entity': 11},
    'H4': {'country': 'Solomon Islands', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 185},
    'T30': {'country': 'West Kiribati', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 65, 'entity': 301},
    'T31': {'country': 'Central Kiribati', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 62, 'entity': 489},
    'T32': {'country': 'East Kiribati', 'continent': 'OC', 'cq_zone': 31, 'itu_zone': 61, 'entity': 488},
    'T5': {'country': 'Somalia', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 232},
    'A3': {'country': 'Tonga', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 160},
    '5W': {'country': 'Samoa', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 190},

    # More South America
    'CE': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'XQ': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'XR': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'OA': {'country': 'Peru', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 136},
    '4T': {'country': 'Peru', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 136},
    'CP': {'country': 'Bolivia', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 104},
    'HC': {'country': 'Ecuador', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 120},
    'HD': {'country': 'Ecuador', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 120},
    'CX': {'country': 'Uruguay', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 144},
    '8R': {'country': 'Guyana', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 129},
    'PZ': {'country': 'Suriname', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 140},
    'FY': {'country': 'French Guiana', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 130},
    'ZP': {'country': 'Paraguay', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 14, 'entity': 132},

    # More Central America/Caribbean (North America continent)
    'TG': {'country': 'Guatemala', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 76},
    'TD': {'country': 'Guatemala', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 76},
    'YN': {'country': 'Nicaragua', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 86},
    'YS': {'country': 'El Salvador', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 74},
    'HU': {'country': 'El Salvador', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 74},
    'HR': {'country': 'Honduras', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 80},
    'HQ': {'country': 'Honduras', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 80},
    'V3': {'country': 'Belize', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 66},
    'KP2': {'country': 'US Virgin Islands', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 105},
    'KP4': {'country': 'Puerto Rico', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 202},
    'KP5': {'country': 'Desecheo Island', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 43},
    'J7': {'country': 'Dominica', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 95},
    'J6': {'country': 'St. Lucia', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 97},
    'J8': {'country': 'St. Vincent', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 98},
    'J3': {'country': 'Grenada', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 77},
    'VP2E': {'country': 'Anguilla', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 22},
    'VP2M': {'country': 'Montserrat', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 84},
    'VP2V': {'country': 'British Virgin Islands', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 106},
    'VP5': {'country': 'Turks & Caicos Islands', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 90},
    'VP9': {'country': 'Bermuda', 'continent': 'NA', 'cq_zone': 5, 'itu_zone': 11, 'entity': 64},
    'V4': {'country': 'St. Kitts & Nevis', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 249},
    'V2': {'country': 'Antigua & Barbuda', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 24},
    '8P': {'country': 'Barbados', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 62},
    'FG': {'country': 'Guadeloupe', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 79},
    'FM': {'country': 'Martinique', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 84},
    'PJ2': {'country': 'Curacao', 'continent': 'NA', 'cq_zone': 9, 'itu_zone': 11, 'entity': 520},
    'PJ4': {'country': 'Bonaire', 'continent': 'NA', 'cq_zone': 9, 'itu_zone': 11, 'entity': 519},
    'PJ5': {'country': 'Saba & St. Eustatius', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 521},
    'PJ7': {'country': 'Sint Maarten', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 518},
    'FJ': {'country': 'St. Martin', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 213},
    '9Y': {'country': 'Trinidad & Tobago', 'continent': 'NA', 'cq_zone': 9, 'itu_zone': 11, 'entity': 90},
    'KL': {'country': 'Alaska', 'continent': 'NA', 'cq_zone': 1, 'itu_zone': 1, 'entity': 6},
    'AL': {'country': 'Alaska', 'continent': 'NA', 'cq_zone': 1, 'itu_zone': 1, 'entity': 6},
    'NL': {'country': 'Alaska', 'continent': 'NA', 'cq_zone': 1, 'itu_zone': 1, 'entity': 6},
    'WL': {'country': 'Alaska', 'continent': 'NA', 'cq_zone': 1, 'itu_zone': 1, 'entity': 6},

    # More Asia
    'AP': {'country': 'Pakistan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 41, 'entity': 370},
    '4K': {'country': 'Azerbaijan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 18},
    'EK': {'country': 'Armenia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 14},
    'EX': {'country': 'Kyrgyzstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},
    'EY': {'country': 'Tajikistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 262},
    'EZ': {'country': 'Turkmenistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 280},
    'UK': {'country': 'Uzbekistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 292},
    'UN': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'UO': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'UP': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'UQ': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'UH': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'UI': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 130},
    'A4': {'country': 'Oman', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 370},
    'A6': {'country': 'United Arab Emirates', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 391},
    'A7': {'country': 'Qatar', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 376},
    'A9': {'country': 'Bahrain', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 304},
    '9K': {'country': 'Kuwait', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 348},
    'HZ': {'country': 'Saudi Arabia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 378},
    '7Z': {'country': 'Saudi Arabia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 378},
    '8Z': {'country': 'Saudi Arabia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 378},
    'YI': {'country': 'Iraq', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 333},
    'YK': {'country': 'Syria', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 384},
    'OD': {'country': 'Lebanon', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 354},
    '4X': {'country': 'Israel', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 336},
    '4Z': {'country': 'Israel', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 336},
    'JY': {'country': 'Jordan', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 342},
    'BV': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    '9M2': {'country': 'West Malaysia', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 328},
    '9M6': {'country': 'East Malaysia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 54, 'entity': 473},
    'XU': {'country': 'Cambodia', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 312},
    'XZ': {'country': 'Myanmar', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 309},
    '1S': {'country': 'Spratly Islands', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 50, 'entity': 247},
    'BX': {'country': 'Bangladesh', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 305},
    'S2': {'country': 'Bangladesh', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 305},
    '4S': {'country': 'Sri Lanka', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 315},
    '9N': {'country': 'Nepal', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 42, 'entity': 369},
    'A5': {'country': 'Bhutan', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 306},
    'P5': {'country': 'North Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 344},
    'BZ': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 318},
    'P9': {'country': 'North Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 344},

    # More Middle East
    'EP': {'country': 'Iran', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 40, 'entity': 330},
    'EQ': {'country': 'Iran', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 40, 'entity': 330},
    'TA': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    'TB': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    'TC': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    '5B': {'country': 'Cyprus', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 215},
    'H2': {'country': 'Cyprus', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 215},
    'C4': {'country': 'Cyprus', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 215},
    'P3': {'country': 'Cyprus', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 215},
    'ZC4': {'country': 'UK Sovereign Base Areas Cyprus', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 283},
    '4J': {'country': 'Azerbaijan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 18},
    '4L': {'country': 'Georgia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 75},

    # More Africa - MAJOR EXPANSION
    '5N': {'country': 'Nigeria', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 450},
    '9G': {'country': 'Ghana', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 424},
    '9L': {'country': 'Sierra Leone', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 458},
    '9Q': {'country': 'Dem. Rep. of the Congo', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 414},
    '9U': {'country': 'Burundi', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 404},
    '9X': {'country': 'Rwanda', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 454},
    'C5': {'country': 'The Gambia', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 422},
    'C9': {'country': 'Mozambique', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 181},
    'CR': {'country': 'Mozambique', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 181},
    'D2': {'country': 'Angola', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 401},
    'D4': {'country': 'Cape Verde', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 409},
    'D6': {'country': 'Comoros', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 411},
    'E3': {'country': 'Eritrea', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 317},
    'EA8': {'country': 'Canary Islands', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 36, 'entity': 29},
    'EA9': {'country': 'Ceuta & Melilla', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 32},
    'EL': {'country': 'Liberia', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 434},
    'ER': {'country': 'Moldova', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 179},
    'SU': {'country': 'Egypt', 'continent': 'AF', 'cq_zone': 34, 'itu_zone': 38, 'entity': 478},
    '6W': {'country': 'Senegal', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 456},
    'J5': {'country': 'Guinea-Bissau', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 192},
    'ST': {'country': 'Sudan', 'continent': 'AF', 'cq_zone': 34, 'itu_zone': 48, 'entity': 466},
    'TU': {'country': 'Cote d\'Ivoire', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 428},
    'TY': {'country': 'Benin', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 416},
    'TZ': {'country': 'Mali', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 442},
    'XT': {'country': 'Burkina Faso', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 480},
    'ZD7': {'country': 'St. Helena', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 66, 'entity': 250},
    'ZD8': {'country': 'Ascension Island', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 66, 'entity': 205},
    'ZD9': {'country': 'Tristan da Cunha', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 66, 'entity': 274},
    'TT': {'country': 'Chad', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 47, 'entity': 410},
    'TL': {'country': 'Central African Republic', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 47, 'entity': 406},
    'TR': {'country': 'Gabon', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 420},
    'TN': {'country': 'Congo', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 412},
    'J2': {'country': 'Djibouti', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 408},
    '5R': {'country': 'Madagascar', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 438},
    '6O': {'country': 'Somalia', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 232},
    'S7': {'country': 'Seychelles', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 379},
    'S9': {'country': 'Sao Tome & Principe', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 47, 'entity': 219},
    '7O': {'country': 'Yemen', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 492},
    '3C': {'country': 'Equatorial Guinea', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 47, 'entity': 418},
    '3V': {'country': 'Tunisia', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 474},
    '3X': {'country': 'Guinea', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 420},
    '7X': {'country': 'Algeria', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 400},
    '5A': {'country': 'Libya', 'continent': 'AF', 'cq_zone': 34, 'itu_zone': 38, 'entity': 436},
    'A2': {'country': 'Botswana', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 402},
    'V5': {'country': 'Namibia', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 464},
    'Z2': {'country': 'Zimbabwe', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 53, 'entity': 452},
    '7Q': {'country': 'Malawi', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 362},
    '5L': {'country': 'Liberia', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 434},
    'A2': {'country': 'Botswana', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 402},
    '3B8': {'country': 'Mauritius', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 165},
    '3B9': {'country': 'Rodriguez Island', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 460},
    'FR': {'country': 'Reunion Island', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 53, 'entity': 453},
    'FT5W': {'country': 'Crozet Island', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 68, 'entity': 41},
    'FT5X': {'country': 'Kerguelen Islands', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 68, 'entity': 131},
    'FT5Z': {'country': 'Amsterdam & St. Paul Islands', 'continent': 'AF', 'cq_zone': 39, 'itu_zone': 68, 'entity': 10},
    'D4': {'country': 'Cape Verde', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 409},

    # More Europe - Complete remaining countries
    'TF': {'country': 'Iceland', 'continent': 'EU', 'cq_zone': 40, 'itu_zone': 17, 'entity': 242},
    'TK': {'country': 'Corsica', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 214},
    '9H': {'country': 'Malta', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 257},
    'IT': {'country': 'Italy', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 248},
    'IG': {'country': 'Italy', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 248},
    'E4': {'country': 'Palestine', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 510},
    'LX': {'country': 'Luxembourg', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 254},
    'S5': {'country': 'Slovenia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 499},
    'T7': {'country': 'San Marino', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 278},
    'T9': {'country': 'Bosnia-Herzegovina', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 501},
    'E7': {'country': 'Bosnia-Herzegovina', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 501},
    '4O': {'country': 'Montenegro', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 514},
    'ZA': {'country': 'Albania', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 3},
    '9A': {'country': 'Croatia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 497},
    'HV': {'country': 'Vatican City', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 295},
    '1A': {'country': 'S.M.O.M.', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 226},
    'ZB': {'country': 'Gibraltar', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 233},
    'Z6': {'country': 'Kosovo', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 522},
    'JW': {'country': 'Svalbard', 'continent': 'EU', 'cq_zone': 40, 'itu_zone': 18, 'entity': 259},
    'JX': {'country': 'Jan Mayen', 'continent': 'EU', 'cq_zone': 40, 'itu_zone': 18, 'entity': 118},
    'EA6': {'country': 'Balearic Islands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 21},
    'IS': {'country': 'Sardinia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 225},
    'IM': {'country': 'Sicily', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 248},
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
