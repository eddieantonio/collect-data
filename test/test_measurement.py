#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests measurements.
"""

import sqlite3

import pytest

from measurements import Measurements, utc_date


def test_run_test():
    """
    Tests that measurements knows how to run a test with the correct
    metadata, as well as knows how to rollback when an exception is thrown
    during testing.
    """

    # Start new measurements using in memory database.
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    measure = Measurements(conn)

    config = measure.define_configuration('test_config')
    experiment = measure.define_experiment('test_experiment')

    # Ensure that these will not run tests if both the config
    # and the experiment are unknown.
    with pytest.raises(BaseException):
        measure.run_test('unknown_config', 'unknown_experiment')

    with pytest.raises(BaseException):
        measure.run_test(config, 'unknown_experiment')

    with pytest.raises(BaseException):
        measure.run_test('unknown_config', experiment)

    # Run a succesful experiment.
    with measure.run_test(config, experiment) as log:
        log.add_measurement(128.3, utc_date.now())
        log.add_measurement(128.2, utc_date.now())
        log.add_measurement(128.5, utc_date.now())
        log.add_measurement(128.2, utc_date.now())

    # Check the database for correct data.
    result = conn.execute(r'''
        SELECT configuration, experiment FROM run
    ''').fetchall()

    assert len(result) == 1, "Must have commit exactly one result"
    run, = result
    assert run['configuration'] == config
    assert run['experiment'] == experiment

    result = conn.execute(r'''
        SELECT COUNT(*) as count FROM measurement
    ''').fetchone()
    assert result['count'] == 4, "Must have exactly four measurements"

    # Run an unsuccesful experiment
    with pytest.raises(Exception):
        with measure.run_test(config, experiment) as log:
            log.add_measurement(128.3, utc_date.now())
            log.add_measurement(128.2, utc_date.now())
            log.add_measurement(128.5, utc_date.now())
            raise Exception('Arbitrary exception')
            log.add_measurement(128.2, utc_date.now())

    # Ensure the database has not changed.
    result = conn.execute(r'''
        SELECT COUNT(*) FROM run
    ''').fetchall()

    assert len(result) < 2, "Did not rollback failed test run"

    result = conn.execute(r'''
        SELECT COUNT(DISTINCT run) as count FROM measurement
    ''').fetchone()
    assert result['count'] == 1, "Must have exactly one test run"
