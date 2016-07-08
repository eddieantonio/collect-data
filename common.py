#!/usr/bin/env python

from time import sleep

from tqdm import trange
from blessings import Terminal

from measurements import Measurements, Experiment, WattsUp


measure = Measurements('energy.sqlite')
configs = set([
    measure.define_configuration('bare', 'Linux running on Chili (only sshd).'),
    measure.define_configuration('native', 'Apps running on Linux natively'),
    measure.define_configuration('docker', 'Apps running in one Docker container (VM-style)'),
    measure.define_configuration('multidocker', 'Apps running in several Docker containers')
])

t = Terminal()

# Start the Watts Up?
print(t.yellow("Waiting for the Watts Up? to start..."))
wattsup = WattsUp(executable='/home/pi/wattsup/wattsup', args=['ttyUSB0', 'watts'])
wattsup.wait_until_ready()
print(t.bold_green("Watts Up? ready!"))

def run(config, experiment, repetitions=40):
    assert config in configs
    # Run the experiment 60 times.
    measure.run(experiment, configuration=config,
    	    repetitions=60,
    	    range=trange,
    	    wattsup=wattsup)

# Remember to call wattsup.close()!
