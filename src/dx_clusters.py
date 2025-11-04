"""
DX Cluster definitions and management
Data sourced from https://www.ng3k.com/Misc/cluster.html
"""

DX_CLUSTERS = [
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
        "callsign": "DL8LAS",
        "name": "DL8LAS - Kiel, Germany",
        "hostname": "dl8las.dyndns.org",
        "port": 7300,
        "location": "Kiel, Germany",
        "type": "Skimmer Server",
        "region": "Europe"
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
