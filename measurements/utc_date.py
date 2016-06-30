#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Time is weird, man. Leave aside special relativity and the effect of inertial
reference frames. Even in the inertial reference of the surface of the Earth,
time is weird. So, we made some weird decisions to make time easier to deal
with on our dumb digital binary computers. We'd like a single, simple number,
so we just count the how many milliseconds it's been since was midnight on
January 1, 1970 at the Greenwich observatory. This is a Unix timestamp,
augmented with explicit reference to an arbitrary timezone: universal
coordinated time (yes, _that's_ what "UTC" stands for).

These are utilities that help convert from and to this arbitrary, yet simple
format. Just be consistent!
"""

from datetime import datetime, timezone


UNIX_EPOCH = datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)


def from_timestamp(timestamp):
    """
    Returns a datetime object from the given Unix timestamp in milliseconds.
    """
    return datetime.fromtimestamp(timestamp / 1000.0,
                                  tz=timezone.utc)


def to_timestamp(date):
    """
    Returns a Unix UTC timestamp in milliseconds as a float.
    """
    return 1000.0 * (date - UNIX_EPOCH).total_seconds()


def now():
    """
    Returns a datetime now in the UTC timezone.
    """
    return datetime.now(tz=timezone.utc)


def is_in_utc(time):
    """
    Returns True if the given datetime is a timezone aware object AND is its
    timezone is UTC.
    """
    return time.tzinfo is timezone.utc
