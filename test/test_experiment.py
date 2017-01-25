#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests defining and running an Experiment.
"""

import sqlite3
import random
import multiprocessing
import logging

import pytest
from path import Path

from measurements import Experiment, Measurements, WattsUp

here = Path(__file__).dirname()

def test_define_experiment():
    """
    Basic test for constructing an experiment.
    """
    @Experiment
    def some_test_name():
        "This is the description"
        pass

    assert isinstance(some_test_name, Experiment)
    assert some_test_name.name == 'some_test_name'
    assert some_test_name.description == 'This is the description'


def test_define_experiment_requires_function():
    with pytest.raises(TypeError):
        Experiment(None)


def test_can_run_experiment():
    mutable = []
    sentinel = object()

    # Side-effect of running this function: mutable will have sentinel added.
    @Experiment
    def test_experiment():
        mutable.append(sentinel)

    test_experiment.run()

    # Prove that the experimental code ran.
    assert mutable[0] is sentinel

def test_before_each():
    mutable = []
    sentinel_before = object()
    sentinel_main = object()

    # Side-effect of running this function: mutable will have sentinel added.
    @Experiment
    def test_experiment():
        mutable.append(sentinel_main)

    @test_experiment.before_each
    def before():
        mutable.append(sentinel_before)

    test_experiment.run_before_each()
    test_experiment.run()

    # Prove that the experimental code ran.
    assert len(mutable) == 2
    assert mutable[0] is sentinel_before
    assert mutable[1] is sentinel_main


def test_run_measurements():
    """
    Tests that measurements knows how to run an experiment in a different
    thread, for the amount required.
    """

    mutable = []
    sentinel = object()

    repetitions = random.randint(10, 40)

    # This is required for interprocess communications
    parent, child = multiprocessing.Pipe()

    # Side-effect of running this function: mutable will have sentinel added
    # <repetition> times IN THE PROCESS THE CODE IS RUNNING IN.
    # Note that this code should run in a different process entirely, so
    # mutable SHOULD NOT BE CHANGED!
    @Experiment
    def test_experiment():
        "Proves it's alive"
        mutable.append(sentinel)
        child.send('hello')

    # Start new measurements using in memory database.
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    measure = Measurements(conn)
    config_name = measure.define_configuration('native')

    # It should raise a type error unless it gets an Experiment
    with pytest.raises(TypeError):
        measure.run(None)

    fake_wattsup = WattsUp(here/'fake-wattsup.py',
                           args=('--no-delay',
                                 '--period', '0'))

    # Run the test experiment.
    measure.run(test_experiment,
                configuration=config_name,
                repetitions=repetitions,
                wattsup=fake_wattsup)

    received_data = []

    # Get all the data
    while parent.poll(.1):
        received_data.append(parent.recv())
    fake_wattsup.close()

    # Prove that the experimental code ran.
    assert len(received_data) == repetitions, (
        'Did not call experiment expected number of times'
    )
    assert all(item == 'hello' for item in received_data)

    # Prove that the experimental code ran in a different thread.
    assert len(mutable) == 0, (
        "Experiment code ran in this process (but shouldn't)"
    )

    # Check the database for correct data.
    result = conn.execute(r'''
        SELECT name, description FROM experiment
        WHERE name = :name
    ''', {'name': test_experiment.name}).fetchone()

    assert result, "Did not save experiment"
    assert result['description'] == test_experiment.description, (
        "Did not save experiment's description."
    )

    result = conn.execute(r'''
        SELECT :name IN (SELECT name FROM experiment) AS answer
    ''', {'name': test_experiment.name}).fetchone()
    assert result['answer'] == True, (
        'Did not save experiment name'
    )

    result = conn.execute(r'''
        SELECT COUNT(*) as count
          FROM run
         WHERE run.experiment = :name
    ''', {'name': test_experiment.name}).fetchone()
    assert result['count'] == repetitions, (
        'Did not persist expected number of runs'
    )
