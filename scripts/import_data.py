#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

sys.path.insert(0, '%s/..' % os.path.dirname(__file__))

from movies.data_import import import_data
import_data("./data", verbose=True)
