#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
My little logger and (maybe) other utilities.
"""

import os
import logging

def gflog(msg):
    # log with a special marker because GAE's logs are getting noisier and noisier
    logging.info("\n\n{marker} {msg}\n\n".format(marker="þþ", msg=msg))

