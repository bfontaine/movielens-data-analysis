# -*- coding: UTF-8 -*-

"""
This module is useful only to import ``plt`` without warning.
"""
__all__ = ["plt"]

# avoid an annoying (useless) warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import matplotlib.pyplot as plt

# silent pyflakes
if False:
    plt
