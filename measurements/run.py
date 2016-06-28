#!/usr/bin/env python

import datetime

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

    def __exit__(self, *excinfo):
        # TODO: commit ONLY IF we got the right signal
        self.connection.commit()

    def add_measurement(self, measurement, time=None):
        """
        Adds a measurement to the database. If a time is provided, it **MUST**
        be a datetime object in the UTC timezone.
        """

        assert isinstance(measurement, (int, float))
        if time is None:
            time = utcnow()
        assert time.tzinfo is datetime.timezone.utc

        self.cursor.execute(r'''
            INSERT INTO measurement (run, power, timestamp)
            VALUES (:id, :power, datetime(:time))
        ''', {'id': self.id, 'power': measurement, 'time': time})

        return self

    def __iadd__(self, measurement):
        """
        Same as Run.add_measurement(power_in_watts).
        """
        self.add_measurement(measurement)
        return self


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)
