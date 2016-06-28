#!/usr/bin/env python

import sqlite3
import random
import logging
from time import sleep

from measurements import Measurements

logging.basicConfig(level=logging.DEBUG)


measure = Measurements(sqlite3.connect('/tmp/test'))

measure.define_configuration('native')
measure.define_configuration('docker')

measure.define_test('idle')

with measure.run_test('native', 'idle') as test_run:
    for i in range(60):
        test_run += random.gauss(70.0, 0.9)
        sleep(1)

with measure.run_test('docker', 'idle') as test_run:
    for i in range(60):
        test_run += random.gauss(70.1, 0.9)
        sleep(1)

for datum in measure.energy():
    print(datum)
