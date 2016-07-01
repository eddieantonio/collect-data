#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Given an existing database of power measurements, creates a new table
with the estimated energy used by each test run. The table generated is, by
default, named `energy` (overridable by using the `--table-name` argument).
The following is the table's schema.

CREATE TABLE energy(
    id              INT,  -- Unique test run ID.
    configuration   TEXT, -- The hardware configuration for the experiment
    experiment      TEXT, -- The name of the experiment
    energy          REAL, -- Estimated energy in Joules
    duration        REAL  -- Duration in milliseconds
)

You may then produce a CSV file suitable for import into R as such:

    $ sqlite3 my-db.sqlite -csv -header 'SELECT * FROM energy' > energy.csv

Alternatively, you may use RSQLite:

    $ R
    > library(DBI)
    > library(RSQLite)
    > conn <- dbConnect(RSQLite::SQLite(), "my-db.sqlite")
    > energy <- dbGetQuery(conn, "SELECT * FROM energy")
    > linux <- energy[energy$configuration == 'native',]
    > docker <- energy[energy$configuration == 'docker',]

"""

import sys
import logging
import argparse

from path import Path

# Dumb things to get the import to work.
sys.path.insert(0, Path(__file__).abspath().dirname().parent)
from measurements import Measurements


logging.basicConfig(level=logging.DEBUG)


class UsageError(ValueError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('database')

    parser.add_argument('-t', '--table-name', default='energy')
    parser.add_argument('-@', '--delete-existing', action='store_true')

    return parser.parse_args()


def main(database=':memory:', table_name='energy', delete_existing=False):
    if database != ':memory:':
        database = Path(database)
        if not database.exists():
            raise UsageError('Database file does not exist: ' + database)

    measure = Measurements(database)
    measure.energy(create_table=table_name, drop_existing=True)

    return 0


if __name__ == '__main__':
    args = parse_args()
    try:
        status = main(**dict(args._get_kwargs()))
    except UsageError as error:
        print(error.args[0], file=sys.stderr)
        exit(-1)
    else:
        exit(status)
