#!/usr/bin/env python

import sqlite3
import logging

from collections import namedtuple


memory = lambda: sqlite3.connect(':memory:')

class Energy(namedtuple('Energy', 'id configuration test energy')):
    def __str__(self):
        return ("{configuration}/{test} #{id}: "
                "{energy:.1f}J".format(**self._asdict()))


class KahanSum:
    """
    Implements Kahan summation to compute arithmetic mean.

    >>> KahanSum().step(0).step(0).step(0).finalize()
    0.0
    >>> KahanSum().step(1e8).step(1.0).step(-1e8).finalize()
    1.0

    """
    def __init__(self):
        self.summation = 0.0
        self.compensation = 0.0

    def step(self, raw_value):
        value = float(raw_value)
        y = value - self.compensation
        t = self.summation + y

        self.compensation = (t - self.summation) - y
        self.summation = t

        return self

    def finalize(self):
        return self.summation


class Connection():
    def __init__(self, conn=None, name=':memory:'):
        self.conn = conn if conn is not None else sqlite3.connect(name)
        self.install_functions()
        self.conn.row_factory = lambda cursor, row: Energy(*row)

    def source(self, name):
        with open(name) as sqlfile:
            self.conn.executescript(sqlfile.read())
        return self

    def install_functions(self):
        self.conn.create_aggregate('ksum', 1, KahanSum)

    def query(self):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT id, configuration, test, total(power) as energy
              FROM measurement JOIN run on run.id = measurement.run
            GROUP BY id
        ''')

        return cursor.fetchall()

if __name__ in ('__main__', '__console__'):
    # BPython console
    c = Connection().source("./schema.sql").source("./sample.sql")
    for datum in c.query():
        print(datum)
