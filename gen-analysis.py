#! /usr/bin/env python

# Copyright 2015 Joseph Samuel Myers.

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
Generate .tex files with IMO results analyses.
"""

import fractions

from medalbound.algorithms import get_cum_alternatives
from medalbound.data.imo import IMOResults

START_YEAR = 1986
NEXT_YEAR = 2016

def get_all_data():
    """Load results for all relevant IMOs."""
    data = {}
    for year in range(START_YEAR, NEXT_YEAR):
        data[year] = IMOResults(year)
    return data

def print_frac(f):
    """Return text for a non-negative fraction in LaTeX form."""
    assert f >= 0
    int_part = f.numerator // f.denominator
    if f == int_part:
        return '%d' % int_part
    else:
        fp = f - int_part
        if int_part == 0:
            int_part = ''
        else:
            int_part = str(int_part)
        return '%s\\frac{%d}{%d}' % (int_part, fp.numerator, fp.denominator)

def gen_bronze_table(data):
    """Generate table of bronze boundary choices."""
    with open('gen-bronze-table.tex', 'w') as tex_file:
        for year in range(START_YEAR, NEXT_YEAR):
            d = data[year]
            ideal_medals = fractions.Fraction(d.num_contestants, 2)
            (num_below, num_above) = get_cum_alternatives(ideal_medals,
                                                          d.cum_total_stats)
            actual_medals = d.cum_medal_stats[2]
            margin_below = ideal_medals - num_below
            margin_above = num_above - ideal_medals
            margin_below = print_frac(margin_below)
            margin_above = print_frac(margin_above)
            if num_below == actual_medals:
                margin_below = '\\mathbf{%s}' % margin_below
            if num_above == actual_medals:
                margin_above = '\\mathbf{%s}' % margin_above
            tex_file.write('%d & $%s$ & $%s$ & $%s$ \\\\\n' %
                           (year, print_frac(ideal_medals),
                            margin_below, margin_above))

def main():
    """Generate all .tex files with IMO results analyses."""
    data = get_all_data()
    gen_bronze_table(data)

main()
