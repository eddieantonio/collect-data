#!/usr/bin/env python

from time import sleep
from tqdm import trange

from measurements import Measurements, Experiment, WattsUp


measure = Measurements('energy.sqlite')


# Start the Watts Up?
wattsup = WattsUp(executable='/home/pi/wattsup/wattsup', args=['ttyUSB0', 'watts'])
wattsup.wait_until_ready()


# Define an experiment:
@Experiment
def idle():
    "Place no load on the computer"
    sleep(60)

config = measure.define_configuration('bare', 'Linux running on Chili (only sshd).')

# Run the experiment 60 times.
measure.run(idle,
            configuration=config,
            repetitions=60,
            range=trange,
            wattsup=wattsup)


# Finished with the Watts Up?
wattsup.close()
