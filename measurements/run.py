#!/usr/bin/env python

import logging
import uuid

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
        next_id = uuid.uuid1().hex
        logger.info('Next run id: %s', next_id)

        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.execute(r'''
            INSERT INTO run(id, configuration, experiment)
            VALUES (?, ?, ?);
        ''', (next_id, self.configuration, self.experiment))

        self.id = next_id

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            # Exited successfully
            logger.info("Committing %s", self.id)
            self.connection.commit()
        else:
            # Something bad happened! Roll back.
            self.connection.rollback()
            logger.error("Rolling back run %s (%s/%s)", self.id,
                         self.configuration, self.experiment,
                         exc_info=(exc_type, exc_value, traceback))
        self.id = None

    def add_measurement(self, measurement, time=None):
        """
        Add a single power measurement (in watts) to the current run.

        If time is provided, it **MUST** be a datetime object in the UTC
        timezone.
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
