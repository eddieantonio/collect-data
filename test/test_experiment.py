#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests defining and running an Experiment.
"""

import sqlite3
import random

import pytest

from measurements import Experiment, Measurements


def test_define_experiment():

    @Experiment
    def some_test_name():
        pass

    assert isinstance(some_test_name, Experiment)
    assert some_test_name.name == 'some_test_name'


def test_define_experiment_requires_function():
    with pytest.raises(TypeError):
        Experiment(None)


def test_can_run_experiment():
    mutable = []
    sentinel = object()

    # Side-effect of running this function:
    # mutable will have sentinel added.
    @Experiment
    def test_experiment():
        mutable.append(sentinel)

    test_experiment.run()

    # Prove that the experimental code ran.
    assert mutable[0] is sentinel


def test_run_measurements():
    mutable = []
    sentinel = object()

    repetitions = random.randint(10, 40)

    # Side-effect of running this function:
    # mutable will have sentinel added <repetition> times
    @Experiment
    def test_experiment():
        mutable.append(sentinel)

    # Start new measurements using in memory database.
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    measure = Measurements(conn)

    # It should raise a type error unless it gets an Experiment
    with pytest.raises(TypeError):
        measure.run(None)

    # Run the test experiment.
    measure.run(test_experiment,
                configuration='native',
                repetitions=repetitions)

    # Prove that the experimental code ran.
    assert len(mutable) == repetitions, (
        'Did not call experiment expected number of times'
    )
    assert all(item is sentinel for item in mutable)

    result = conn.execute(r'''
        SELECT :name IN (SELECT name FROM experiment) AS answer
    ''', {'name': test_experiment.name}).fetchone()
    assert result['answer'] == True, (
        'Did not save experiment name'
    )

    # Check the database for correct data.
    result = conn.execute(r'''
        SELECT COUNT(*) as count
          FROM run
         WHERE run.experiment = :name
    ''', {'name': test_experiment.name}).fetchone()
    assert result['count'] == repetitions, (
        'Did not persist expected number of runs'
    )
