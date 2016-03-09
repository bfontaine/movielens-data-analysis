# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import numpy as np
from movies import insights
from movies.analysis import RatingsGraph
from movies.plotting import plt
from movies.db import Movie

rg = RatingsGraph()
cc = insights.common_movies_fans(rg, 0.5, 10)

# cc above can be computed from this, if that's necessary
complete_cc = insights.common_movies_fans(rg, 0, 10)

fontsize = 7
movies = set()

for m1, ms in cc.items():
    movies.add(m1)
    for m2 in ms:
        movies.add(m2)

# those are the same movie
movies.remove("m266")
movies.remove("m680")

movies = sorted(movies, key=lambda m: len(rg.movie_fans(m)))
n = len(movies)

matrix = np.zeros((n, n))

# add more values
for m1, ms in complete_cc.items():
    for m2, corr in ms.items():
        if m1 not in movies or m2 not in movies:
            continue

        i1 = movies.index(m1)
        i2 = movies.index(m2)

        matrix[i1, i2] = corr
        matrix[i2, i1] = corr

# with open("ordered-matrix.json") as f:
#     import json
#     matrix = np.matrix(json.loads(f.read()))


#with open("/tmp/m.json", "w") as f:
#    import json
#    f.write(json.dumps(matrix.tolist()))
#    raise Exception()

fig_, ax = plt.subplots()
heatmap = ax.pcolor(matrix, cmap=plt.cm.Blues)

plt.axis([0, n, 0, n])

labels = ["%s (N=%d)" % (Movie.get_by_id(m).title, len(rg.movie_fans(m)))
        for m in movies]

ticks = np.arange(0, n)+0.4

ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.set_xticklabels(labels, rotation="vertical", fontsize=fontsize)
ax.set_yticklabels(labels, fontsize=fontsize)

plt.colorbar(heatmap, ax=ax)
plt.show()
