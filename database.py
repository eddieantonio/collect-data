#!/usr/bin/env python

import sqlite3
import logging
import datetime

import path

logger = logging.getLogger(__name__)

here = path.from_string(__file__).parent

class Run:
    """
    A run of a given test.

    >>> with measurements().run_test('docker', 'stackbench') as test:
    ...     test += 90.5
    ...     test += 90.4
    ...     test += 90.5
    ...     test += 90.5
    """
    def __init__(self, connection, configuration, test):
        self.connection = connection
        self.test = test
        self.configuration = configuration
        self.cursor = connection.cursor()

    def __enter__(self):
        self.cursor.execute('BEGIN TRANSACTION')
        return self

    def __exit__(self, *excinfo):
        # TODO: commit ONLY IF we got the right signal
        self.connection.commit()

    def add_measurement(self, measurement, time=None):
        """
        Adds a measurement to the database. If a time is provided, it MUST be
        in the UTC timezone.
        """

        assert isinstance(measurement, (int, float))
        if time is None:
            time = utcnow()
        assert time.tzinfo is datetime.timezone.utc

        self.cursor.execute(r'''
            INSERT INTO measurement (configuration, test, power, time)
            VALUES (?, ?, ?, ?)
        ''', (self.configuration, self.test, measurement))

        return self

    def __iadd__(self, measurement):
        self.add_measurement(measurement)
        return self


class Measurements:
    def __init__(self, conn=None):
        if conn is None:
            logger.warn("Using transient in-memory SQL database.")
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = conn

        self._source(here/'schema.sql')
        self._source(here/'sample.sql')

    def run_test(self, configuration, test):
        assert self._configuration_exists(configuration)
        assert self._test_exists(test)
        return Run(self.conn, configuration, test)

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


def utcnow():
    return datetime.datetime.now(tz=datetime.timezone.utc)


if __name__ in ('__main__', '__console__'):
    logging.basicConfig()
    # BPython console
    c = Connection()
    for measurement in c.energy():
        print(energy)
