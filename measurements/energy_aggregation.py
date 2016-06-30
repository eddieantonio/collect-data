#!/usr/bin/env python

import logging
import math

from itertools import islice
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
        interpoloate_missing_measurements(self.measurements)
        return math.fsum(sample.watts for sample in self.measurements)

    @classmethod
    def install(cls, connection, name='energy'):
        connection.create_aggregate(name, 2, cls)


def interpoloate_missing_measurements(measurements):
    """
    Adds missing samples to the given list of measurements.

    Note: This mutates the original list!
    """

    # Sort the samples by timestamp; we will then walk through each pair of
    # chronologically consecutive samples to determine if any samples are
    # missing in between.
    measurements.sort(key=lambda s: s.timestamp)

    # Create an auxillary storage for interpolated samples as
    # to note mutate the original list during iteration.
    interpolated = []

    for first, second in pairs(measurements):
        # Determine the number of missing measurements.
        number_missing = missing_measurements(first, second)
        if number_missing == 0:
            continue

        logger.debug('%d measurement(s) missing between %f and %f (∆%f)',
                     number_missing,
                     first.timestamp,
                     second.timestamp,
                     (second.timestamp - first.timestamp))

        # Interpolation: simply copy the first measurement for as many missing
        # samples as are required.
        for i in range(number_missing):
            # Estimated time in milliseconds for this interpolated sample.
            estimated_time = 1000 * (i + 1) + first.timestamp
            sample = Measurement(watts=first.watts,
                                 timestamp=estimated_time)
            interpolated.append(sample)

    measurements.extend(interpolated)
    return measurements


def missing_measurements(first, second):
    """
    Returns the number of estimated missing measurements. Usually, this
    returns 0.
    """
    assert second.timestamp > first.timestamp
    difference = (second.timestamp - first.timestamp) / 1000.0  # in seconds

    assert round(difference) >= 1
    return round(difference) - 1


def pairs(iterable):
    """
    Yields each consecutive pair of an iterable.
    """
    return zip(iterable, islice(iterable, 1, None, 1))
