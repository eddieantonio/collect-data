#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Integration tests for the EnergyAggregation.
"""

import sqlite3

from measurements import Measurements, utc_date
from measurements.energy_aggregation import EnergyAggregation

from helpers import N, fabricate_data


def test_energy_aggregation():
    """
    Tests ingesting realistic measurements, and then using the
    EnergyAggregation function in SQLite to return energy.
    """

    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    measure = Measurements(conn)
    config = measure.define_configuration('native')
    experiment = measure.define_experiment('idle')

    avg_watts = 48.7
    test_duration = 120

    # Run a fake experiment:
    distribution = N(μ=avg_watts, σ=.1)
    samples = fabricate_data(distribution, duration=test_duration)
    assert len(samples) == test_duration

    # Log the measurements:
    with measure.run_test(config, experiment) as log:
        for watts, timestamp in samples:
            log.add_measurement(watts, utc_date.from_timestamp(timestamp))

    # Now every measurement should be in the database.
    result = conn.execute(r'''
        SELECT COUNT(*) as count,
               AVG(power) as average,
               (MAX(timestamp) - MIN(timestamp)) / 1000 as duration
         FROM measurement
    ''').fetchone()
    assert result['count'] == test_duration, (
        "Not all samples found in the database"
    )
    # What **should** be done is a t-test, but simply comparing the mean
    # should be fine.
    assert result['average'] in distribution, (
        "Power samples are not from the original distribution!"
    )
    assert result['duration'] in N(μ=test_duration, σ=2), (
        "Unexpected test duration."
    )

    # Ensure this is the only test in the database.
    result = conn.execute('SELECT COUNT(DISTINCT run) as runs '
                          '  FROM measurement').fetchone()
    assert result['runs'] == 1, (
        "There was not exactly one test run in the database!"
    )

    # The power data looks sane. We can now attempt to estimate the energy.
    EnergyAggregation.install(conn)

    # The holy grail query that should be installed as a view.
    result = conn.execute(r'''
        SELECT configuration, experiment, energy(power, timestamp) as energy
          FROM measurement JOIN run on measurement.run = run.id
      GROUP BY run.id
    ''').fetchone()

    expected_energy = avg_watts * test_duration
    wiggle_room =  2.5  # expect around five Joules of fudge space

    assert result['configuration'] == config
    assert result['experiment'] == experiment
    assert result['energy'] in N(µ=expected_energy, σ=wiggle_room)
