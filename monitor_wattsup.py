#!/usr/bin/env python

import subprocess
import multiprocessing
import datetime

from path import Path

here = Path(__file__).parent

def start(conn):
    program = here/'fake-wattsup.py'
    assert program.exists()

    # Start a blocking text stream
    with subprocess.Popen([program], stdout=subprocess.PIPE) as proc:
        print("Process open")

        # Read one line
        buff = proc.stdout.readline()
        print("Ready!")

        while True:
            buff = proc.stdout.readline()
            timestamp = utcnow()
            measurement = buff.decode("ascii").strip()
            print("Got measurement:", measurement, timestamp)


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)

start(None)
