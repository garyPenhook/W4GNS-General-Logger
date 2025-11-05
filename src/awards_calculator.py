"""
ARRL Awards Calculator
Calculates progress toward various ARRL awards based on logged contacts
"""

from collections import defaultdict
import re


class AwardsCalculator:
    """Calculate ARRL award progress from contact database"""

    def __init__(self, database):
        self.database = database

    def calculate_all_awards(self):
        """Calculate progress for all supported ARRL awards"""
        contacts = self.database.get_all_contacts()

        return {
            'dxcc': self.calculate_dxcc(contacts),
            'was': self.calculate_was(contacts),
            'wac': self.calculate_wac(contacts),
            'wpx': self.calculate_wpx(contacts),
            'vucc': self.calculate_vucc(contacts)
        }

    def calculate_dxcc(self, contacts):
        """
        DXCC (DX Century Club) - Work 100 different countries/entities

        Returns:
            dict: Total countries worked, by band, by mode, countries list
        """
        # Track overall, by band, by mode
        countries_overall = set()
        countries_by_band = defaultdict(set)
        countries_by_mode = defaultdict(set)

        country_list = []

        for contact in contacts:
            contact_dict = dict(contact)
            country = contact_dict.get('country', '').strip()
            band = contact_dict.get('band', '').strip()
            mode = contact_dict.get('mode', '').strip()
            callsign = contact_dict.get('callsign', '').strip()
            date = contact_dict.get('date', '')

            if country:
                if country not in countries_overall:
                    countries_overall.add(country)
                    country_list.append({
                        'country': country,
                        'callsign': callsign,
                        'date': date,
                        'band': band,
                        'mode': mode
                    })

                if band:
                    countries_by_band[band].add(country)

                if mode:
                    # Normalize mode
                    mode_cat = self._normalize_mode(mode)
                    countries_by_mode[mode_cat].add(country)

        # Sort country list by date
        country_list.sort(key=lambda x: x['date'])

        return {
            'total': len(countries_overall),
            'goal': 100,
            'percent': min(100, (len(countries_overall) / 100) * 100),
            'countries': sorted(list(countries_overall)),
            'country_details': country_list,
            'by_band': {band: len(countries) for band, countries in countries_by_band.items()},
            'by_mode': {mode: len(countries) for mode, countries in countries_by_mode.items()},
            'needed': max(0, 100 - len(countries_overall))
        }

    def calculate_was(self, contacts):
        """
        WAS (Worked All States) - Work all 50 US states

        Returns:
            dict: Total states worked, by band, by mode, states list
        """
        us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }

        states_overall = set()
        states_by_band = defaultdict(set)
        states_by_mode = defaultdict(set)

        state_list = []

        for contact in contacts:
            contact_dict = dict(contact)
            state = contact_dict.get('state', '').strip().upper()
            country = contact_dict.get('country', '').strip()
            band = contact_dict.get('band', '').strip()
            mode = contact_dict.get('mode', '').strip()
            callsign = contact_dict.get('callsign', '').strip()
            date = contact_dict.get('date', '')

            # Only count if in USA and valid state
            if country in ['United States', 'USA', 'US'] and state in us_states:
                if state not in states_overall:
                    states_overall.add(state)
                    state_list.append({
                        'state': state,
                        'callsign': callsign,
                        'date': date,
                        'band': band,
                        'mode': mode
                    })

                if band:
                    states_by_band[band].add(state)

                if mode:
                    mode_cat = self._normalize_mode(mode)
                    states_by_mode[mode_cat].add(state)

        # Sort state list by date
        state_list.sort(key=lambda x: x['date'])

        missing_states = us_states - states_overall

        return {
            'total': len(states_overall),
            'goal': 50,
            'percent': (len(states_overall) / 50) * 100,
            'states': sorted(list(states_overall)),
            'state_details': state_list,
            'missing': sorted(list(missing_states)),
            'by_band': {band: len(states) for band, states in states_by_band.items()},
            'by_mode': {mode: len(states) for mode, states in states_by_mode.items()},
            'needed': len(missing_states)
        }

    def calculate_wac(self, contacts):
        """
        WAC (Worked All Continents) - Work all 6 continents

        Returns:
            dict: Continents worked, by band, by mode
        """
        continents = {'NA', 'SA', 'EU', 'AF', 'AS', 'OC'}

        continents_overall = set()
        continents_by_band = defaultdict(set)
        continents_by_mode = defaultdict(set)

        continent_list = []

        for contact in contacts:
            contact_dict = dict(contact)
            continent = contact_dict.get('continent', '').strip().upper()
            band = contact_dict.get('band', '').strip()
            mode = contact_dict.get('mode', '').strip()
            callsign = contact_dict.get('callsign', '').strip()
            date = contact_dict.get('date', '')
            country = contact_dict.get('country', '')

            if continent in continents:
                if continent not in continents_overall:
                    continents_overall.add(continent)
                    continent_list.append({
                        'continent': continent,
                        'callsign': callsign,
                        'country': country,
                        'date': date,
                        'band': band,
                        'mode': mode
                    })

                if band:
                    continents_by_band[band].add(continent)

                if mode:
                    mode_cat = self._normalize_mode(mode)
                    continents_by_mode[mode_cat].add(continent)

        # Sort continent list by date
        continent_list.sort(key=lambda x: x['date'])

        missing_continents = continents - continents_overall

        continent_names = {
            'NA': 'North America',
            'SA': 'South America',
            'EU': 'Europe',
            'AF': 'Africa',
            'AS': 'Asia',
            'OC': 'Oceania'
        }

        return {
            'total': len(continents_overall),
            'goal': 6,
            'percent': (len(continents_overall) / 6) * 100,
            'continents': sorted(list(continents_overall)),
            'continent_details': continent_list,
            'missing': [continent_names[c] for c in sorted(missing_continents)],
            'by_band': {band: len(conts) for band, conts in continents_by_band.items()},
            'by_mode': {mode: len(conts) for mode, conts in continents_by_mode.items()},
            'needed': len(missing_continents)
        }

    def calculate_wpx(self, contacts):
        """
        WPX (Worked All Prefixes) - Work different call sign prefixes

        Returns:
            dict: Total prefixes worked, by band, by mode
        """
        prefixes_overall = set()
        prefixes_by_band = defaultdict(set)
        prefixes_by_mode = defaultdict(set)

        for contact in contacts:
            contact_dict = dict(contact)
            callsign = contact_dict.get('callsign', '').strip().upper()
            band = contact_dict.get('band', '').strip()
            mode = contact_dict.get('mode', '').strip()

            if callsign:
                prefix = self._extract_prefix(callsign)
                if prefix:
                    prefixes_overall.add(prefix)

                    if band:
                        prefixes_by_band[band].add(prefix)

                    if mode:
                        mode_cat = self._normalize_mode(mode)
                        prefixes_by_mode[mode_cat].add(prefix)

        return {
            'total': len(prefixes_overall),
            'prefixes': sorted(list(prefixes_overall)),
            'by_band': {band: len(prefixes) for band, prefixes in prefixes_by_band.items()},
            'by_mode': {mode: len(prefixes) for mode, prefixes in prefixes_by_mode.items()}
        }

    def calculate_vucc(self, contacts):
        """
        VUCC (VHF/UHF Century Club) - Work 100 grid squares on VHF/UHF bands

        Returns:
            dict: Total grids worked on VHF/UHF, by band
        """
        vhf_uhf_bands = {'6m', '2m', '70cm', '1.25m', '33cm', '23cm'}

        grids_overall = set()
        grids_by_band = defaultdict(set)

        grid_list = []

        for contact in contacts:
            contact_dict = dict(contact)
            grid = contact_dict.get('gridsquare', '').strip().upper()
            band = contact_dict.get('band', '').strip()
            callsign = contact_dict.get('callsign', '').strip()
            date = contact_dict.get('date', '')

            # Only count VHF/UHF bands
            if band in vhf_uhf_bands and grid and len(grid) >= 4:
                # Use 4-character grid
                grid_4 = grid[:4]

                if grid_4 not in grids_overall:
                    grids_overall.add(grid_4)
                    grid_list.append({
                        'grid': grid_4,
                        'callsign': callsign,
                        'date': date,
                        'band': band
                    })

                if band:
                    grids_by_band[band].add(grid_4)

        # Sort grid list by date
        grid_list.sort(key=lambda x: x['date'])

        return {
            'total': len(grids_overall),
            'goal': 100,
            'percent': min(100, (len(grids_overall) / 100) * 100),
            'grids': sorted(list(grids_overall)),
            'grid_details': grid_list,
            'by_band': {band: len(grids) for band, grids in grids_by_band.items()},
            'needed': max(0, 100 - len(grids_overall))
        }

    def _extract_prefix(self, callsign):
        """
        Extract WPX prefix from callsign

        Rules:
        - Prefix is everything before the first digit
        - Include the first digit in the prefix
        """
        # Find first digit
        match = re.search(r'\d', callsign)
        if match:
            pos = match.start()
            # Include digit and all before it
            return callsign[:pos+1]
        return None

    def _normalize_mode(self, mode):
        """Normalize mode for award tracking"""
        mode = mode.upper()

        # Phone modes
        if mode in ['SSB', 'USB', 'LSB', 'FM', 'AM']:
            return 'PHONE'

        # CW
        if mode == 'CW':
            return 'CW'

        # Digital modes
        if mode in ['FT8', 'FT4', 'RTTY', 'PSK31', 'PSK63', 'JT65', 'JT9', 'MFSK', 'OLIVIA', 'CONTESTIA']:
            return 'DIGITAL'

        return mode
