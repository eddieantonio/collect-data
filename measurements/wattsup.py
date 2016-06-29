#!/usr/bin/env python

"""
High-level interface to the WattsUp? Pro power monitor.

Usage::

    from measurements.wattsup import WattsUp

    with WattsUp('/path/to/wattsup') as client:
        measurement, timestamp = client.next_measurement()
        print("Got measurement:", measurement, timestamp)
        # Take as many measurements as necessary.
"""

import subprocess
from multiprocessing import Process, Pipe
import datetime

from path import Path
from sh import which

here = Path(__file__).parent


class WattsUpMonitor:
    def __init__(self, conn, executable=None):
        self.conn = conn
        self.should_send = False

        # Start a blocking text stream
        with subprocess.Popen([executable], stdout=subprocess.PIPE) as proc:
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
        self.send_measurement(float(measurement), timestamp)

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

    def __init__(self, executable=None):
        self._conn, child_conn = Pipe(duplex=True)

        # Use the test program.
        if executable is None:
            executable = (which('wattsup') or
                          _raise(ValueError('Could not find wattsup in PATH')))

        # Ensure the executable resolves to a real path.
        executable = Path(executable)
        assert executable.exists(), \
            'Executable not found: {}'.format(executable)

        proc = Process(name='WattsUp? Monitor',
                       target=WattsUpMonitor,
                       args=(child_conn,),
                       kwargs={'executable': executable})
        proc.start()
        assert proc.is_alive()

        self._proc = proc
        self._ready = False

    def next_measurement(self):
        """
        Waits until the next measurement is available and returns it.
        """

        self.wait_until_ready()

        status, payload = self._recv()
        assert status == 'data'
        measurement, timestamp = payload
        return measurement, timestamp

    def wait_until_ready(self):
        """
        Returns when the WattsUp is ready and receiving power measurements.
        """
        if self._ready:
            return self

        # Block until ready.
        status, payload = self._recv()
        assert status == 'ready'
        self._ready = True

        return self

    def __enter__(self):
        self.wait_until_ready()

        # Allow sending messages.
        self._send('send')
        return self

    def __exit__(self, *exception_info):
        # Stop sending messages
        self._send('stop_send')


    def _send(self, message):
        return self._conn.send(message)

    def _recv(self):
        return self._conn.recv()


def _raise(exception):
    """
    Raise an exception (as an expression).
    """
    raise exception


def utcnow():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)


if __name__ == '__main__':
    with WattsUp(executable=here.parent/'test'/'fake-wattsup.py') as client:
        while True:
            measurement, timestamp = client.next_measurement()
            print("Got measurement:", measurement, timestamp)
