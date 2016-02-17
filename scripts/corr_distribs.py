# -*- coding: UTF-8 -*-

# Copy of plot_distribs except that we use colors to show how each distribution
# correlates with the top-right one

# This script could be refacted, it's kinda ugly and inefficient as is

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import numpy as np
import json
from movies.listutils import correlation

# avoid an annoying (useless) warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import matplotlib.pyplot as plt


distribs = []
users = []

# ditribution with the most people
max_distrib = []

# used to get the top-right distrib
max_gt_count = 0
min_buddy_threshold = 1

gt_counts = set()
buddy_thresholds = set()

filename = "distributions-people-ids.jsons"

with open(filename) as f:
    for line in f:
        d = json.loads(line)

        distribs.append(d)

        distrib = d["distribution"]
        gt_count = d["gt_count"]
        buddy_threshold = d["buddy_threshold"]

        max_gt_count = max(max_gt_count, gt_count)
        min_buddy_threshold = min(min_buddy_threshold, buddy_threshold)

        if max_gt_count == gt_count and min_buddy_threshold == buddy_threshold:
            max_distrib = d

        gt_counts.add(d["gt_count"])
        buddy_thresholds.add(d["buddy_threshold"])

#           buddy_threshold
#          +--------------->
#          | _  _  _  _  _
# gt_count | _  _  _  _  _
#          | _  _  _  ...
#          V
nrows = len(gt_counts)
ncols = len(buddy_thresholds)

last_row_index = ncols * (nrows - 1)

users = set()
for d in distribs:
    for arr in d["distribution"]:
        users.update(arr)

# We need to have an ordered list of all users in order to construct rankings.
# Each distribution D will be an array of the same size of this one (U), and
# D[i] = r means the user U[i] is ranked at the position r.
#
# e.g. with users = [u1, u2, u3] and a distribution [[], [u1, u3], [u2]] we'll
# have this ranking:
#   [1, 2, 1]
#
users = sorted(users, key=lambda u: int(u[1:]))

# We use these for users who are not ranked
INFINITY = 1000

rankings = []
max_ranking = []

for d in distribs:
    arr = d["distribution"]

    ranking = [INFINITY] * len(users)
    for pos, gts in enumerate(arr):
        for u in gts:
            idx = users.index(u)
            ranking[idx] = pos

    d["ranking"] = ranking

    if d == max_distrib:
        max_ranking = ranking
    rankings.append(d)

# Now compute the correlation between each ranking and the reference one, i.e.
# the one with min buddy_threshold and max gt_count
ncols = len(gt_counts)
nrows = len(buddy_thresholds)

corr2d = np.zeros((nrows, ncols))
i = 0
j = 0

for d in distribs:
    ranking = d["ranking"]

    if len(ranking) != len(max_ranking):
        print max_ranking

    corr = correlation(ranking, max_ranking)

    corr2d[j, i] = corr
    i += 1
    if i >= ncols:
        i = 0
        j += 1

# flip up/down
corr2d = np.flipud(corr2d)

fig_, ax = plt.subplots()
heatmap = ax.pcolor(corr2d, cmap=plt.cm.RdBu, vmin=-1, vmax=1)

plt.axis((0, len(gt_counts), 0, len(buddy_thresholds)))

ticks = np.arange(0, 10)+0.4
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.set_xticklabels(sorted(gt_counts))
# reverse=True because we flipped the matrix up/down
ax.set_yticklabels(["%.4f" % b for b in sorted(buddy_thresholds, reverse=True)])

plt.colorbar(heatmap, ax=ax)
plt.show()
