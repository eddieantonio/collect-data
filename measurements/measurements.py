#!/usr/bin/env python

import sqlite3
import logging

from path import Path

from .run import Run

logger = logging.getLogger(__name__)
here = Path(__file__).parent


class Measurements:
    """
    Interface to measurements stored in an SQLite3 database.
    """

    def __init__(self, conn=None):
        if conn is None:
            logger.warn("Using transient in-memory SQL database.")
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = conn

        location = here/'schema.sql'
        logger.debug('Loading schema from {}'.format(location))
        self._source(location)

    def run_test(self, configuration, experiment):
        """
        Start a run of an experiment.

        To be used in a context manager::

            m = Measurements(connection)
            with m.run_test('docker', 'idle') as log:
                log += power_in_watts
        """
        assert self._configuration_exists(configuration)
        assert self._experiment_exists(experiment)
        return Run(self.conn, configuration, experiment)

    def define_configuration(self, name, description=None):
        """
        Ensures a configuration with the given name exists in the database.
        """

        self.conn.execute(r'''
            INSERT OR REPLACE INTO configuration(name, description)
            VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()

        return self

    def define_experiment(self, name, description=None):
        """
        Ensures an experiment with the given name exists in the database.
        """

        self.conn.execute(r'''
            INSERT OR REPLACE INTO experiment(name, description)
            VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()

        return self

    def energy(self):
        """
        Yields the energy per each experiment in the database.
        """

        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT id, configuration, experiment, total(power) as energy
              FROM measurement JOIN run on run.id = measurement.run
            GROUP BY id
        ''')

        return cursor.fetchall()

    def _source(self, name):
        with open(str(name)) as sqlfile:
            self.conn.executescript(sqlfile.read())
        return self

    def _experiment_exists(self, test_name):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT 1 FROM experiment WHERE name = ?
        ''', (test_name,))
        return cursor.fetchone() is not None

    def _configuration_exists(self, config_name):
        cursor = self.conn.cursor()
        cursor.execute(r'''
            SELECT 1 FROM configuration WHERE name = ?
        ''', (config_name,))
        return cursor.fetchone() is not None


if __name__ in ('__main__', '__console__'):
    # BPython console
    logging.basicConfig()
    m = Measurements()
    for measurement in m.energy():
        print(energy)
