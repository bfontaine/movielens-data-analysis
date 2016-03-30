# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.analysis import global_ratings_graph

rg = global_ratings_graph()

movies = [(m, len(rg.movie_fans(m))) for m in rg.movies()]
movies.sort(key=lambda p: p[1], reverse=True)

users = set(rg.users())
# people who haven't seen all movies (in the current set)
people = set()
# people who haven't seen any movie (in the current set)
hipsters = set(users)

limit_printed = False

# For each movie from the most watched to the least watched update the `people`
# set with the users who haven't seen it and print the current length
# We stop when all users are in the set.
for i, (movie, _) in enumerate(movies):
    haventseen = users.difference(rg.movie_fans(movie))
    people.update(haventseen)
    hipsters.intersection_update(haventseen)
    print "Movie %2d: %3d people missed >=1, %3d people haven't seen any" % (
            i, len(people), len(hipsters))
    if len(people) == len(users) and not limit_printed:
        print "-------------------"
        limit_printed = True
    if not hipsters:
        break
