# -*- coding: UTF-8 -*-

import json
from movies.analysis import RatingsGraph
from movies import insights

rg = RatingsGraph()

# deciles
buddy_thresholds = [
    0,
    0.0036363636363636364,
    0.0063916104885135619,
    0.010060980215131566,
    0.014521552144421941,
    0.020288483446378184,
    0.028861602160590777,
    0.041990776417902477,
    0.065420561190010773,
    0.1234828753671024,
]

gt_counts = range(1, 10+1)

def mk_results(output, movies=False):
    with open(output, "w") as f:
        for buddy_threshold in buddy_thresholds:
            for gt_count in gt_counts:
                d = insights.gatekeepers_distribution(rg,
                        gatekeepers_count=gt_count,
                        buddy_threshold=buddy_threshold,
                        movies=movies)

                res = {
                    "buddy_threshold": buddy_threshold,
                    "gt_count": gt_count,
                    "distribution": d,
                }

                print "gt_count: %2d / threshold: %.4f / mx: %3d" % (
                        gt_count, buddy_threshold, len(d))
                f.write("%s\n" % json.dumps(res))

mk_results("distributions-people.jsons")
mk_results("distributions-movies.jsons", True)
