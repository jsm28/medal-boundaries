#! /usr/bin/env python3

# Copyright 2015-2019 Joseph Samuel Myers.

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
NEXT_YEAR = 2020


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
            tex_file.write('%d & $%s$ & $%s$ & $%s$ \\\\\n'
                           % (year, print_frac(ideal_medals),
                              margin_below, margin_above))


def gen_bronze_alg_list(data):
    """
    Generate list of years where algorithms fail to predict the bronze
    boundary correctly.
    """
    algs = (('Never give medals to more than half the contestants: ',
             MarginAlgorithmLinear(1, 0, True)),
            ('Give as near half the contestants as possible medals, '
             'being generous in case of equality ($b\\ge a$)',
             MarginAlgorithmLinear(1, 1, False)),
            ('Go over if $b\\ge 5a$', MarginAlgorithmLinear(5, 1, False)),
            ('Go over if $b > 4a$', MarginAlgorithmLinear(4, 1, True)),
            ('Go over if $b\\ge 3.5a$', MarginAlgorithmLinear(7, 2, False)),
            ('Go over if $b\\ge 1.5a^2$',
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


def gen_gs_alg_table(data):
    """
    Generate list of years where algorithms fail to predict the gold
    and silver boundaries correctly.
    """
    algs = (('I', MedalAlgorithmIndependent()),
            ('S', MedalAlgorithmLowestFirst()),
            ('L^1', MedalAlgorithmLp(1, False)),
            ('L^2', MedalAlgorithmLp(2, False)),
            ('L^1s', MedalAlgorithmLp(1, True)),
            ('L^2s', MedalAlgorithmLp(2, True)),
            ('R', MedalAlgorithmRatio()))
    with open('gen-gs-alg-table.tex', 'w') as tex_file:
        ydata = {}
        for year in range(START_YEAR, NEXT_YEAR):
            d = data[year]
            dt = (d.cum_medal_stats[2], d.cum_medal_stats[1],
                  d.cum_medal_stats[0])
            ydata[year] = {dt: ['Actual']}
        for alg in algs:
            for year in range(START_YEAR, NEXT_YEAR):
                d = data[year]
                predicted = alg[1].compute_boundaries(d.cum_total_stats,
                                                      [1, 2, 3, 6],
                                                      [None, None,
                                                       d.cum_medal_stats[2],
                                                       None])
                pt = (predicted[2], predicted[1], predicted[0])
                if pt in ydata[year]:
                    ydata[year][pt].append(alg[0])
                else:
                    ydata[year][pt] = [alg[0]]
        max_num_opts = max([len(ydata[year].keys())
                            for year in range(START_YEAR, NEXT_YEAR)])
        col_descs = ['c' for i in range(max_num_opts+1)]
        tex_file.write('\\begin{tabular}{|%s|}\n' % '|'.join(col_descs))
        for year in range(START_YEAR, NEXT_YEAR):
            yd = ydata[year]
            ylist = []
            for k in sorted(yd.keys()):
                if 'Actual' in yd[k]:
                    ylist.append('{\\small\\textbf{(%d, %d, %d)}}'
                                 % (k[2], k[1]-k[2], k[0]-k[1]))
                else:
                    ylist.append('{\\small(%d, %d, %d)} {\\footnotesize $%s$}'
                                 % (k[2], k[1]-k[2], k[0]-k[1],
                                    ''.join(yd[k])))
            ylist.extend(['' for i in range(max_num_opts - len(ylist))])
            tex_file.write('%d & %s\\\\\n' % (year, ' & '.join(ylist)))
        tex_file.write('\\end{tabular}\n')


def main():
    """Generate all .tex files with IMO results analyses."""
    data = get_all_data()
    gen_bronze_table(data)
    gen_bronze_alg_list(data)
    gen_gs_alg_table(data)


main()
