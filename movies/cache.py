# -*- coding: UTF-8 -*-

from collections import OrderedDict
from .db import KeyValue, init_db

__all__ = ["Cache"]

class Cache(object):
    def __init__(self, key_prefix="cache", max_items=100):
        init_db()
        # we use a prefix for the keys like we'd do with e.g. redis to ensure
        # our keys don't conflict with others.
        self.key_prefix = key_prefix

        # we also store values in a dictionary so that it's even faster to
        # access them. We use a simple LRU implementation using an ordered
        # dict. Each time a value is acceeded it's moved at its end and we
        # check the size: if we have too many cached elements we remove the
        # first ones, i.e. the oldest ones.
        self._values = OrderedDict()
        # Those are the max items we store in memory
        self.max_items = max_items

        # keep a list of the memoized0 functions
        self.memoized0 = []

    def memoize0(self, k=None):
        """
        Memoize a function with no arguments.

        Usage: ::

            @memoize0("some-key")
            def myfunc():
                return 42

            @memoize0()
            def myfunc2():
                return 37

        With no key it takes the name of the function. Provide a key if the
        function name might clash with other memoized functions in other
        modules.

        The result is cached in the underlying database.
        """
        # memoize0 is not a decorator; it's a function that returns a decorator
        # (hence ``@memoize0()`` instead of ``@memoize0``). The decorator is
        # below:
        def _decorator(fn):
            if k is None:
                # if the key is not given, use the function name
                key = "%s.fn.%s" % (self.key_prefix, fn.__name__)
            else:
                key = "%s.%s" % (self.key_prefix, k)

            # this is the re-definition of the decorated function
            def _fn():
                # get the key or None if it doesn't exist
                if key in self._values:
                    return self._hit(key)
                v = KeyValue.get_key(key)
                if v is None:
                    # if it doesn't exist, call the original function
                    v = fn()
                    # and cache the result
                    self.cache(key, v)
                else:
                    self.cache(key, v)
                # then return either the cached or computed value
                return v

            # ensure the decorator behaves like the original function
            # not to break anything
            _fn.__name__ = fn.__name__
            _fn.__doc__ = fn.__doc__

            self.memoized0.append(_fn)

            # then return the re-defined function
            return _fn

        # return the actual decorator that'll get the function it decorates as
        # its sole argument
        return _decorator

    def cache(self, key, value):
        """
        Cache a key/value pair.
        """
        KeyValue.set_key(key, value)
        if key in self._values:
            del self._values[key]
        self._values[key] = value
        self._check_size()

    def warmup(self):
        """
        Call all memoized functions to ensure their result is in the cache.
        """
        for fn in self.memoized0:
            fn()

    def destroy(self):
        """
        Destroy the cached data. The cache can still be used afterward; it's
        just empty.
        """
        KeyValue.del_key_prefix("%s." % self.key_prefix)
        self._values = {}

    def _check_size(self):
        keys = self._values.keys()
        size = len(keys)
        if self.max_items < 0:
            self.max_items = 0
        while size > self.max_items:
            del self._values[keys.pop(0)]
            size -= 1

    def _hit(self, key):
        v = self._values[key]
        if self._last_key != key:
            # force 'key' to be the last
            del self._values[key]
            self._values[key] = v
        return v

    def _last_key(self):
        if not self._values:
            return None
        # http://stackoverflow.com/a/9917213/735926
        return next(reversed(self._values))
