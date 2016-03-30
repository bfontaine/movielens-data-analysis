# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.analysis import global_ratings_graph
from movies.db import Movie

rg = global_ratings_graph()

# greedy algorithm
people = set(rg.users())
movies = [(m, set(rg.movie_fans(m))) for m in rg.movies()]

covering_movies = []

while people:
    best_coverage = 0
    best_idx = -1

    for i, (_, fans) in enumerate(movies):
        coverage = len(people.intersection(fans))
        if coverage > best_coverage:
            best_coverage = coverage
            best_idx = i

    best_movie, fans = movies.pop(best_idx)
    people.difference_update(fans)
    covering_movies.append((best_movie, best_coverage))

print len(covering_movies)
print "\n".join([
    "%-50s -- %3d" % (Movie.get_by_id(m).title, c) for m, c in covering_movies])
