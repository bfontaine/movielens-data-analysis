# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import json
import numpy as np

# avoid an annoying (useless) warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import matplotlib.pyplot as plt


def unpack_distrib(d):
    """
    Return the original data from a given distribution, e.g.: ::

        >>> unpack_distrib([0, 3, 2, 0, 1])
        [1, 1, 1, 2, 2, 4]
    """
    data = []
    for i, n in enumerate(d):
        if n:
            data += [i] * n

    return data


distribs = []

gt_counts = set()
buddy_thresholds = set()

#filename = "distributions-movies.jsons"
filename = "distributions-people.jsons"

with open(filename) as f:
    for line in f:
        d = json.loads(line)
        distribs.append(d)

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

logspace = np.logspace(0, 10, base=2)

for i, d in enumerate(distribs):
    gtc = d["gt_count"]
    bt = d["buddy_threshold"]
    arr = unpack_distrib(d["distribution"])

    ax = plt.subplot(nrows, ncols, i+1)
    plt.hist(arr, bins=logspace)
    ax.set_yscale("log", basey=2, nonposy="clip")
    ax.set_xscale("log", basex=2, nonposx="clip")

    # remove the X ticks labels unless we're at the bottom
    if i < last_row_index:
        locs, _ = plt.xticks()
        plt.xticks(locs, [])
    else:
        plt.xlabel("%d" % gtc)

    # remove the Y ticks labels unless we're on the left
    if i % nrows != 0:
        locs, _ = plt.yticks()
        plt.yticks(locs, [])
    else:
        plt.ylabel("%.4f" % bt)

plt.show()
