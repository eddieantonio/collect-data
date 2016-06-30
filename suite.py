#!/usr/bin/env python

import logging
from datetime import datetime

from tqdm import trange

from measurements import Measurements, WattsUp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

measure = Measurements('/tmp/test')

measure.define_configuration('native', 'Linux running on Calzone')
measure.define_experiment('idle', 'Place no load no the computer')

wattsup = WattsUp('./test/fake-wattsup.py')

logger.info('Waiting for Watts Up?...')
wattsup.wait_until_ready()
logger.info('Watts Up? ready')


def seconds_elapsed_since(time):
    return (datetime.now() - time).total_seconds()


# Repeat the test 60 times.
for _ in trange(60):
    with wattsup, measure.run_test('native', 'idle') as test_run:
        start = datetime.now()
        while seconds_elapsed_since(start) < 60.0:
            watts, timestamp = wattsup.next_measurement()
            test_run.add_measurement(watts, timestamp)

# Finished with the Wattsup.
wattsup.close()

# Print the statistics back.
for datum in measure.energy():
    print(datum)
