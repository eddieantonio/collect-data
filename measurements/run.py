#!/usr/bin/env python

import logging
import hashlib

from . import utc_date

logger = logging.getLogger(__name__)

THIRTY_ONE_BITS = 0x7FFFFFFF
THIRTY_TWO_BITS = 0xFFFFFFFF


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
        next_id = 1 + self.get_max_id()
        logger.info('Next integer id: %d', next_id)
        hashed_id = id_hash(next_id, self.configuration)

        self.cursor.execute('BEGIN TRANSACTION')
        self.cursor.execute(r'''
            INSERT INTO run(id, configuration, experiment)
            VALUES (?, ?, ?);
        ''', (hashed_id, self.configuration, self.experiment))

        self.id = hashed_id

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

    def get_max_id(self):
        """
        Gets the maximum integer ID for this particular configuration.
        """
        cursor = self.connection.cursor()
        max_id, = cursor.execute('SELECT MAX(id) FROM run WHERE configuration = ?',
                             (self.configuration,)).fetchone()
        if max_id is None:
            return 0

        assert (max_id >> 32 ==
                stable_hash(self.configuration) & THIRTY_ONE_BITS)
        return int(max_id) & THIRTY_TWO_BITS

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


def id_hash(sequence, configuration):
    """
    Creates an ID based on the hash of the configuration.
    """
    assert sequence & THIRTY_TWO_BITS == sequence
    # Get the rightmost 31-bits. 31 so that we don't exceed a 63-bit unsigned
    # integer. SQLite will freak out if we have an actual 64 bit int...
    config_hash = stable_hash(configuration) & THIRTY_ONE_BITS
    result = sequence | (config_hash << 32)
    assert result < 2**63, "Result too large"
    return result


def stable_hash(string):
    return int(hashlib.sha256(string.encode('UTF-8')).hexdigest(), 16)
