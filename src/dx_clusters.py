"""
DX Cluster definitions and management
Data sourced from https://www.ng3k.com/Misc/cluster.html
"""

DX_CLUSTERS = [
    # USA RBN/Skimmer Clusters (Reverse Beacon Network)
    {
        "callsign": "AE5E",
        "name": "AE5E - Thief River Falls, MN (RBN)",
        "hostname": "dxspots.com",
        "port": 7300,
        "location": "Thief River Falls, MN",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "K1AX-11",
        "name": "K1AX-11 - N. Virginia (RBN)",
        "hostname": "dxdata.io",
        "port": 7300,
        "location": "N. Virginia",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "AI9T",
        "name": "AI9T - Marshall, IL (RBN)",
        "hostname": "dxc.ai9t.com",
        "port": 7300,
        "location": "Marshall, IL",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "K7TJ-1",
        "name": "K7TJ-1 - Spokane, WA (RBN)",
        "hostname": "k7tj.ewarg.org",
        "port": 7300,
        "location": "Spokane, WA",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "AI6W-1",
        "name": "AI6W-1 - Newcastle, CA (RBN)",
        "hostname": "ai6w.net",
        "port": 7300,
        "location": "Newcastle, CA",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "KB8PMY-3",
        "name": "KB8PMY-3 - Hamilton, OH (RBN)",
        "hostname": "kb8pmy.net",
        "port": 7300,
        "location": "Hamilton, OH",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "K9LC",
        "name": "K9LC - Rockford, IL (RBN)",
        "hostname": "k9lc.ddns.net",
        "port": 7300,
        "location": "Rockford, IL",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "AE3N-2",
        "name": "AE3N-2 - Virginia (RBN)",
        "hostname": "dxc.ae3n.us",
        "port": 7300,
        "location": "Virginia",
        "type": "DX Spider (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "K4GSO-2",
        "name": "K4GSO-2 - Ocala, FL (RBN)",
        "hostname": "dxc.k4gso.com",
        "port": 7373,
        "location": "Ocala, FL",
        "type": "AR-Cluster (+RBN)",
        "region": "North America"
    },
    {
        "callsign": "K2CAN",
        "name": "K2CAN - Oswego, NY (RBN)",
        "hostname": "k2can.us",
        "port": 7373,
        "location": "Oswego, NY",
        "type": "AR-Cluster (+RBN)",
        "region": "North America"
    },
    # Original clusters (kept for compatibility)
    {
        "callsign": "NC7J",
        "name": "NC7J - Syracuse, UT",
        "hostname": "dxc.nc7j.com",
        "port": 7373,
        "location": "Syracuse, UT",
        "type": "CW RTTY Skimmer",
        "region": "North America"
    },
    {
        "callsign": "W1NR",
        "name": "W1NR - Marlborough, MA",
        "hostname": "dx.w1nr.net",
        "port": 7300,
        "location": "Marlborough, MA",
        "type": "DXSpider",
        "region": "North America"
    },
    {
        "callsign": "W1NR-9",
        "name": "W1NR-9 - US DX (zones 1-8)",
        "hostname": "usdx.w1nr.net",
        "port": 7300,
        "location": "Marlborough, MA",
        "type": "DXSpider",
        "region": "North America"
    },
    {
        "callsign": "K1TTT",
        "name": "K1TTT - Peru, MA",
        "hostname": "k1ttt.net",
        "port": 7373,
        "location": "Peru, MA",
        "type": "AR-Cluster",
        "region": "North America"
    },
    {
        "callsign": "W3LPL",
        "name": "W3LPL - Glenwood, MD",
        "hostname": "w3lpl.net",
        "port": 7373,
        "location": "Glenwood, MD",
        "type": "AR-Cluster v.6",
        "region": "North America"
    },
    {
        "callsign": "W6RFU",
        "name": "W6RFU - Santa Barbara, CA",
        "hostname": "ucsbdx.ece.ucsb.edu",
        "port": 7300,
        "location": "Santa Barbara, CA",
        "type": "DX Spider",
        "region": "North America"
    },
    # International RBN clusters
    {
        "callsign": "G6NHU-2",
        "name": "G6NHU-2 - Essex, UK",
        "hostname": "dxspider.co.uk",
        "port": 7300,
        "location": "Essex, UK",
        "type": "DX Spider (RBN feed)",
        "region": "Europe"
    },
    {
        "callsign": "DL8LAS",
        "name": "DL8LAS - Kiel, Germany",
        "hostname": "dl8las.dyndns.org",
        "port": 7300,
        "location": "Kiel, Germany",
        "type": "Skimmer Server",
        "region": "Europe"
    },
    {
        "callsign": "S50CLX",
        "name": "S50CLX - Slovenia",
        "hostname": "s50clx.infrax.si",
        "port": 41112,
        "location": "Slovenia",
        "type": "Multi-mode Skimmer",
        "region": "Europe"
    },
    {
        "callsign": "ZL2ARN-10",
        "name": "ZL2ARN-10 - New Zealand",
        "hostname": "zl2arn.ddns.net",
        "port": 7300,
        "location": "New Zealand",
        "type": "DXSpider",
        "region": "Oceania"
    }
]


def get_clusters_by_region(region=None):
    """Get DX clusters filtered by region"""
    if region is None:
        return DX_CLUSTERS
    return [c for c in DX_CLUSTERS if c["region"] == region]


def get_cluster_by_callsign(callsign):
    """Get a specific cluster by callsign"""
    for cluster in DX_CLUSTERS:
        if cluster["callsign"] == callsign:
            return cluster
    return None


def get_all_regions():
    """Get unique list of all regions"""
    return sorted(list(set(c["region"] for c in DX_CLUSTERS)))
