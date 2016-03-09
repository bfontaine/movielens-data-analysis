# -*- coding: UTF-8 -*-

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

import json

import networkx as nx

from movies.analysis import RatingsGraph
from movies import insights

rg = RatingsGraph()
all_buddies = rg.users_buddies(0)

# deciles
buddy_thresholds = [
    0.0024,
    0.0171,
    0.0276,
    0.0385,
    0.0504,
    0.0638,
    0.0804,
    0.1016,
    0.1311,
    0.1769,
    0.6897,
]

gt_counts = range(1, 10+1)

# We use this to compute each filtered projected graph from the non-filtered
# one instead of re-computing each from scratch
def make_buddies(threshold):
    g = nx.Graph()

    for u1, us in all_buddies.edge.items():
        for u2, opts in us.items():
            if opts["score"] >= threshold:
                g.add_edge(u1, u2, opts)

    return g


def mk_distrib(buddies, gt_count, buddy_threshold, **kw):
    print "Running with gt_count: %2d / threshold: %.4f" % (
            gt_count, buddy_threshold)

    d = insights.gatekeepers_distribution(rg,
            gatekeepers_count=gt_count,
            buddies=buddies,
            **kw)
            #keep_ids=True)

    res = {
        "buddy_threshold": buddy_threshold,
        "gt_count": gt_count,
        "distribution": d,
    }

    return "%s\n" % json.dumps(res)

def mk_results(output, **kw):
    with open(output, "w") as f:
        for buddy_threshold in buddy_thresholds:
            buddies = make_buddies(buddy_threshold)

            for gt_count in gt_counts:
                f.write(mk_distrib(buddies, gt_count, buddy_threshold, **kw))

#mk_results("distributions-people-ids.jsons")
mk_results("distributions-people-jaccard.jsons", keep_ids=False)
