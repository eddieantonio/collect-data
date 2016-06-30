#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Helper functions for tests.
"""

import random

from measurements import utc_date


class N:
    """
    Normal distribution.

    You can sample from the distribution and check whether a sample is likely
    to be from the same distribution.
    """

    def __init__(self, µ=0.0, σ=1.0):
        self.mean = μ
        self.sd = σ

    def sample(self):
        """
        Return a sample from the distribution.
        """
        return random.gauss(self.mean, self.sd)

    def __contains__(self, other):
        """
        Returns True if the sample is within 2 standard deviations of the mean
        (95.45% of samples).
        """

        lower, upper = (self.mean + coeff * self.sd for coeff in (-2, 2))
        return lower <= other <= upper

    def __repr__(self):
        return "N(μ={}, σ={})".format(self.mean, self.sd)


def fabricate_data(distribution, duration=40, percent_missing=0.0):
    """
    Generates fake measurements with timestamps.

    Must provide a distribution for sampling measurements.
    """
    missing_rate = percent_missing / 100.0

    samples = []
    start_timestamp = utc_date.to_timestamp(utc_date.now())  # in milliseconds

    for second in range(duration):
        if random.uniform(0.0, 1.0) <= missing_rate:
            # Skip measurement
            continue

        timestamp = 1000 * second + start_timestamp
        # Add or subtract a few millseconds from the timestamp...
        timestamp += N(μ=0, σ=20).sample()

        samples.append((distribution.sample(), timestamp))

    return samples
