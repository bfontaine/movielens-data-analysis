# -*- coding: UTF-8 -*-
#
# Plot a matrix of users x movies with a filled cell for each user/movie pair.
# The result will be very large (~1600 movies times 943 users)

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import numpy as np
from movies.analysis import RatingsGraph
from movies.plotting import plt
from movies.cache import Cache

cache = Cache()

rg = RatingsGraph()

def run():
    # sort users by their number of watched movies
    user_ranks = sorted(
            [(u, len(rg.user_movies(u))) for u in rg.users()],
            key=lambda p: p[1],
            reverse=True)
    users = [u for u, _ in user_ranks]

    # sort movies by their number of watchers
    movie_ranks = sorted(
            [(m, len(rg.movie_fans(m))) for m in rg.movies()],
            key=lambda p: p[1],
            reverse=True)
    movies = [m for m, _ in movie_ranks]

    matrix = np.zeros((len(users), len(movies)))

    for i, user in enumerate(users):
        user_movies = set(rg.user_movies(user))

        for j, movie in enumerate(movies):
            if movie not in user_movies:
                continue

            matrix[i, j] = 1

    plt.matshow(matrix)
    plt.show()

if __name__ == "__main__":
    run()
