Measurements
============

Utilities for obtaining energy measurements from a Watts Up? Pro.

Setup
-----

Requires Python 3.5+ and pip (`virtualenv` recommended):

    $ pip install -r requirements.txt

Usage
-----

Create a Python script to run an experiment:

```python
from measurements import Measurements, WattsUp

# Connect to the database:
measure = Measurements('my-power.db')

# Setup the System-Under-Test to your liking.
...

# Give a name to the configuration
config = measure.define_configuration('docker')

# Give a name to the experiment
experiment = measure.define_experiment('fullstack')

# Start the Watts Up? client
wattsup = WattsUp()

# Delay until the Watts Up? is reliably delivering power measurements.
wattsup.wait_until_ready()

# Log measurements until the experiment is done.
with wattsup, measure.run_test(config, experiment) as log:
    while not experiment_done:
        watts, timestamp = wattsup.next_measurement()
        log.add_measurement(watts, timestamp)

# Teardown the System-Under-Test
...
```


Test
----

First, ensure `measurements` is importable:

```sh
pip install -e .
```

Then, simply use `setup.py`:

```sh
python setup.py test
```
