# -*- coding: UTF-8 -*-

# Find max N such that there exist a bi-clique of >=N users and >=N movies.
# (or max N,M with N users and M movies)

import os
import sys
import itertools
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.analysis import RatingsGraph

def common_fans_size(m_ids):
    return len(rg.movies_fans(m_ids))

rg = RatingsGraph()

N = 0

movies = rg.movies()

# TODO optimize
for m in range(3, len(movies)):
    for movies_set in itertools.combinations(movies, m):
        n = common_fans_size(movies_set)

        if n == m and n > N:
            N = n
            print "N=%d" % N
            break
