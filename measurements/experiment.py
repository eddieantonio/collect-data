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

    To be used as a decorator:

    >>> @Experiment
    >>> def name_of_experiment():
    ...     "description of experiment"
    ...     print("hello")
    ...
    >>> name_of_experiment.name
    'name_of_experiment'
    >>> name_of_experiment.description
    'description of experiment'
    >>> name_of_experiment.run()
    """
    def __init__(self, fn):
        if not isinstance(fn, FunctionType):
            raise TypeError('Must be used as a function decorator')

        self._fn = fn
        self._before_fn = None

    @property
    def name(self):
        """
        The name of the test.
        """
        return self._fn.__name__

    @property
    def description(self):
        """
        A full description of the test.
        """
        return self._fn.__doc__

    def run(self):
        """
        Run the experiment once.
        """
        return self._fn()

    def run_before_each(self):
        """
        Run the function before the run.
        """
        if self._before_fn is not None:
            return self._before_fn()

    def before_each(self, fn):
        """
        Decorator that registers the function to run before each test run.
        """
        self._before_fn = fn
