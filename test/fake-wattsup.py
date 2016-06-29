#!/usr/bin/env python

"""
Emulates the output of wattsup invoked as:

    ./wattsup ttyUSB0 watts

"""

import sys
import random

from time import sleep

sleep(random.randint(2, 10))
while True:
    print("%.1f" % (random.gauss(48.1, 0.2),))
    sys.stdout.flush()
    sleep(1)
