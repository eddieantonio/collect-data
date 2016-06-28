#!/usr/bin/env python

import subprocess
import multiprocessing
import datetime

from path import Path

here = Path(__file__).parent

class WattsUpMonitor:
    def __init__(self, conn):
        program = here/'fake-wattsup.py'
        assert program.exists()
        self.conn = conn

        # Start a blocking text stream
        with subprocess.Popen([program], stdout=subprocess.PIPE) as proc:
            self.proc = proc
            self.wait_for_ready()
            self.loop()

    def wait_for_ready(self):
        # Read one line
        buff = self.proc.stdout.readline()

    def loop(self):
        proc = self.proc
        while True:
            line_buffer = proc.stdout.readline()
            timestamp = utcnow()
            measurement = line_buffer.decode("ascii").strip()
            print("Got measurement:", measurement, timestamp)


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)

WattsUpMonitor(None)
