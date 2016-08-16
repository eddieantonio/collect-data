#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from time import sleep
#from sh import netperf

from measurements import Experiment


@Experiment
def idle():
    "Place no load on the computer for one hour."
    sleep(60 * 60)


# TODO: Write Chris's tests
# TODO: Write Wordpress stress test
