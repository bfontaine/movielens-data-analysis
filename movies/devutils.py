# -*- coding: UTF-8 -*-

import time

def timeit(fn):
    """
    Decorator to print how much time a function used to complete.

    Example: ::

        @timeit
        def f(args):
            print "foo"
    """
    name = fn.__name__

    def _fn(*args, **kwargs):
        before = time.time()
        ret = fn(*args, **kwargs)
        after = time.time()

        print "[timeit] %s: %f" % (name, after - before)
        return ret

    _fn.__name__ = name
    return _fn
