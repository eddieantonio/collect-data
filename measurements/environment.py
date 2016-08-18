#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
A key-value for global variables, that also looks up the operating system's
environment variables.

>>> from measurments import env
>>> '/bin' in env.PATH
True
>>> env.HOSTNAME = 'freedomstation'
>>> env.HOSTNAME
'freedomstation'
"""

import os


class Environment:
    """
    Environment variables.
    """
    __slots__ = ['_env']

    def __init__(self):
        # Can't use self._env = ... because it induces infinite recursion.
        object.__setattr__(self, '_env', {})

    def lookup(self, key, default=None):
        # Look it up locally
        if key in self._env:
            return self._env[key]

        # Look it up in the OS environment or return the default.
        return os.getenv(key, default)

    def __getattr__(self, key):
        return self.lookup(key)

    def __getitem__(self, key):
        return self.lookup(key)

    def __setattr__(self, key, value):
        self._env[key] = value

    def __contains__(self, key):
        # If we get this exact item back as the default, this means the lookup
        # failed.
        not_found = object()
        # double negative ftw
        return self.lookup(key, not_found) is not not_found
