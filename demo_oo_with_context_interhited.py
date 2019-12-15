#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 18:34:45 2019

@author: thomas

why context managers? see
https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/

TL;DR: "Essentially, any object that needs to have close called on it
        after use is (or should be) a context manager."

this defaults init works:
    https://stackoverflow.com/questions/8073726/python-inheritance-and-default-values-in-init
this defaults init format didn't:
    https://scikit-rf.readthedocs.io/en/latest/_modules/skrf/vi/vna/keysight_pna.html

"""

class dummyc(object):
    
    # to be overwritten by children
    firstnamedef=""
    lastnamedef=""
    def __init__(self, firstname=firstnamedef, lastname=lastnamedef):
        print("aa")
        self.firstname=firstname
        self.lastname=lastname
        self.report("created")
        
        
    def __del__(self):
        self.report("delete called, session ended")
        #return
    
    def __enter__(self):
        self.report("with-context entered")
        return self # unless this happens, tanya dies before reporting "locked and loaded"
    
    def __exit__(self, exc_type, exc_value, tb):
        self.report("with-context exited")
        self.__del__() # unless this happens, session doesn't get exited
        #return
    
    def report(self, st):
        print("{} {} reports: {}".format(self.firstname, self.lastname, st))
        
    def be_silly(self):
        raise Exception("pink fluffy unicorns riding on rainbows")
        

class herbert(dummyc):
    firstnamedef="Herbert"
    lastnamedef="Dummyuser"
    def __init__(self, firstname=firstnamedef, lastname=lastnamedef):
         super(herbert, self).__init__(firstname="Herbert", lastname="Dummyuser") # call parent init 

    
### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #demo(herbfail=1)
    
   with herbert() as herb:
       herb.report("bananaa")