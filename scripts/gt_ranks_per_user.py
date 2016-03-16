# -*- coding: UTF-8 -*-
#
# Plot a matrix with one line per user and one column per gatekeeper.
# Gatekeepers are ordered by decreasing frequency: the first on the left is the
# one with the most gatekeepees while the last one on the right is the one with
# the least gatekeepees. M_{i,j} is filled only if gatekeeper i gatekeeps user
# j. We sort users by the average rank of their gatekeepers.

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import numpy as np
from collections import defaultdict
from movies.analysis import RatingsGraph
from movies.plotting import plt
from movies.cache import Cache

cache = Cache()

#@cache.memoize0("gt_ranks_users_gatekeepers")
@cache.memoize0("gt_ranks_users_gatekeepers10:0.1769")
def get_users_gatekeepers():
    rg = RatingsGraph()
    return rg.users_movies_gatekeepers(10, 0.1769)

def run():
# This might take a long time, let's give some feedback
# It takes >30s without memoization, <1s with it
    print "Computing gatekeepers..."
    users_gatekeepers = get_users_gatekeepers()
    print "Done."

    gatekeepers = defaultdict(int)
    for gts in users_gatekeepers.values():
        for gt in gts:
            gatekeepers[gt] += 1

# remove gatekeepers with < 5 gatekeepees
    gatekeepers = {g: n for g, n in gatekeepers.items() if n >= 5}

    first = lambda p: p[0]
    second = lambda p: p[1]

    ranking = map(first, sorted(gatekeepers.items(), key=second, reverse=True))

    users = []
    for user in users_gatekeepers:
        gts = users_gatekeepers[user]
        ranks = []
        for gt in gts:
            if gt in ranking:
                ranks.append(ranking.index(gt))

        if not ranks:
            continue

        avg_rank = sum(ranks)/float(len(ranks))
        users.append((user, avg_rank, min(ranks), len(ranks)))

    # Sort by average gatekeeper rank then by the first rank
    def cmp_avg_rank_then_first_one(u1, u2):
        _, avg1, min1, n_ranks1 = u1
        _, avg2, min2, n_ranks2 = u2

        #return cmp(n_ranks1, n_ranks2)

        eq = cmp(avg1, avg2)
        if eq:
            return eq
        return cmp(min1, min2)

    users = map(first, sorted(users, cmp=cmp_avg_rank_then_first_one))

    matrix = np.zeros((len(users_gatekeepers), len(gatekeepers)))

    for user, gts in users_gatekeepers.items():
        for gt in gts:
            if gt not in ranking:
                continue
            u_idx = users.index(user)
            g_idx = ranking.index(gt)

            matrix[u_idx, g_idx] = 1

    plt.matshow(matrix)
    plt.show()

if __name__ == "__main__":
    run()
