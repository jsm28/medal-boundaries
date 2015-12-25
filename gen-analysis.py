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

from medalbound.algorithms import get_cum_alternatives, \
    MarginAlgorithmLinear, MarginAlgorithmQuadratic, \
    MedalAlgorithmIndependent, MedalAlgorithmLowestFirst, \
    MedalAlgorithmLp, MedalAlgorithmRatio
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

def gen_bronze_alg_list(data):
    """
    Generate list of years where algorithms fail to predict the bronze
    boundary correctly.
    """
    algs = (('Never give medals to more than half the contestants: ',
             MarginAlgorithmLinear(1, 0, True)),
            ('Give as near half the contestants as possible medals, '
             'being generous in case of equality ($b\ge a$)',
             MarginAlgorithmLinear(1, 1, False)),
            ('Go over if $b\ge 5a$', MarginAlgorithmLinear(5, 1, False)),
            ('Go over if $b > 4a$', MarginAlgorithmLinear(4, 1, True)),
            ('Go over if $b\ge 3.5a$', MarginAlgorithmLinear(7, 2, False)),
            ('Go over if $b\ge 1.5a^2$',
             MarginAlgorithmQuadratic(3, 2, False)))
    with open('gen-bronze-alg-list.tex', 'w') as tex_file:
        for alg in algs:
            ylist = []
            for year in range(START_YEAR, NEXT_YEAR):
                d = data[year]
                predicted = alg[1].compute_boundaries(d.cum_total_stats,
                                                      [1, 2, 3, 6],
                                                      [None, None, None, None])
                if predicted[2] != d.cum_medal_stats[2]:
                    ylist.append(year)
            ylist = [str(y) for y in ylist]
            tex_file.write('\\item %s: %s.\n' % (alg[0], ', '.join(ylist)))

def gen_gs_alg_list(data):
    """
    Generate list of years where algorithms fail to predict the gold
    and silver boundaries correctly.
    """
    algs = (('Choose boundaries independently', MedalAlgorithmIndependent()),
            ('Choose silver first', MedalAlgorithmLowestFirst()),
            ('$L^1$, unscaled', MedalAlgorithmLp(1, False)),
            ('$L^2$, unscaled', MedalAlgorithmLp(2, False)),
            ('$L^1$, scaled', MedalAlgorithmLp(1, True)),
            ('$L^2$, scaled', MedalAlgorithmLp(2, True)),
            ('Ratios', MedalAlgorithmRatio()))
    with open('gen-gs-alg-list.tex', 'w') as tex_file:
        for alg in algs:
            ylist = []
            for year in range(START_YEAR, NEXT_YEAR):
                d = data[year]
                predicted = alg[1].compute_boundaries(d.cum_total_stats,
                                                      [1, 2, 3, 6],
                                                      [None, None,
                                                       d.cum_medal_stats[2],
                                                       None])
                if (predicted[0] != d.cum_medal_stats[0] or
                    predicted[1] != d.cum_medal_stats[1]):
                    actual = '(%d, %d, %d)' % (d.medal_stats[0],
                                               d.medal_stats[1],
                                               d.medal_stats[2])
                    pred = '(%d, %d, %d)' % (predicted[0],
                                             predicted[1] - predicted[0],
                                             predicted[2] - predicted[1])
                    ybad = '%d (%s predicted, %s actual)' % (year,
                                                             pred,
                                                             actual)
                    ylist.append(ybad)
            tex_file.write('\\item %s: %s.\n' % (alg[0], ', '.join(ylist)))

def main():
    """Generate all .tex files with IMO results analyses."""
    data = get_all_data()
    gen_bronze_table(data)
    gen_bronze_alg_list(data)
    gen_gs_alg_list(data)

main()
