#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Runs an experiment.
"""


import argparse
from contextlib import closing

from tqdm import trange
from blessings import Terminal

import experiments
from measurements import Measurements, Experiment, WattsUp


assert __name__ == '__main__'

VALID_EXPERIMENTS = [name for name, thing in vars(experiments).items()
                     if isinstance(thing, Experiment)]

CONFIGURATIONS = {
    'native': 'Apps running on one Linux machine natively',
    'multidocker': 'Apps running across several Docker containers'
}

# Setup argument parsing.
parser = argparse.ArgumentParser(description="Run an experiment")
parser.add_argument('experiment_name', metavar='EXPERIMENT',
                    choices=VALID_EXPERIMENTS,
                    help=('The name of the experiment to run. Choose one of ' +
                          ', '.join(VALID_EXPERIMENTS)))
parser.add_argument('configuration_name', metavar='CONFIGURATION',
                    choices=CONFIGURATIONS,
                    help=('The name of the machine configuration. Choose one of ' +
                          ', '.join(CONFIGURATIONS.keys())))
parser.add_argument('--fake-wattsup', action='store_true',
                    help='Use the fake wattsup instead.')

# Inject parsed arguments into global scope.
args = parser.parse_args()
globals().update(args._get_kwargs())
del args, parser


# Set up other random things.
t = Terminal()

# Load the measurements.
measure = Measurements('energy.sqlite')
# Vivify the experiment and the configuration.
config = measure.define_configuration(configuration_name,
                                      CONFIGURATIONS[configuration_name])
experiment = getattr(experiments, experiment_name)

# Start the Watts Up?
if fake_wattsup:
    wattsup = WattsUp('./test/fake-wattsup.py', args=('--no-delay',))
else:
    # TODO: unhardcode path
    wattsup = WattsUp(executable='/home/pi/wattsup/wattsup', args=['ttyUSB0', 'watts'])

print(t.yellow("Waiting for the Watts Up? to start..."))
wattsup.wait_until_ready()
print(t.bold_green("Watts Up? ready!"))

# TODO: Create command line argument for repetitions?
repetitions = 60
# TODO: Create command line argument for sleep_time?
sleep_time = 120

print("Running '{t.green}{experiment_name}{t.normal}' "
      "{t.red}{repetitions}{t.normal} times "
      "on {t.blue}{configuration_name}{t.normal}"
      .format(**vars()))


# Run the experiment!
with closing(wattsup):
    measure.run(experiment,
                configuration=config,
                repetitions=repetitions,
                sleep_time=sleep_time,
                range=trange,
                wattsup=wattsup)
