#!/usr/bin/env python

import logging
import math

from collections import namedtuple

__all__ = ['EnergyAggregation']

logger = logging.getLogger(__name__)

Measurement = namedtuple('Measurement', 'watts timestamp')


class EnergyAggregation:
    """
    An SQLite aggregation function that approximates energy over time.

    Usage
    -----

    First, you must install it on the connection objects in Python::

        import sqlite3
        conn = sqlite3.connect(...)
        EnergyAggregation.install(conn)

    Then subsequent SQL queries can use it::

        SELECT energy(power, timestamp) FROM measurements GROUP BY test_id
    """

    def __init__(self):
        # This will collect samples, then in finalize, sum them, and ensure
        # any missing data is interpolated.
        self.measurements = []

    def step(self, watts, timestamp):
        # Simply accumulate samples.
        sample = Measurement(float(watts), timestamp)
        self.measurements.append(sample)

        return self

    def finalize(self):
        self.measurements.sort(key=lambda s: s.timestamp)
        return math.fsum(sample.watts for sample in self.measurements)

    @classmethod
    def install(cls, connection, name='energy'):
        connection.create_aggregate(name, 2, cls)
