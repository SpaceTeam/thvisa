#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 21:37:06 2020

@author: https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager

"""
# pseudocode explaining non-object oriented contextmanager-decoration "@contextmanager"
# non-object oriented means non-instancable --> we don't want that!!
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwds):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)

with managed_resource(timeout=3600) as resource:
    print("Hi")
    # Resource is released at the end of this block,
    # even if code in the block raises an exception