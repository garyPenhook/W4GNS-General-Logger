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

    # Israel
    '4X': {'country': 'Israel', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 336},
    '4Z': {'country': 'Israel', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 336},

    # China
    'B': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 43, 'entity': 318},
    'BY': {'country': 'China', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 43, 'entity': 318},

    # India
    'VU': {'country': 'India', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 324},

    # Thailand
    'HS': {'country': 'Thailand', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 387},

    # Philippines
    'DU': {'country': 'Philippines', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 50, 'entity': 375},

    # Indonesia
    'YB': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},
    'YC': {'country': 'Indonesia', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 327},

    # Egypt
    'SU': {'country': 'Egypt', 'continent': 'AF', 'cq_zone': 34, 'itu_zone': 39, 'entity': 478},

    # Kenya
    '5Z': {'country': 'Kenya', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 430},

    # Nigeria
    '5N': {'country': 'Nigeria', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 450},

    # Poland
    'SP': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    'SQ': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},
    '3Z': {'country': 'Poland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 269},

    # Czech Republic
    'OK': {'country': 'Czech Republic', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 503},
    'OL': {'country': 'Czech Republic', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 503},

    # Ukraine
    'UR': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UT': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UU': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},
    'UX': {'country': 'Ukraine', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 288},

    # Netherlands
    'PA': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PB': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PC': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PD': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PE': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PF': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PG': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PH': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},
    'PI': {'country': 'Netherlands', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 263},

    # Belgium
    'ON': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OO': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OP': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OQ': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OR': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OS': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},
    'OT': {'country': 'Belgium', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 209},

    # Sweden
    'SA': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SB': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SC': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SD': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SE': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SF': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SG': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SH': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SI': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SJ': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SK': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SL': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    'SM': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},
    '7S': {'country': 'Sweden', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 284},

    # Switzerland
    'HB': {'country': 'Switzerland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 287},
    'HE': {'country': 'Switzerland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 28, 'entity': 287},

    # Austria
    'OE': {'country': 'Austria', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 206},

    # Portugal
    'CR': {'country': 'Portugal', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 272},
    'CT': {'country': 'Portugal', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 37, 'entity': 272},

    # Greece
    'SV': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SW': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},
    'SX': {'country': 'Greece', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 236},

    # Norway
    'LA': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LB': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LC': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LD': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LE': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LF': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LG': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LH': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LI': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LJ': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},
    'LN': {'country': 'Norway', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 266},

    # Denmark
    'OU': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OV': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OW': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OX': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OY': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    'OZ': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    '5P': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},
    '5Q': {'country': 'Denmark', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 18, 'entity': 221},

    # Finland
    'OF': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OG': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OH': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OI': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},
    'OJ': {'country': 'Finland', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 18, 'entity': 224},

    # Turkey
    'TA': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    'TB': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    'TC': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},
    'YM': {'country': 'Turkey', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 390},

    # Saudi Arabia
    '7Z': {'country': 'Saudi Arabia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 378},
    'HZ': {'country': 'Saudi Arabia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 378},

    # Korea (South)
    'HL': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'HM': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'D7': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'D8': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'D9': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'DS': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},
    'DT': {'country': 'Rep. of Korea', 'continent': 'AS', 'cq_zone': 25, 'itu_zone': 44, 'entity': 137},

    # Taiwan
    'BM': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BN': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BO': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BP': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BQ': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BU': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BV': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BW': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},
    'BX': {'country': 'Taiwan', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 386},

    # Singapore
    '9V': {'country': 'Singapore', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 381},

    # Malaysia
    '9M': {'country': 'Malaysia', 'continent': 'AS', 'cq_zone': 28, 'itu_zone': 54, 'entity': 343},

    # Hong Kong
    'VR2': {'country': 'Hong Kong', 'continent': 'AS', 'cq_zone': 24, 'itu_zone': 44, 'entity': 321},

    # Pakistan
    'AP': {'country': 'Pakistan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 41, 'entity': 370},

    # UAE
    'A6': {'country': 'United Arab Emirates', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 391},

    # Qatar
    'A7': {'country': 'Qatar', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 376},

    # Kuwait
    '9K': {'country': 'Kuwait', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 348},

    # Jordan
    'JY': {'country': 'Jordan', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 342},

    # Lebanon
    'OD': {'country': 'Lebanon', 'continent': 'AS', 'cq_zone': 20, 'itu_zone': 39, 'entity': 354},

    # Iraq
    'YI': {'country': 'Iraq', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 39, 'entity': 333},

    # Bangladesh
    'S2': {'country': 'Bangladesh', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 305},

    # Nepal
    '9N': {'country': 'Nepal', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 42, 'entity': 369},

    # Sri Lanka
    '4S': {'country': 'Sri Lanka', 'continent': 'AS', 'cq_zone': 22, 'itu_zone': 41, 'entity': 315},

    # Vietnam
    '3W': {'country': 'Vietnam', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 293},
    'XV': {'country': 'Vietnam', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 293},

    # Laos
    'XW': {'country': 'Laos', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 143},

    # Cambodia
    'XU': {'country': 'Cambodia', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 312},

    # Myanmar (Burma)
    'XZ': {'country': 'Myanmar', 'continent': 'AS', 'cq_zone': 26, 'itu_zone': 49, 'entity': 309},

    # Mongolia
    'JT': {'country': 'Mongolia', 'continent': 'AS', 'cq_zone': 23, 'itu_zone': 33, 'entity': 363},
    'JU': {'country': 'Mongolia', 'continent': 'AS', 'cq_zone': 23, 'itu_zone': 33, 'entity': 363},
    'JV': {'country': 'Mongolia', 'continent': 'AS', 'cq_zone': 23, 'itu_zone': 33, 'entity': 363},

    # Kazakhstan
    'UN': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},
    'UO': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},
    'UP': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},
    'UQ': {'country': 'Kazakhstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},

    # Uzbekistan
    'UK': {'country': 'Uzbekistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 196},
    'UJ': {'country': 'Uzbekistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 196},
    'UH': {'country': 'Uzbekistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 196},
    'UI': {'country': 'Uzbekistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 196},

    # Kyrgyzstan
    'EX': {'country': 'Kyrgyzstan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 135},

    # Tajikistan
    'EY': {'country': 'Tajikistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 262},

    # Turkmenistan
    'EZ': {'country': 'Turkmenistan', 'continent': 'AS', 'cq_zone': 17, 'itu_zone': 30, 'entity': 279},

    # Armenia
    'EK': {'country': 'Armenia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 14},

    # Georgia
    '4L': {'country': 'Georgia', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 75},

    # Azerbaijan
    '4J': {'country': 'Azerbaijan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 18},
    '4K': {'country': 'Azerbaijan', 'continent': 'AS', 'cq_zone': 21, 'itu_zone': 29, 'entity': 18},

    # === EUROPE - Additional Countries ===

    # Ireland
    'EI': {'country': 'Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 245},
    'EJ': {'country': 'Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 245},

    # Scotland
    'GM': {'country': 'Scotland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 279},
    'MM': {'country': 'Scotland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 279},

    # Northern Ireland
    'GI': {'country': 'Northern Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 265},
    'MI': {'country': 'Northern Ireland', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 265},

    # Wales
    'GW': {'country': 'Wales', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 294},
    'MW': {'country': 'Wales', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 294},

    # Iceland
    'TF': {'country': 'Iceland', 'continent': 'EU', 'cq_zone': 40, 'itu_zone': 17, 'entity': 242},

    # Romania
    'YO': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},
    'YP': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},
    'YQ': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},
    'YR': {'country': 'Romania', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 275},

    # Bulgaria
    'LZ': {'country': 'Bulgaria', 'continent': 'EU', 'cq_zone': 20, 'itu_zone': 28, 'entity': 212},

    # Serbia
    'YU': {'country': 'Serbia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 296},
    'YT': {'country': 'Serbia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 296},

    # Croatia
    '9A': {'country': 'Croatia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 497},

    # Slovenia
    'S5': {'country': 'Slovenia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 499},

    # Hungary
    'HA': {'country': 'Hungary', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 239},
    'HG': {'country': 'Hungary', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 239},

    # Slovakia
    'OM': {'country': 'Slovakia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 504},

    # Lithuania
    'LY': {'country': 'Lithuania', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 146},

    # Latvia
    'YL': {'country': 'Latvia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 145},

    # Estonia
    'ES': {'country': 'Estonia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 29, 'entity': 52},

    # Belarus
    'EU': {'country': 'Belarus', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 27},
    'EV': {'country': 'Belarus', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 27},
    'EW': {'country': 'Belarus', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 27},

    # Moldova
    'ER': {'country': 'Moldova', 'continent': 'EU', 'cq_zone': 16, 'itu_zone': 29, 'entity': 179},

    # Albania
    'ZA': {'country': 'Albania', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 201},

    # North Macedonia
    'Z3': {'country': 'North Macedonia', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 502},

    # Bosnia-Herzegovina
    'E7': {'country': 'Bosnia-Herzegovina', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 501},

    # Montenegro
    '4O': {'country': 'Montenegro', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 514},

    # Kosovo
    'Z6': {'country': 'Kosovo', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 522},

    # Malta
    '9H': {'country': 'Malta', 'continent': 'EU', 'cq_zone': 15, 'itu_zone': 28, 'entity': 257},

    # Luxembourg
    'LX': {'country': 'Luxembourg', 'continent': 'EU', 'cq_zone': 14, 'itu_zone': 27, 'entity': 254},

    # === AFRICA - Complete Coverage ===

    # Morocco
    'CN': {'country': 'Morocco', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 446},
    '5C': {'country': 'Morocco', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 446},

    # Algeria
    '7X': {'country': 'Algeria', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 400},

    # Tunisia
    '3V': {'country': 'Tunisia', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 474},
    'TS': {'country': 'Tunisia', 'continent': 'AF', 'cq_zone': 33, 'itu_zone': 37, 'entity': 474},

    # Libya
    '5A': {'country': 'Libya', 'continent': 'AF', 'cq_zone': 34, 'itu_zone': 38, 'entity': 436},

    # Zimbabwe
    'Z2': {'country': 'Zimbabwe', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 53, 'entity': 452},

    # Botswana
    'A2': {'country': 'Botswana', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 402},

    # Tanzania
    '5H': {'country': 'Tanzania', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 470},

    # Ethiopia
    'ET': {'country': 'Ethiopia', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 425},

    # Namibia
    'V5': {'country': 'Namibia', 'continent': 'AF', 'cq_zone': 38, 'itu_zone': 57, 'entity': 464},

    # Ghana
    '9G': {'country': 'Ghana', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 424},

    # Senegal
    '6W': {'country': 'Senegal', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 456},
    '6V': {'country': 'Senegal', 'continent': 'AF', 'cq_zone': 35, 'itu_zone': 46, 'entity': 456},

    # Mozambique
    'C9': {'country': 'Mozambique', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 53, 'entity': 181},

    # Zambia
    '9J': {'country': 'Zambia', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 53, 'entity': 482},

    # Uganda
    '5X': {'country': 'Uganda', 'continent': 'AF', 'cq_zone': 37, 'itu_zone': 48, 'entity': 286},

    # Rwanda
    '9X': {'country': 'Rwanda', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 454},

    # Burundi
    '9U': {'country': 'Burundi', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 404},

    # Angola
    'D2': {'country': 'Angola', 'continent': 'AF', 'cq_zone': 36, 'itu_zone': 52, 'entity': 401},

    # === SOUTH AMERICA - Complete Coverage ===

    # Chile
    'CE': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'CA': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'CB': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'CC': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},
    'CD': {'country': 'Chile', 'continent': 'SA', 'cq_zone': 12, 'itu_zone': 14, 'entity': 112},

    # Peru
    'OA': {'country': 'Peru', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 136},
    'OB': {'country': 'Peru', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 136},
    'OC': {'country': 'Peru', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 136},

    # Colombia
    'HJ': {'country': 'Colombia', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 116},
    'HK': {'country': 'Colombia', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 116},

    # Venezuela
    'YV': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    'YW': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    'YY': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},
    '4M': {'country': 'Venezuela', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 148},

    # Ecuador
    'HC': {'country': 'Ecuador', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 120},
    'HD': {'country': 'Ecuador', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 120},

    # Bolivia
    'CP': {'country': 'Bolivia', 'continent': 'SA', 'cq_zone': 10, 'itu_zone': 12, 'entity': 104},

    # Uruguay
    'CX': {'country': 'Uruguay', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 144},
    'CV': {'country': 'Uruguay', 'continent': 'SA', 'cq_zone': 13, 'itu_zone': 14, 'entity': 144},

    # Paraguay
    'ZP': {'country': 'Paraguay', 'continent': 'SA', 'cq_zone': 11, 'itu_zone': 14, 'entity': 132},

    # Guyana
    '8R': {'country': 'Guyana', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 124},

    # Suriname
    'PZ': {'country': 'Suriname', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 140},

    # French Guiana
    'FY': {'country': 'French Guiana', 'continent': 'SA', 'cq_zone': 9, 'itu_zone': 12, 'entity': 63},

    # === NORTH AMERICA - Caribbean & Central America ===

    # Cuba
    'CM': {'country': 'Cuba', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 70},
    'CO': {'country': 'Cuba', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 70},
    'T4': {'country': 'Cuba', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 70},

    # Jamaica
    '6Y': {'country': 'Jamaica', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 82},

    # Bahamas
    'C6': {'country': 'Bahamas', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 60},

    # Costa Rica
    'TI': {'country': 'Costa Rica', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 308},

    # Panama
    'HP': {'country': 'Panama', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 88},
    'H3': {'country': 'Panama', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 88},
    'HO': {'country': 'Panama', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 88},

    # Guatemala
    'TG': {'country': 'Guatemala', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 76},

    # Honduras
    'HR': {'country': 'Honduras', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 80},

    # El Salvador
    'YS': {'country': 'El Salvador', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 74},

    # Nicaragua
    'YN': {'country': 'Nicaragua', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 86},
    'H6': {'country': 'Nicaragua', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 86},
    'H7': {'country': 'Nicaragua', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 86},

    # Belize
    'V3': {'country': 'Belize', 'continent': 'NA', 'cq_zone': 7, 'itu_zone': 11, 'entity': 66},

    # Dominican Republic
    'HI': {'country': 'Dominican Republic', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 72},

    # Haiti
    'HH': {'country': 'Haiti', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 78},
    '4V': {'country': 'Haiti', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 78},

    # Puerto Rico
    'KP': {'country': 'Puerto Rico', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 202},

    # US Virgin Islands
    'KV': {'country': 'US Virgin Islands', 'continent': 'NA', 'cq_zone': 8, 'itu_zone': 11, 'entity': 285},

    # === OCEANIA - Pacific Islands ===

    # Papua New Guinea
    'P2': {'country': 'Papua New Guinea', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 163},

    # Fiji
    '3D2': {'country': 'Fiji', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 176},

    # Samoa
    '5W': {'country': 'Samoa', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 190},

    # Tonga
    'A3': {'country': 'Tonga', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 62, 'entity': 160},

    # Solomon Islands
    'H4': {'country': 'Solomon Islands', 'continent': 'OC', 'cq_zone': 28, 'itu_zone': 51, 'entity': 185},

    # Vanuatu
    'YJ': {'country': 'Vanuatu', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 158},

    # New Caledonia
    'FK': {'country': 'New Caledonia', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 56, 'entity': 162},

    # French Polynesia
    'FO': {'country': 'French Polynesia', 'continent': 'OC', 'cq_zone': 32, 'itu_zone': 63, 'entity': 175},

    # Guam
    'KH2': {'country': 'Guam', 'continent': 'OC', 'cq_zone': 27, 'itu_zone': 64, 'entity': 103},

    # === ANTARCTICA ===
    # Antarctica
    'CE9': {'country': 'Antarctica', 'continent': 'AN', 'cq_zone': 12, 'itu_zone': 69, 'entity': 13},
    'KC4': {'country': 'Antarctica', 'continent': 'AN', 'cq_zone': 38, 'itu_zone': 72, 'entity': 13},
    'R1F': {'country': 'Antarctica', 'continent': 'AN', 'cq_zone': 38, 'itu_zone': 69, 'entity': 13},
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
