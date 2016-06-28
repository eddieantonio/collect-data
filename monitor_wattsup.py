#!/usr/bin/env python

import subprocess
from multiprocessing import Process, Pipe
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
        self.conn.send(('ready', None))

    def loop(self):
        proc = self.proc
        conn = self.conn
        while True:
            line_buffer = proc.stdout.readline()
            timestamp = utcnow()
            measurement = line_buffer.decode("ascii").strip()
            conn.send(('data', (measurement, timestamp)))


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()

    p = Process(name='WattsUp? Monitor',
                target=WattsUpMonitor,
                args=(child_conn,))
    p.start()

    if not p.is_alive():
        print("It deaded.")
        exit(-1)

    status, payload = parent_conn.recv()
    assert status == 'ready'

    while True:
        status, payload = parent_conn.recv()
        assert status == 'data'
        measurement, timestamp = payload
        print("Got measurement:", measurement, timestamp)
