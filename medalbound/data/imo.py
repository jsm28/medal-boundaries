# IMOResults class for medalbound package.

# Copyright 2015-2022 Joseph Samuel Myers.

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
This module provides the IMOResults class that provides information
about results of IMOs.
"""

import os.path
import xml.etree.ElementTree

from medalbound.data.results import Results

__all__ = ['IMOResults']


class IMOResults(Results):

    """Subclass of Results providing IMO information."""

    def get_cache_dir_name(self):
        return 'imo-%d' % self.event_id

    def get_cache_file_names(self):
        return ['IMO_Individual.xml']

    def get_data_url(self, file_name):
        return ('https://www.imo-official.org/year_individual_r.aspx'
                '?year=%d&column=total&order=desc&download=XML'
                % self.event_id)

    def imo_special_case_exclude(self, contestant_id):
        """
        Return whether this contestant should be excluded for the
        purposes of medal boundaries consideration.
        """
        # At IMO 2005, because of problems with the transmission of
        # one translation to the contestants, medal boundaries were
        # determined without considering two contestants, and then
        # those contestants were given awards as if they had scored 7
        # on the affected problem.  One ineligible contestant was
        # disqualified in 2016 from IMOs 2010, 2011 and 2012; cached
        # downloaded data might predate that disqualification, while
        # their scores need adding back for data from after the
        # disqualification so the calculations reflect the same data
        # used by the Jury to decide medal boundaries at the time.
        special_cases = ((2005, '8613'), (2005, '8678'),
                         (2010, '19342'), (2011, '20886'), (2012, '21815'))
        return (self.event_id, contestant_id) in special_cases

    def imo_special_case_add(self):
        """Return special cases (total, award) to add for this event."""
        special_cases = {2010: [(21, 'Silver medal')],
                         2011: [(14, '')],
                         2012: [(18, 'Bronze medal')]}
        if self.event_id in special_cases:
            return special_cases[self.event_id]
        else:
            return []

    def process_data(self):
        xml_file_name = os.path.join(self.cache_dir, 'IMO_Individual.xml')
        xml_et = xml.etree.ElementTree.parse(xml_file_name)
        # This information isn't in the XML file, just assume it
        # always has this value for years for which this code is used.
        self.max_total = 42
        self.total_stats = [0 for i in range(self.max_total + 1)]
        award_stats = {'Gold medal': 0, 'Silver medal': 0, 'Bronze medal': 0,
                       '': 0}
        self.num_contestants = 0
        for c in xml_et.iter('contestant'):
            if not self.imo_special_case_exclude(c.attrib['id']):
                self.num_contestants += 1
                total = int(c.find('total').text)
                award = c.find('award').text
                if award == 'Honourable mention' or award is None:
                    award = ''
                if award not in award_stats:
                    raise ValueError('Unknown award: %s' % award)
                self.total_stats[total] += 1
                award_stats[award] += 1
        for c in self.imo_special_case_add():
            self.num_contestants += 1
            self.total_stats[c[0]] += 1
            award_stats[c[1]] += 1
        self.medal_stats = [award_stats['Gold medal'],
                            award_stats['Silver medal'],
                            award_stats['Bronze medal']]
