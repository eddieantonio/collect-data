#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests that the energy aggregation works properly.
"""

import random
from math import sqrt

from measurements.energy_aggregation import EnergyAggregation
from measurements import utc_date

class N:
    """
    Normal distribution.
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
    Generates fake measurements, with timestamps.
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


def test_energy():
    agg = EnergyAggregation()

    avg_watts = 48.1
    give_or_take = .2
    test_duration = 60  # seconds

    samples = fabricate_data(N(μ=avg_watts, σ=give_or_take),
                             duration=test_duration,
                             percent_missing=0)

    assert len(samples) == test_duration, (
        "Must create as many samples as there are seconds"
    )

    # Add all of the generated samples to our aggregation.
    for sample in samples:
        agg.step(*sample)
    value = agg.finalize()

    estimated_avg_energy = avg_watts * test_duration
    estimated_sd = give_or_take * test_duration

    assert value in N(μ=estimated_avg_energy, σ=estimated_sd), (
        "Estimated energy value unlikely to be from the true distribution"
    )


def test_energy_missing_samples():
    agg = EnergyAggregation()

    avg_watts = 48.1
    give_or_take = .2
    test_duration = 60  # seconds

    samples = fabricate_data(N(μ=avg_watts, σ=give_or_take),
                             duration=test_duration,
                             percent_missing=4.0)

    assert test_duration - 4 <= len(samples) <= test_duration, (
        "Data did not have a reason amount of samples"
    )

    for sample in samples:
        agg.step(*sample)
    value = agg.finalize()

    estimated_avg_energy = avg_watts * test_duration
    # I don't really know what the estimated standard deviation should be
    # but let's make it grow at most O(√(|seconds|))
    estimated_sd = give_or_take * sqrt(test_duration)

    assert value in N(μ=estimated_avg_energy, σ=estimated_sd), (
        "Estimated energy value unlikely to be from the true distribution"
    )
