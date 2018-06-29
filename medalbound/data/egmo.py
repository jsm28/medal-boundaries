# EGMOResults class for medalbound package.

# Copyright 2017-2018 Joseph Samuel Myers.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <https://www.gnu.org/licenses/>.

"""
This module provides the EGMOResults class that provides information
about results of EGMOs.
"""

import os.path

from matholymp.fileutil import read_utf8_csv
from medalbound.data.results import Results

__all__ = ['EGMOResults']

class EGMOResults(Results):

    """Subclass of Results providing EGMO information."""

    def get_cache_dir_name(self):
        return 'egmo-%d' % self.event_id

    def get_cache_file_names(self):
        return ['countries.csv', 'people.csv']

    def get_data_url(self, file_name):
        if file_name == 'countries.csv':
            return ('https://www.egmo.org/egmos/egmo%d/countries/countries.csv'
                    % self.event_id)
        else:
            return ('https://www.egmo.org/egmos/egmo%d/people/people.csv'
                    % self.event_id)

    def process_data(self):
        countries_csv_name = os.path.join(self.cache_dir, 'countries.csv')
        people_csv_name = os.path.join(self.cache_dir, 'people.csv')
        countries = read_utf8_csv(countries_csv_name)
        countries_official = { c['Code'] for c in countries
                               if c['Official European'] == 'Yes' }
        people = read_utf8_csv(people_csv_name)
        people = [p for p in people
                  if p['Contestant Code']
                  and p['Country Code'] in countries_official]
        self.max_total = 56 if self.event_id == 1 else 42
        self.total_stats = [0 for i in range(self.max_total + 1)]
        award_stats = {'Gold Medal': 0, 'Silver Medal': 0, 'Bronze Medal': 0,
                       '': 0}
        self.num_contestants = 0
        for c in people:
            self.num_contestants += 1
            total = int(c['Total'])
            award = c['Award']
            if award == 'Honourable Mention':
                award = ''
            if award not in award_stats:
                raise ValueError('Unknown award: %s' % award)
            self.total_stats[total] += 1
            award_stats[award] += 1
        self.medal_stats = [award_stats['Gold Medal'],
                            award_stats['Silver Medal'],
                            award_stats['Bronze Medal']]
