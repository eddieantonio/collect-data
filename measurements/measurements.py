#!/usr/bin/env python

import sqlite3
import re
import logging
import multiprocessing

from time import sleep

from path import Path

from .run import Run
from .energy_aggregation import EnergyAggregation
from .experiment import Experiment
from .wattsup import WattsUp

logger = logging.getLogger(__name__)
here = Path(__file__).parent


class Measurements:
    """
    Interface to measurements stored in an SQLite3 database.
    """

    def __init__(self, conn=None):
        if conn is None:
            logger.warn("Using transient in-memory SQLite database.")
            self.conn = sqlite3.connect(':memory:')
        elif isinstance(conn, sqlite3.Connection):
            logger.info("Using provided SQLite connection")
            self.conn = conn
        elif isinstance(conn, str):
            logger.info("Using SQLite database file: %r", conn)
            self.conn = sqlite3.connect(conn)

        location = here/'schema.sql'
        logger.debug('Loading schema from {}'.format(location))
        self._source(location)

        logger.debug('Installing energy aggregation')
        EnergyAggregation.install(self.conn)

    def run(self, experiment,
            # TODO: add per-test timeout?
            configuration=None,
            repetitions=1,
            sleep_time=0,
            range=range,  # Allow for dependency injecting tqdm.trange()
            wattsup=None,
            write_back_energy=False):
        """
        Runs an experiment on a given configuration. May run the experiment
        for as many repetitions as are required.
        """

        if not isinstance(experiment, Experiment):
            raise TypeError('Must pass an experiment object')

        # Vivify the experiment name.
        self.define_experiment(experiment.name, experiment.description)

        # Create and ready the WattsUp instance if not given.
        if wattsup is None:
            wattsup = WattsUp()
        wattsup.wait_until_ready()

        # Run the experiment
        assert repetitions >= 1
        for _ in range(repetitions):
            process = multiprocessing.Process(target=experiment.run)

            # Do a single run.
            with self.run_test(configuration, experiment.name) as log:
                process.start()

                # Enable logging from the Watts Up?
                with wattsup:
                    while process.is_alive():
                        watts, time = wattsup.next_measurement()
                        log.add_measurement(watts, time)

                # Presumably, the process has ended.
                process.join()

                if process.exitcode != 0:
                    raise RuntimeError('Experiment exited unsuccesfully:' +
                                       str(process.exitcode))

            # Write back the energy instantly.
            if write_back_energy:
                log.write_back_energy()

            # Give the machine an arbitrary amount of idle time before the next run.
            sleep(sleep_time)

        # The experiment should be done.
        logger.debug('Experiment complete')

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

        return name

    def define_experiment(self, name, description=None):
        """
        Ensures an experiment with the given name exists in the database.
        """

        self.conn.execute(r'''
            INSERT OR REPLACE INTO experiment(name, description)
            VALUES (?, ?)
        ''', (name, description))
        self.conn.commit()

        return name

    def energy(self, create_table=None, drop_existing=False):
        """
        Yields the energy per each experiment in the database.

        If `create_table` is a string, this also inserts the data into a table
        with the given name. Additionally, if `drop_existing` is True, then
        any table with the name given in `create_table`.

        """

        query =(r'''
            SELECT run.id as id,
                   configuration, experiment,
                   energy(power, timestamp) as energy,
                   MIN(timestamp) as started,
                   MAX(timestamp) as ended,
                   (MAX(timestamp) - MIN(timestamp))
                     as elapsed_time -- in milliseconds
              FROM measurement JOIN run ON measurement.run = run.id
          GROUP BY run.id;
        ''')

        if create_table:
            return self._create_table(query, create_table, drop_existing)

        cursor = self.conn.cursor()
        cursor.execute(query)

        return cursor.fetchall()

    def _source(self, name):
        with open(str(name)) as sqlfile:
            self.conn.executescript(sqlfile.read())
        return self

    def _create_table(self, query, name, drop_existing):
        # Ensure we get a valid table name.
        if not re.match('^(?!sqlite_)[A-Za-z0-9_]+$', name):
            raise ValueError('Invalid table name: ' + name)

        command = ''

        if drop_existing:
            command += 'DROP TABLE IF EXISTS {name};\n'.format(name=name)

        command += (r'''
            CREATE TABLE {name} AS {query}
        ''').format(name=name, query=query)

        logger.debug('Executing:\n%s', command)

        self.conn.executescript(command)
        self.conn.commit()

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
