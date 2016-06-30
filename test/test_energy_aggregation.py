#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests that the energy aggregation works properly.
"""

from measurements.energy_aggregation import EnergyAggregation

from helpers import N, fabricate_data


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
    """
    Tests that missing samples are interpolated reasonably.
    """

    agg = EnergyAggregation()

    avg_watts = 48.1
    test_duration = 60  # seconds

    # Control for the randomness of the data:
    # By having no randomness, the samples will all be the same value,
    # hence, if no samples are missing, the calculated energy should be equal
    # to the naïve estimation of energy (power * time).
    give_or_take = 0

    # Chris Solinas found that about 4.0% of samples from the Watts Up? were
    # missing. Hence, we test that we can interpolate the missing samples.
    samples = fabricate_data(N(μ=avg_watts, σ=give_or_take),
                             duration=test_duration,
                             percent_missing=4.0)

    # Expect anywhere between 55 to 60 samples.
    assert test_duration - 5 <= len(samples) <= test_duration, (
        "Data did not have a reason amount of samples"
    )

    for sample in samples:
        agg.step(*sample)
    value = agg.finalize()

    estimated_avg_energy = avg_watts * test_duration
    estimated_sd = .5  # allow for one Joule of fudge space.

    assert value in N(μ=estimated_avg_energy, σ=estimated_sd), (
        "Estimated energy value unlikely to be from the true distribution"
    )
