# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import json

# avoid an annoying (useless) warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import matplotlib.pyplot as plt


distribs = []
max_freq = 0
max_count = 0

gt_counts = set()
buddy_thresholds = set()

#filename = "distributions-movies.jsons"
filename = "distributions-people.jsons"

with open(filename) as f:
    for line in f:
        d = json.loads(line)
        distribs.append(d)

        max_count = max(max_count, len(d["distribution"]))
        max_freq = max(max_freq, *d["distribution"])

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

for i, d in enumerate(distribs):
    gtc = d["gt_count"]
    bt = d["buddy_threshold"]
    arr = d["distribution"]

    # TODO use logarithmic bins
    # http://stackoverflow.com/a/6856155/735926

    plt.subplot(nrows, ncols, i+1)
    # x1, x2, y1, y2
    plt.axis((1, max_count, 0, max_freq))
    plt.bar(range(len(arr)), arr, width=1)

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
