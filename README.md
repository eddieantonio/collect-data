Measurements
============

Utilities for obtaining energy measurements from a Watts Up? Pro.

Setup
-----

Requires Python 3.5+ and pip (`virtualenv` recommended):

    $ pip install -r requirements.txt

Usage
-----

### Running experiments

Create a Python script to run an experiment:

```python
from measurements import Measurements, Experiment, WattsUp

# Connect to the database:
measure = Measurements('my-power.db')

# Setup the System-Under-Test to your liking.
...

# Give a name to the configuration
config = measure.define_configuration('docker')

# Write the experiment
@Experiment
def fullstack():
    "This experiment Apache Benchmark on the Pis..."
    ...

# Start the Watts Up? client
wattsup = WattsUp()

# Delay until the Watts Up? is reliably delivering power measurements.
wattsup.wait_until_ready()

# Run the tests 60 times with the given wattsup instance.
measure.run(idle,
            repetitions=60,
            configuration=config,
            wattsup=wattsup)

# Finished with the Wattsup.
wattsup.close()

# Teardown the System-Under-Test
...
```

### Getting energy data

Use the module as a script to estimate energy from all of the tests and
copy it into a table.

If your data is stored in an SQLite database file called `my-power.db`:

```sh
$ python -m measurments --table-name=energy my-power.db
```

Then you can access `energy` in SQLite:

```sh
$ sqlite3 -csv -header my-power.db 'SELECT * FROM energy'
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
