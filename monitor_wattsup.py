#!/usr/bin/env python

import subprocess
from multiprocessing import Process, Pipe
import datetime

from path import Path

here = Path(__file__).parent

class WattsUpMonitor:
    def __init__(self, conn):
        self.conn = conn
        self.should_send = False

        program = here/'fake-wattsup.py'
        assert program.exists()

        # Start a blocking text stream
        with subprocess.Popen([program], stdout=subprocess.PIPE) as proc:
            self.proc = proc
            self.wait_for_ready()
            self.loop()

    def wait_for_ready(self):
        # Read one line
        buff = self.proc.stdout.readline()
        self.reply('ready')

    def loop(self):
        proc = self.proc

        while True:
            self.handle_control_message()
            self.blocking_read_measurement()

    def blocking_read_measurement(self):
        """
        Block until a measurement comes in.
        """
        line_buffer = self.proc.stdout.readline()
        timestamp = utcnow()
        measurement = line_buffer.decode("ascii").strip()
        self.send_measurement(measurement, timestamp)

    def handle_control_message(self):
        """
        Handles control messages from the client.
        """
        # Check if there's data.
        if not self.conn.poll():
            return

        message = self.conn.recv()
        if message == 'send':
            self.should_send = True
        elif message == 'stop_send':
            self.should_send = False
        else:
            raise ValueError('Unknown control message: {}'.format(message))

    def send_measurement(self, measurement, timestamp):
        if self.should_send:
            self.reply('data', (measurement, timestamp))

    def reply(self, message, payload=None):
        self.conn.send((message, payload))


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)

if __name__ == '__main__':
    parent_conn, child_conn = Pipe(duplex=True)

    p = Process(name='WattsUp? Monitor',
                target=WattsUpMonitor,
                args=(child_conn,))
    p.start()

    if not p.is_alive():
        print("It deaded.")
        exit(-1)

    # Block until ready.
    status, payload = parent_conn.recv()
    assert status == 'ready'
    # Allow sending messages.
    parent_conn.send('send')

    while True:
        status, payload = parent_conn.recv()
        assert status == 'data'
        measurement, timestamp = payload
        print("Got measurement:", measurement, timestamp)
