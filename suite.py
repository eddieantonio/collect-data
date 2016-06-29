#!/usr/bin/env python

import logging
from tqdm import trange

from measurements import Measurements, WattsUp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

measure = Measurements('/tmp/test')

measure.define_configuration('native', 'Linux running on Calzone')
measure.define_experiment('idle', 'Place no load no the computer')

logger.info('Waiting for Watts Up?...')
wattsup = WattsUp('./test/fake-wattsup.py').wait_until_ready()
logger.info('Watts Up? ready')

# Repeat the test 60 times.
for _ in trange(60):
    with wattsup, measure.run_test('native', 'idle') as test_run:
        for i in range(60):
            watts, timestamp = wattsup.next_measurement()
            test_run.add_measurement(watts, timestamp)

wattsup.close()

# Print the statistics back.
for datum in measure.energy():
    print(datum)
