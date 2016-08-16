Measurements
============

Utilities for obtaining energy measurements from a Watts Up? Pro.

Setup
-----

Requires Python 3.5+ and pip (`virtualenv` recommended):

    $ pip install -r requirements.txt

Usage
-----

### Defining an experiment

Add the experiment to `experiments.py`:

```python
@Experiment
def fullstack():
    "This experiment runs Apache Benchmark on the Pis..."
    ...
```

### Running an experiments

Use `./run-experiment.py`:

```sh
$ python run-experiment.py fullstack native
```

### Getting energy data

Use the module as a script to estimate energy from all of the tests and
copy it into a table.

If your data is stored in an SQLite database file called `energy.sqlite`:

```sh
$ python -m measurments --table-name=energy energy.sqlite
```

Then you can access the `energy` table in SQLite (or use your favourite driver).

```sh
$ sqlite3 -csv -header energy.sqlite 'SELECT * FROM energy'
id,configuration,experiment,energy,started,ended,elapsed_time
2,native,idle,2640.2,1467665307981.03,1467665366137.17,58156.1420898438
3,native,idle,2685.1,1467665367137.38,1467665426296.44,59159.0610351562
4,native,idle,2684.8,1467665427299.03,1467665486454.59,59155.5590820313
5,native,idle,2729.8,1467665487458.47,1467665547626.23,60167.7639160156
6,native,idle,2684.6,1467665548628.7,1467665607794.03,59165.33203125
7,native,idle,2640.1,1467665609798.64,1467665667980.85,58182.216796875
8,native,idle,2684.4,1467665668985.92,1467665728154.63,59168.7067871094
9,native,idle,2684.8,1467665729156.64,1467665788295.35,59138.71484375
10,native,idle,2685.5,1467665789300.51,1467665848479.9,59179.3918457031
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
