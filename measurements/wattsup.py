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
import datetime
import logging

from multiprocessing import Process, Pipe
from contextlib import suppress

from path import Path
from sh import which

__all__ = ['WattsUp']

here = Path(__file__).parent
logger = logging.getLogger(__name__)

class ExitSuccessfully(BaseException):
    """
    Thrown when the WattsUpMonitor exits succesfully.
    """


class WattsUpMonitor:
    def __init__(self, conn, executable=None, args=None):
        self.conn = conn
        self.should_send = False

        # Start a blocking text stream
        arg_list = [executable] + list(args or ())
        with subprocess.Popen(arg_list, stdout=subprocess.PIPE) as proc:
            self.proc = proc
            self.wait_for_ready()
            with suppress(ExitSuccessfully):
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
        measurement_text = line_buffer.decode("ascii").strip()

        try:
            measurement = float(measurement_text)
        except ValueError as exception:
            logger.exception("Could not read measurement %r:",
                             measurement_text)
        else:
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
        elif message == 'terminate':
            self.terminate()
        else:
            raise ValueError('Unknown control message: {}'.format(message))

    def send_measurement(self, measurement, timestamp):
        if self.should_send:
            self.reply('data', (measurement, timestamp))

    def reply(self, message, payload=None):
        self.conn.send((message, payload))

    def terminate(self):
        self.proc.terminate()
        self.reply('exit')
        self.conn.close()
        raise ExitSuccessfully()


class WattsUp:
    """
    High-level interface to the WattsUp?

    Usage::

        with WattsUp() as client:
            measurement, timestamp = client.next_measurement()
            print("Got measurement:", measurement, timestamp)
            # Take as many measurements as necessary.

    """

    def __init__(self, executable=None, args=None):
        self._conn, child_conn = Pipe(duplex=True)

        # Use the test program.
        if executable is None:
            executable = (which('wattsup') or
                          _raise(ValueError('Could not find wattsup in PATH')))

        # Ensure the executable resolves to a real path.
        executable = Path(executable)
        assert executable.exists(), (
            'Executable not found: {}'.format(executable)
        )

        proc = Process(name='WattsUp? Monitor',
                       target=WattsUpMonitor,
                       args=(child_conn,),
                       kwargs={'executable': executable, 'args': args})
        proc.start()
        assert proc.is_alive()

        self._proc = proc
        self._ready = False
        self._closed = False

    def close(self):
        """
        Closes the connection to the Watts Up?
        """
        self._send('terminate')
        self._flush_until_exit()

        self._conn.close()
        self._proc.join()
        return self

    def _flush_until_exit(self, timeout=3):
        while True:
            status, _ = self._recv()
            if status == 'exit':
                return

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
        status, _ = self._recv()
        assert status == 'ready'
        self._ready = True

        return self

    @property
    def _conn(self):
        """
        Pipe connection to the WattsUpMonitor.

        Raises a RuntimeError when access is attempted, but the connection is
        closed.
        """
        if self._real_conn and self._real_conn.closed:
            raise RuntimeError('Cannot used Watts Up? after calling .close()')
        return self._real_conn

    @_conn.setter
    def _conn(self, conn):
        self._real_conn = conn

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
    client = WattsUp(executable=here.parent/'test'/'fake-wattsup.py',
                     args=['-D'])
    with client:
        for _ in range(2):
            measurement, timestamp = client.next_measurement()
            print("Got measurement:", measurement, timestamp)

    client.close()
