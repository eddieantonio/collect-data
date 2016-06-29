#!/usr/bin/env python

"""
Emulates the output of wattsup invoked as:

    ./wattsup ttyUSB0 watts

"""

import sys
import random

import argparse

from time import sleep

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--mean', type=float, default=48.1)
parser.add_argument('-s', '--std-dev', type=float, default=0.2)

parser.add_argument('-r', '--missing-rate', type=float, default=0.04)

parser.add_argument('-D', '--no-delay', dest='delay', action='store_false')

parser.add_argument('-m', '--min-delay', type=int, default=2)
parser.add_argument('-M', '--max-delay', type=int, default=10)

args = parser.parse_args()
# Inject arguments into global scope.
globals().update(args._get_kwargs())
del args, parser

assert min_delay <= max_delay
assert 0.0 <= missing_rate < 1.0

try:
    if delay:
        sleep(random.randint(min_delay, max_delay))

    while True:
        if not missing_rate or random.uniform(0.0, 1.0) > missing_rate:
            print("{:.1f}".format(random.gauss(mean, std_dev)))
            sys.stdout.flush()
        sleep(1)

except KeyboardInterrupt:
    exit(0)
