#!/usr/bin/env python

from sh import netperf
from common import *

# Define an experiment:
@Experiment
def netperf0():
    "Run an initial netperf stress test. Real parameters to be determined."
    netperf(H='chili')

# Run the experiment 60 times.
run('bare', netperf0)

# Finished with the Watts Up?
wattsup.close()
