#!/usr/bin/env python

import datetime

class Run:
    """
    A run of a given test. Usage:

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
        self.id = None

    def __enter__(self):
        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.execute(r'''
            INSERT INTO run(configuration, test)
            VALUES (?, ?);
        ''', (self.configuration, self.test))

        self.id = self.cursor.lastrowid

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
            INSERT INTO measurement (run, power, timestamp)
            VALUES (?, ?, ?)
        ''', (self.id, measurement, time))

        return self

    def __iadd__(self, measurement):
        self.add_measurement(measurement)
        return self


def utcnow():
    return datetime.datetime.now(tz=datetime.timezone.utc)
