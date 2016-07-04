#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests defining and running an Experiment.
"""

import pytest

from measurements import Experiment


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
