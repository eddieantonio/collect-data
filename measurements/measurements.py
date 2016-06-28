#!/usr/bin/env python

import sqlite3
import logging

from . import path
from .run import Run

logger = logging.getLogger(__name__)
here = path.from_string(__file__).parent


class Measurements:
    def __init__(self, conn=None):
        if conn is None:
            logger.warn("Using transient in-memory SQL database.")
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = conn

        self._source(here/'schema.sql')

    def run_test(self, configuration, test):
        """
        Start the run of a test.
        """
        assert self._configuration_exists(configuration)
        assert self._test_exists(test)
        return Run(self.conn, configuration, test)

    def define_test(self, name, description=None):
        self.conn.execute(r'''
            INSERT OR REPLACE INTO test(name, description)
            VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()

        return self

    def define_configuration(self, name, description=None):
        self.conn.execute(r'''
            INSERT OR REPLACE INTO configuration(name, description)
            VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()

        return self

    def energy(self):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT id, configuration, test, total(power) as energy
              FROM measurement JOIN run on run.id = measurement.run
            GROUP BY id
        ''')

        return cursor.fetchall()

    def _source(self, name):
        with open(str(name)) as sqlfile:
            self.conn.executescript(sqlfile.read())
        return self

    def _test_exists(self, test_name):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT 1 FROM test WHERE name = ?
        ''', (test_name,))
        return cursor.fetchone() is not None

    def _configuration_exists(self, config_name):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT 1 FROM configuration WHERE name = ?
        ''', (config_name,))
        return cursor.fetchone() is not None


if __name__ in ('__main__', '__console__'):
    logging.basicConfig()
    # BPython console
    m = Measurements()
    for measurement in m.energy():
        print(energy)