"""
Maidenhead Gridsquare Locator System utilities

Provides functions to convert gridsquares to coordinates and calculate
distances between gridsquares using the haversine formula.
"""

import math
from typing import Tuple, Optional


def gridsquare_to_latlon(gridsquare: str) -> Tuple[float, float]:
    """
    Convert a Maidenhead gridsquare to latitude and longitude (center of square)

    Supports 4, 6, and 8 character gridsquares (e.g., FN31, FN31pr, FN31pr79)

    Args:
        gridsquare: Maidenhead gridsquare string

    Returns:
        Tuple of (latitude, longitude) in decimal degrees

    Raises:
        ValueError: If gridsquare format is invalid
    """
    gridsquare = gridsquare.strip().upper()

    # Validate length - must be exactly 4, 6, or 8 characters
    if len(gridsquare) not in (4, 6, 8):
        raise ValueError(f"Gridsquare must be 4, 6, or 8 characters, got {len(gridsquare)}: {gridsquare}")

    # Field (first 2 characters, A-R only)
    # Maidenhead divides world into 18x18 fields (A-R), not A-Z
    if not (gridsquare[0].isalpha() and gridsquare[1].isalpha()):
        raise ValueError(f"Invalid field characters: {gridsquare[:2]}")
    if not ('A' <= gridsquare[0] <= 'R' and 'A' <= gridsquare[1] <= 'R'):
        raise ValueError(f"Field characters must be A-R, got: {gridsquare[:2]}")

    lon = (ord(gridsquare[0]) - ord('A')) * 20 - 180
    lat = (ord(gridsquare[1]) - ord('A')) * 10 - 90

    # Square (characters 3-4, 00-99)
    if not (gridsquare[2].isdigit() and gridsquare[3].isdigit()):
        raise ValueError(f"Invalid square characters: {gridsquare[2:4]}")

    lon += int(gridsquare[2]) * 2
    lat += int(gridsquare[3]) * 1

    # Subsquare (characters 5-6, A-X only) - optional
    # Each square is divided into 24x24 subsquares (A-X)
    if len(gridsquare) >= 6:
        if not (gridsquare[4].isalpha() and gridsquare[5].isalpha()):
            raise ValueError(f"Invalid subsquare characters: {gridsquare[4:6]}")
        if not ('A' <= gridsquare[4] <= 'X' and 'A' <= gridsquare[5] <= 'X'):
            raise ValueError(f"Subsquare characters must be A-X, got: {gridsquare[4:6]}")

        lon += (ord(gridsquare[4]) - ord('A')) * (2.0 / 24.0)
        lat += (ord(gridsquare[5]) - ord('A')) * (1.0 / 24.0)

    # Extended subsquare (characters 7-8, 00-99) - optional
    if len(gridsquare) >= 8:
        if not (gridsquare[6].isdigit() and gridsquare[7].isdigit()):
            raise ValueError(f"Invalid extended subsquare characters: {gridsquare[6:8]}")

        lon += int(gridsquare[6]) * (2.0 / 240.0)
        lat += int(gridsquare[7]) * (1.0 / 240.0)

    # Return center of the square
    # Add half the width/height of the final precision level
    if len(gridsquare) >= 8:
        lon += (2.0 / 240.0) / 2
        lat += (1.0 / 240.0) / 2
    elif len(gridsquare) >= 6:
        lon += (2.0 / 24.0) / 2
        lat += (1.0 / 24.0) / 2
    else:  # 4 characters
        lon += 1.0  # Center of 2-degree square
        lat += 0.5  # Center of 1-degree square

    return lat, lon


def haversine_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance between two points using haversine formula

    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees

    Returns:
        Distance in nautical miles
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Earth radius in nautical miles using WGS84 mean radius
    # WGS84 mean radius = 6371.0088 km, 1 NM = 1.852 km
    # Earth radius in NM = 6371.0088 / 1.852 ≈ 3440.0691 NM
    earth_radius_nm = 3440.0691

    return c * earth_radius_nm


def gridsquare_distance_nm(grid1: str, grid2: str) -> Optional[float]:
    """
    Calculate distance between two gridsquares in nautical miles

    Args:
        grid1: First gridsquare
        grid2: Second gridsquare

    Returns:
        Distance in nautical miles, or None if either gridsquare is invalid
    """
    try:
        lat1, lon1 = gridsquare_to_latlon(grid1)
        lat2, lon2 = gridsquare_to_latlon(grid2)
        return haversine_distance_nm(lat1, lon1, lat2, lon2)
    except (ValueError, IndexError):
        return None


def gridsquare_distance_miles(grid1: str, grid2: str) -> Optional[float]:
    """
    Calculate distance between two gridsquares in statute miles

    Args:
        grid1: First gridsquare
        grid2: Second gridsquare

    Returns:
        Distance in statute miles, or None if either gridsquare is invalid
    """
    distance_nm = gridsquare_distance_nm(grid1, grid2)
    if distance_nm is not None:
        # Convert nautical miles to statute miles (1 NM = 1.15078 miles)
        return distance_nm * 1.15078
    return None


if __name__ == '__main__':
    # Test cases
    print("Testing gridsquare distance calculations")
    print("=" * 60)

    # Test 1: Short distance (should be close to 0)
    grid1 = "FN31pr"
    grid2 = "FN31pr"
    dist = gridsquare_distance_miles(grid1, grid2)
    print(f"{grid1} to {grid2}: {dist:.1f} miles (should be ~0)")

    # Test 2: Medium distance
    grid1 = "FN31pr"
    grid2 = "FN42aa"
    dist = gridsquare_distance_miles(grid1, grid2)
    print(f"{grid1} to {grid2}: {dist:.1f} miles")

    # Test 3: Long distance (coast to coast)
    grid1 = "FN31pr"  # New York area
    grid2 = "CM87"    # Los Angeles area
    dist = gridsquare_distance_miles(grid1, grid2)
    print(f"{grid1} to {grid2}: {dist:.0f} miles (should be ~2400)")

    # Test 4: Coordinate conversion
    lat, lon = gridsquare_to_latlon("FN31pr")
    print(f"\nFN31pr center: {lat:.4f}°N, {lon:.4f}°W")
