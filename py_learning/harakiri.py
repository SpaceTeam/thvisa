#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:18:58 2020

@author: https://stackoverflow.com/questions/293431/python-object-deleting-itself
@editor: thirschbuechler

this is probably overkill to alternatively exit a with-context, rather than by exception,
but hey, maybe it will be needed, or related to getting rid of the visa-handle within thvisa

# for some reason, __enter__ does not work in the with-context
"""

# NOTE: This is Python 3 code, it should work with python 2, but I haven't tested it.
import weakref #https://docs.python.org/3/library/weakref.html

class InsaneClass(object):
    _alive = []
    def __new__(cls): # there is a difference btw. cls and self, but i don't understand
        self = super().__new__(cls)
        InsaneClass._alive.append(self)

        return weakref.proxy(self)

    def commit_suicide(self):
        self._alive.remove(self)
        
    def __enter__(self):
        print("enter says hello")
        return self
    
    def __init__(self):
        pass
        
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        print("bye")


if __name__ == '__main__': # test if called as executable, not as library
    
    instance = InsaneClass()
    instance.__enter__()
    instance.commit_suicide()
    #print(instance)
    print(InsaneClass) # pointer
    print(InsaneClass().__enter__()) # an object
    
    print("now, something completely different!")
        
    with InsaneClass() as i:
        i.commit_suicide()
        print(i)