#!/usr/bin/env python

import logging

from . import utc_date

logger = logging.getLogger(__name__)


class Run:
    """
    A run of a given experiment. Usage::

        with Measurements().run_test('docker', 'stackbench') as test:
            test += 90.5
            test += 90.4
            test += 90.5
            test += 90.5
    """

    def __init__(self, connection, configuration, experiment):
        self.connection = connection
        self.experiment = experiment
        self.configuration = configuration
        self.cursor = connection.cursor()
        self.id = None

    def __enter__(self):
        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.execute(r'''
            INSERT INTO run(configuration, experiment)
            VALUES (?, ?);
        ''', (self.configuration, self.experiment))

        self.id = self.cursor.lastrowid

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Exited successfully
        if exc_type is None:
            logger.info("Committing %r", self.id)
            self.connection.commit()
        else:
            self.connection.rollback()
            logger.error("Rolling back run %r (%s/%s)", self.id,
                         self.configuration, self.experiment,
                         exc_info=(exc_type, exc_value, traceback))

    def add_measurement(self, measurement, time=None):
        """
        Adds a measurement to the database. If a time is provided, it **MUST**
        be a datetime object in the UTC timezone.
        """

        assert isinstance(measurement, (int, float))
        if time is None:
            time = utc_date.now()
        assert utc_date.is_in_utc(time)

        self.cursor.execute(r'''
            INSERT INTO measurement (run, power, timestamp)
            VALUES (:id, :power, :timestamp)
        ''', {
            'id': self.id,
            'power': measurement,
            'timestamp': utc_date.to_timestamp(time)
        })

        return self

    def __iadd__(self, measurement):
        """
        Same as Run.add_measurement(power_in_watts).
        """
        self.add_measurement(measurement)
        return self
