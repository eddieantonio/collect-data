#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests defining and running an Experiment.
"""

import multiprocessing

from types import FunctionType

__all__ = ['Experiment']


class Experiment:
    """
    Defines an experiment to be used with measurements.
    """
    def __init__(self, fn):
        if not isinstance(fn, FunctionType):
            raise TypeError('Must be used as a function decorator')

        self._fn = fn

    @property
    def name(self):
        return self._fn.__name__

    def run(self):
        return self._fn()
