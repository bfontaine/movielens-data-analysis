# -*- coding: UTF-8 -*-

"""
This script prints some basic info about the dataset in the database
"""

import os
import sys
sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.analysis import global_ratings_graph

rg = global_ratings_graph()

print "Movies: %d" % len(rg.movies())
print "Users: %d" % len(rg.users())
