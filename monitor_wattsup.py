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
            # TODO: Add termination control message?
            raise ValueError('Unknown control message: {}'.format(message))

    def send_measurement(self, measurement, timestamp):
        if self.should_send:
            self.reply('data', (measurement, timestamp))

    def reply(self, message, payload=None):
        self.conn.send((message, payload))


class WattsUp:
    """
    High-level interface to the WattsUp?

    Usage::

        with WattsUp() as client:
            measurement, timestamp = client.next_measurement()
            print("Got measurement:", measurement, timestamp)
            # Take as many measurements as necessary.

    """

    def __init__(self):
        self._conn, child_conn = Pipe(duplex=True)

        proc = Process(name='WattsUp? Monitor',
                       target=WattsUpMonitor,
                       args=(child_conn,))
        proc.start()
        assert proc.is_alive()

        self._proc = proc
        self._wait_until_ready()

    def close(self):
        self._conn.close()
        # This might block... indefinitely.
        self._proc.join()

    def __enter__(self):
        # Allow sending messages.
        self._send('send')
        return self

    def __exit__(self, *exception_info):
        # Stop sending messages
        self._send('stop_send')

    def next_measurement(self):
        """
        Blocks until the next measurement is available and returns it.
        """

        status, payload = self._recv()
        assert status == 'data'
        measurement, timestamp = payload
        return measurement, timestamp

    def _wait_until_ready(self):
        # Block until ready.
        status, payload = self._recv()
        assert status == 'ready'

    def _send(self, message):
        return self._conn.send(message)

    def _recv(self):
        return self._conn.recv()


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


if __name__ == '__main__':
    with WattsUp() as client:
        while True:
            measurement, timestamp = client.next_measurement()
            print("Got measurement:", measurement, timestamp)
