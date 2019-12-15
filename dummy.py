#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:44:42 2019

@author: thomas
"""

def printdummy(*args):
    pass

myprint = print

myprint("hello","bye")

myprint = printdummy

myprint("you suck!","\nreally..")