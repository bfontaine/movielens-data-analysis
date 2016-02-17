#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np

# copied from the cancerologues project
def correlation(l1, l2):
    """
    Return the correlation coefficient between two lists

    >>> correlation([1, 2, 3, 4], [2, 4, 6, 7])
    0.9897782665572893
    """
    return np.corrcoef(l1, l2).tolist()[0][1]
