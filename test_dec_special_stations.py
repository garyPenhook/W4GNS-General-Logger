#!/usr/bin/env python3
"""
Test script for December WES special station tracking
"""

# Simulate the contest tab's December special station logic
class MockContestTab:
    def __init__(self):
        # December WES Special Stations
        self.dec_reindeer_stations = {
            'AI5BE', 'WM4Q', 'W2EB', 'W0EJ', 'NX1K',
            'AB4PP', 'NQ8T', 'KA3BPN', 'W7AMI', 'W7VC'
        }
        self.dec_santa_station = 'K4KYN'
        self.dec_scrooge_station = 'W4CMG'
        self.dec_elf_stations = {
            'G0RDO', 'W0NZZ', 'KD2YMM', 'W9KMK', 'K2MZ',
            'NQ3K', 'W4LRB', 'KM4JEG', 'K4TNE', 'F6EJN'
        }

        self.contest_type = 'WES'
        self.monthly_theme = 'Dec - Reindeer'
        self.bonus_theme = 5
        self.dec_special_stations = set()
        self.monthly_theme_qsos = []

    def _calculate_theme_bonus(self, callsign, band, skcc):
        """Calculate WES monthly theme bonus if applicable"""
        if self.contest_type != 'WES' or self.monthly_theme == 'None':
            return 0

        theme_bonus = 0
        theme = self.monthly_theme

        # December - Reindeer Stations (special callsigns, 5 pts each, once per band)
        if theme == 'Dec - Reindeer':
            special_key = (callsign, band)
            # Check if this is a special station and hasn't been worked on this band yet
            if special_key not in self.dec_special_stations:
                is_special = False

                # Check all December special station categories
                if callsign in self.dec_reindeer_stations:
                    is_special = True
                elif callsign == self.dec_santa_station:
                    is_special = True
                elif callsign == self.dec_scrooge_station:
                    is_special = True
                elif callsign in self.dec_elf_stations:
                    is_special = True

                if is_special:
                    self.dec_special_stations.add(special_key)
                    theme_bonus = self.bonus_theme  # 5 points per special station per band
                    self.monthly_theme_qsos.append(f"{callsign}/{band}")

        return theme_bonus


def test_december_special_stations():
    """Test December WES special station tracking"""
    print("Testing December WES Special Station Tracking")
    print("=" * 60)

    contest = MockContestTab()

    test_cases = [
        # (callsign, band, skcc, expected_bonus, description)
        ('AI5BE', '40m', None, 5, 'Reindeer station (Dasher) on 40m'),
        ('AI5BE', '40m', None, 0, 'Duplicate: Dasher on 40m again'),
        ('AI5BE', '20m', None, 5, 'Dasher on new band (20m)'),
        ('K4KYN', '40m', None, 5, 'Santa station on 40m'),
        ('W4CMG', '40m', None, 5, 'Scrooge station on 40m'),
        ('G0RDO', '40m', None, 5, 'Elf station on 40m'),
        ('W1AW', '40m', None, 0, 'Regular station (not special)'),
        ('WM4Q', '80m', None, 5, 'Reindeer station (Dancer) on 80m'),
        ('F6EJN', '20m', None, 5, 'Elf station on 20m'),
        ('K4KYN', '20m', None, 5, 'Santa on new band (20m)'),
    ]

    total_bonus = 0
    for callsign, band, skcc, expected_bonus, description in test_cases:
        bonus = contest._calculate_theme_bonus(callsign, band, skcc)
        total_bonus += bonus
        status = "✓" if bonus == expected_bonus else "✗"
        print(f"{status} {description}")
        print(f"  Callsign: {callsign}, Band: {band}, Bonus: {bonus} (expected: {expected_bonus})")
        if bonus != expected_bonus:
            print(f"  ERROR: Expected {expected_bonus} but got {bonus}")

    print()
    print("=" * 60)
    print(f"Total special stations worked: {len(contest.dec_special_stations)}")
    print(f"Total theme bonus points: {total_bonus}")
    print(f"Theme QSOs: {len(contest.monthly_theme_qsos)}")
    print()
    print("Special stations by callsign:")

    # Group by callsign
    stations_by_call = {}
    for call, band in sorted(contest.dec_special_stations):
        if call not in stations_by_call:
            stations_by_call[call] = []
        stations_by_call[call].append(band)

    for call, bands in sorted(stations_by_call.items()):
        station_type = ""
        if call in contest.dec_reindeer_stations:
            station_type = "Reindeer"
        elif call == contest.dec_santa_station:
            station_type = "Santa"
        elif call == contest.dec_scrooge_station:
            station_type = "Scrooge"
        elif call in contest.dec_elf_stations:
            station_type = "Elf"

        bands_str = ', '.join(sorted(bands))
        print(f"  {call:<12} ({station_type:<8}) - {len(bands)} band(s): {bands_str}")

    print()
    print("All 22 special stations:")
    print(f"  Reindeer: {', '.join(sorted(contest.dec_reindeer_stations))}")
    print(f"  Santa: {contest.dec_santa_station}")
    print(f"  Scrooge: {contest.dec_scrooge_station}")
    print(f"  Elves: {', '.join(sorted(contest.dec_elf_stations))}")


if __name__ == '__main__':
    test_december_special_stations()
