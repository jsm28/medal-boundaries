# Results class for medalbound package.

# Copyright 2015-2017 Joseph Samuel Myers.

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
This module provides the Results base class that provides information
about results of mathematical olympiads.
"""

import os
import os.path
import sys
_py3 = sys.version_info.major >= 3
if _py3:
    import urllib.request
    urlretrieve = urllib.request.urlretrieve
else:
    import urllib
    urlretrieve = urllib.urlretrieve

__all__ = ['Results']

class Results(object):

    """
    A Results object represents the information about the results of a
    mathematical olympiad that is relevant to determining medal
    boundaries, together with the actual medal boundaries at that
    event.
    """

    def __init__(self, event_id):
        """
        Get the data for a given event, with an identifier that may be
        an event number or year (whatever is convenient for that kind
        of event).
        """
        self.event_id = event_id
        self.cache_dir = os.path.join('cache', self.get_cache_dir_name())
        if not os.access(self.cache_dir, os.F_OK):
            os.makedirs(self.cache_dir)
        files = self.get_cache_file_names()
        for f in files:
            if not os.access(os.path.join(self.cache_dir, f), os.F_OK):
                self.download_data(f)
        self.process_data()
        self.set_cum_stats()

    def get_cache_dir_name(self):
        """
        Return the name of a directory in which to cache event results.
        """
        raise NotImplementedError

    def get_cache_file_names(self):
        """Return a list of file names to download for an event."""
        raise NotImplementedError

    def download_data(self, file_name):
        """
        Download a particular file of data for an event.
        """
        url = self.get_data_url(file_name)
        urlretrieve(url, os.path.join(self.cache_dir, file_name))

    def get_data_url(self, file_name):
        """
        Return the URL to use for downloading a particular file of
        data for an event.
        """
        raise NotImplementedError

    def process_data(self):
        """
        Set various attributes of this object based on the data that
        has been downloaded.  num_contestants is the number of
        contestants.  max_total is the maximum total score of a
        contestant (possibly not achieved).  total_stats has the
        statistics of total scores.  medal_stats has the number of
        each kind of medal (starting with gold), and is None if medal
        boundaries have not yet been set at this event.
        """
        raise NotImplementedError

    def set_cum_stats(self):
        """Set the cumulative statistics of scores from this event."""
        self.cum_total_stats = [0 for i in range(self.max_total + 1)]
        cum_total = 0
        for i in range(self.max_total, -1, -1):
            cum_total += self.total_stats[i]
            self.cum_total_stats[i] = cum_total
        if self.medal_stats is None:
            self.sum_medal_stats = None
        else:
            self.cum_medal_stats = [0 for i in range(len(self.medal_stats))]
            cum_total = 0
            for i in range(len(self.medal_stats)):
                cum_total += self.medal_stats[i]
                self.cum_medal_stats[i] = cum_total
