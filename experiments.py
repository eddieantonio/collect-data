#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from time import sleep

from measurements import Experiment, env


@Experiment
def idle():
    "Place no load on the computer for ten minutes."
    sleep(60 * 10)


@Experiment
def redis():
    """
    Runs the Redis benchmark. See Solinas 2015 §4.1 for the original
    parameters.
    """
    from sh import ssh,redis_benchmark

    assert 'REDIS_HOST' in env, "You forgot to define REDIS_HOST"
    redis_benchmark(h=env.REDIS_HOST, c=50, r=50000)


@Experiment
def postgresql():
    """
    Place no load on the computer for one hour.
    """
    from sh import pgbench

    assert 'POSTGRES_HOST' in env, "You forgot to define POSTGRES_HOST"
    pgbench(host=env.POSTGRES_HOST, username=env.POSTGRES_USER or 'postgres',
            client=50, transactions=1000)


@Experiment
def wordpress():
    "Wordpress stress test"

    from sh import tsung

    tsung("-f", "./carson.xml", "start")
