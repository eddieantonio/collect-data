#!/usr/bin/env python

import logging

from .kahan_sum import KahanSum

logger = logging.getLogger(__name__)

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
        self.sum = KahanSum()

    def step(self, *args):
        logging.debug('energy%r', args)
        value, *_ = args
        self.sum += float(value)

    def finalize(self):
        return float(self.sum)

    @classmethod
    def install(cls, connection, name='energy'):
        connection.create_aggregate(name, 2, cls)
