#!/usr/bin/env python

from setuptools import setup

setup(name='Measurements',
      version='0.1.0',
      description='Run energy tests using a Watts Up? Pro',
      author='Eddie Antonio Santos',
      packages=['measurements'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'])
