#!/usr/bin/env python

from common import *

# Define an experiment:
@Experiment
def idle():
    "Place no load on the computer"
    sleep(1)

# Run the experiment 60 times.
run('bare', idle)

# Finished with the Watts Up?
wattsup.close()
