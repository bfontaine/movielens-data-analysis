#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.data_import import import_data

directory = "./data"

if len(sys.argv) == 3:
    directory = sys.argv[1]
    fmt = sys.argv[2]
else:
    print "Usage:\n\t%s [<directory> <format>]\n" % sys.argv[0]
    print "Using directory='./data' and format='ml-100k'"
    fmt = "ml-100k"

print "Importing data from '%s' using format '%s'" % (directory, fmt)

import_data(directory, fmt, verbose=True)
