#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class KahanSum:
    """
    Numerically stable summation with maximum O(√(n)) error.

    Usage:

    >>> s = KahanSum()
    >>> for x in [.1] * 10:
    ...     s += x
    ...
    >>> float(s)
    1.0

    W. Kahan's paper: http://dx.doi.org/10.1145/363707.363723
    """

    __slots__ = ('_sum', '_compensation')

    def __init__(self, initial=0.0):
        self._sum = float(initial)
        self._compensation = 0.0

    def __iadd__(self, number):
        y = float(number) - self._compensation
        t = self._sum + y
        self._compensation = (t - self._sum) - y
        self._sum = t

        return self

    def __isub__(self, number):
        self += -number
        return self

    def __float__(self):
        return self._sum

    def __int__(self):
        return int(self._sum)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
