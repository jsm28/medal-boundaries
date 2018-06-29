# Algorithms classes for medalbound package.

# Copyright 2015-2018 Joseph Samuel Myers.

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
This module provides algorithms for determining medal boundaries for
mathematical olympiads.
"""

import fractions

__all__ = ['get_cum_alternatives', 'Algorithm', 'MarginAlgorithm',
           'MarginAlgorithmLinear', 'MarginAlgorithmQuadratic',
           'MedalAlgorithmIndependent', 'MedalAlgorithmLowestFirst',
           'MedalAlgorithmScore', 'MedalAlgorithmLp', 'MedalAlgorithmRatio']


def get_cum_alternatives(ideal_cum, cum_stats):
    """Return alternatives for the number of medals around an ideal value."""
    num_below = 0
    for i in range(len(cum_stats)-1, -1, -1):
        if cum_stats[i] <= ideal_cum:
            num_below = cum_stats[i]
        if cum_stats[i] >= ideal_cum:
            return (num_below, cum_stats[i])
    raise ValueError('Ideal number of medals exceeds number of contestants')


class Algorithm(object):

    """
    An Algorithm object represents an algorithm for determining some
    or all medal boundaries based on cumulative statistics of
    contestants at or above each score (or other measure of rank),
    possibly given some boundaries that have already been determined.
    """

    def compute_boundaries(self, cum_stats, goal, known_bound):
        """
        Compute boundaries and return a list with cumulative
        statistics for the number of contestants with a given medal or
        above, possibly None for any boundaries not computed.
        cum_stats has cumulative statistics by rank (best contestants
        / highest scores last); goal has the desired proportions
        (e.g. [1, 2, 3, 6] for the IMO); known_bound has the already
        determined boundaries.  An algorithm is expected to work with
        a fixed set of boundaries having already been computed (for
        example, a gold/silver algorithm existing bronze boundaries to
        have been computed already) and does not need to be flexible
        about what information is provided.
        """
        raise NotImplementedError


class MarginAlgorithm(Algorithm):

    """
    A MarginAlgorithm determines the total number of medals based on
    the choices for how many medals to go above or below the ideal
    number of medals.
    """

    def __init__(self, choice_fn):
        """
        Initialise a MarginAlgorithm.  choice_fn(margin_below,
        margin_above) should return True if going above the ideal
        number of medals, False otherwise.
        """
        self.choice_fn = choice_fn

    def compute_boundaries(self, cum_stats, goal, known_bound):
        if len(known_bound) != len(goal):
            raise ValueError('Inconsistency in number of possible awards')
        num_contestants = cum_stats[0]
        goal_sum = sum(goal)
        goal_sum_medals = goal_sum - goal[-1]
        goal_medal_frac = fractions.Fraction(goal_sum_medals, goal_sum)
        goal_medal_ideal = num_contestants * goal_medal_frac
        (num_below, num_above) = get_cum_alternatives(goal_medal_ideal,
                                                      cum_stats)
        margin_below = goal_medal_ideal - num_below
        margin_above = num_above - goal_medal_ideal
        if self.choice_fn(margin_below, margin_above):
            num_medals = num_above
        else:
            num_medals = num_below
        ret = [None for i in goal]
        ret[-2] = num_medals
        ret[-1] = num_contestants
        return ret


class MarginAlgorithmLinear(MarginAlgorithm):

    """
    A MarginAlgorithmLinear determines the total number of medals
    based on a linear comparison of the choices for how many medals to
    go above or below the ideal number.
    """

    def __init__(self, num, den, strict_ineq):
        """
        Initialise a MarginAlgorithmLinear.  If the choices are a
        medals above the ideal number or b below the ideal number,
        choose to go above if b >= (num/den)*a (> instead of >= if
        strict_ineq).
        """
        def choose_linear(margin_below, margin_above):
            if den * margin_below > num * margin_above:
                return True
            elif den * margin_below == num * margin_above and not strict_ineq:
                return True
            else:
                return False
        super(MarginAlgorithmLinear, self).__init__(choose_linear)


class MarginAlgorithmQuadratic(MarginAlgorithm):

    """
    A MarginAlgorithmQuadratic determines the total number of medals
    based on a quadratic comparison of the choices for how many medals
    to go above or below the ideal number.
    """

    def __init__(self, num, den, strict_ineq):
        """
        Initialise a MarginAlgorithmQuadratic.  If the choices are a
        medals above the ideal number or b below the ideal number,
        choose to go above if b >= (num/den)*a^2 (> instead of >= if
        strict_ineq).
        """
        def choose_quadratic(margin_below, margin_above):
            margin_above_2 = margin_above * margin_above
            if den * margin_below > num * margin_above_2:
                return True
            elif den * margin_below == num * margin_above_2 and not strict_ineq:
                return True
            else:
                return False
        super(MarginAlgorithmQuadratic, self).__init__(choose_quadratic)


class MedalAlgorithmIndependent(Algorithm):

    """
    A MedalAlgorithmIndependent determines the margin for each type of
    medal independently, by making the number of contestants with that
    medal or above as close as possible to the ideal number,
    determined based on the total number of medals, and erring on the
    side of generosity in the case of equality.
    """

    def compute_boundaries(self, cum_stats, goal, known_bound):
        if len(known_bound) != len(goal):
            raise ValueError('Inconsistency in number of possible awards')
        num_medals = known_bound[-2]
        goal_sum = sum(goal)
        goal_sum_medals = goal_sum - goal[-1]
        num_to_find = len(goal) - 2
        ret = list(known_bound)
        for i in range(num_to_find):
            goal_sum_high = sum(goal[0:i+1])
            goal_frac = fractions.Fraction(goal_sum_high, goal_sum_medals)
            goal_ideal = num_medals * goal_frac
            (num_below, num_above) = get_cum_alternatives(goal_ideal,
                                                          cum_stats)
            margin_below = goal_ideal - num_below
            margin_above = num_above - goal_ideal
            if margin_below >= margin_above:
                ret[i] = num_above
            else:
                ret[i] = num_below
        return ret


class MedalAlgorithmLowestFirst(Algorithm):

    """
    A MedalAlgorithmLowestFirst determines the margin for each type of
    medal starting with the second-lowest, by making the number of
    contestants with that medal or above as close as possible to the
    ideal number, determined based on the total number of medals, and
    erring on the side of generosity in the case of equality, then
    repeating with the number with each medal or above as a proportion
    of those with the next lower medal or above.
    """

    def compute_boundaries(self, cum_stats, goal, known_bound):
        if len(known_bound) != len(goal):
            raise ValueError('Inconsistency in number of possible awards')
        num_to_find = len(goal) - 2
        ret = list(known_bound)
        for i in range(num_to_find-1, -1, -1):
            goal_sum_num = sum(goal[0:i+1])
            goal_sum_den = sum(goal[0:i+2])
            goal_frac = fractions.Fraction(goal_sum_num, goal_sum_den)
            goal_ideal = ret[i+1] * goal_frac
            (num_below, num_above) = get_cum_alternatives(goal_ideal,
                                                          cum_stats)
            margin_below = goal_ideal - num_below
            margin_above = num_above - goal_ideal
            if margin_below >= margin_above:
                ret[i] = num_above
            else:
                ret[i] = num_below
        return ret


class MedalAlgorithmScore(Algorithm):

    """
    A MedalAlgorithmScore determines the margin for each type of
    medal, given the total number of medals, by minimising a score
    function that represents the deviation from the ideal.
    """

    def __init__(self, score_fn):
        """
        Initialise a MedalAlgorithmScore.  score_fn is given the goal
        and cumulative statistics for the number of contestants with
        each medal or above (ending with the total number of
        contestants, which is ignored).
        """
        self.score_fn = score_fn

    def _search_by_score(self, cum_stats, goal, known_bound, pos):
        best_bound = None
        best_score = None
        have_best_score = False
        for i in range(len(cum_stats)-1, -1, -1):
            if cum_stats[i] > known_bound[pos+1]:
                break
            rec_bound = list(known_bound)
            rec_bound[pos] = cum_stats[i]
            if pos == 0:
                new_bound = rec_bound
                new_score = self.score_fn(goal, rec_bound)
            else:
                (new_score, new_bound) = self._search_by_score(cum_stats,
                                                               goal,
                                                               rec_bound,
                                                               pos-1)
            if not have_best_score:
                best_bound = new_bound
                best_score = new_score
                have_best_score = True
            elif new_score <= best_score:
                # In the case of equality of scores, we prefer to give
                # more people gold+silver, then to give more people
                # gold.  This corresponds to later examples with the
                # same score being preferred over earlier ones.
                best_bound = new_bound
                best_score = new_score
        if not have_best_score:
            raise ValueError('No admissible boundaries found')
        return (best_score, best_bound)

    def compute_boundaries(self, cum_stats, goal, known_bound):
        if len(known_bound) != len(goal):
            raise ValueError('Inconsistency in number of possible awards')
        (score, ret) = self._search_by_score(cum_stats, goal, known_bound,
                                             len(known_bound)-3)
        return ret


class MedalAlgorithmLp(MedalAlgorithmScore):

    """
    A MedalAlgorithmLp determines the margin for each type of medal,
    given the total number of medals, by minimising the L^p norm of
    the vector of differences between the actual number of medals and
    the ideal number of medals of each type, possibly after first
    scaling those numbers so that the ideal numbers are equal.
    """

    def __init__(self, p, scale):
        """Initialise a MedalAlgorithmLp."""
        def score_lp(goal, bounds):
            num_medal_types = len(goal)-1
            goal_total = sum(goal[0:num_medal_types])
            score = 0
            for i in range(num_medal_types):
                num_this_medal = bounds[i]
                if i > 0:
                    num_this_medal -= bounds[i-1]
                ideal_this_medal = bounds[-2]
                if scale:
                    num_this_medal *= fractions.Fraction(goal_total, goal[i])
                else:
                    ideal_this_medal *= fractions.Fraction(goal[i], goal_total)
                diff = abs(num_this_medal - ideal_this_medal)
                score += pow(diff, p)
            return score
        super(MedalAlgorithmLp, self).__init__(score_lp)


class MedalAlgorithmRatio(MedalAlgorithmScore):

    """
    A MedalAlgorithmRatio determines the margin for each type of
    medal, given the total number of medals, by minimising the sum of
    scaled ratios of each ordered pair of types of medals, where the
    scaling makes the ideal ratio equal to 1 (so if there are N types
    of medal, the minimum score in the case of equality is N(N-1) by
    AM-GM).
    """

    def __init__(self):
        """Initialise a MedalAlgorithmRatio."""
        def score_ratio(goal, bounds):
            num_medal_types = len(goal)-1
            num_medals = []
            for i in range(num_medal_types):
                num_this_medal = bounds[i]
                if i > 0:
                    num_this_medal -= bounds[i-1]
                num_medals.append(num_this_medal)
                # Cases with zero of a medal are less-preferred than any others.
                if num_this_medal == 0:
                    return (1, 0)
            score = 0
            for i in range(num_medal_types):
                for j in range(num_medal_types):
                    if i != j:
                        ratio = fractions.Fraction(num_medals[i], num_medals[j])
                        goal_ratio = fractions.Fraction(goal[i], goal[j])
                        score += ratio / goal_ratio
            return (0, score)
        super(MedalAlgorithmRatio, self).__init__(score_ratio)
