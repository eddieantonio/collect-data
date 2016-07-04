#!/usr/bin/env python

import logging
from time import sleep
from tqdm import trange

from measurements import Measurements, Experiment, WattsUp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

measure = Measurements('/tmp/test')

measure.define_configuration('native', 'Linux running on Calzone')

# Replace this with the actual WattsUp application.
wattsup = WattsUp('./test/fake-wattsup.py', args=('--no-delay',))

logger.info('Waiting for Watts Up?...')
wattsup.wait_until_ready()
logger.info('Watts Up? ready')


# Define an experiment:
@Experiment
def idle():
    "Place no load on the computer"
    sleep(60)

# Run the tests with the given wattsup instance.
measure.run(idle,
            configuration='native',
            repetitions=60,
            range=trange,
            wattsup=wattsup)

# Finished with the Wattsup.
wattsup.close()

# Print the statistics back.
for datum in measure.energy():
    print(datum)
