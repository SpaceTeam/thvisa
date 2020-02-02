#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 18:34:45 2019

@author: thomas

why context managers? see
https://jeffknupp.com/blog/2016/03/07/python-with-context-managers/

TL;DR: "Essentially, any object that needs to have close called on it
        after use is (or should be) a context manager."


"""

class dummyc():
    def __init__(self, firstname, lastname):
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
        
        
def demo(herbfail=0, tanfail=0):
    print("\n## Who won't end the session? ##")
    
    if herbfail:
        print("herbert will fail hard if no try-except block")
    
    if tanfail:
        print("Tanya will fail but recover")
    elif not herbfail:
        print("demonstrating regular operation")
        
    print("")
    
    myherb = dummyc(firstname="Herbert",lastname="Dummyuser")
    print("Later maybe, now i'll fetch a banana")
    if herbfail:
        myherb.be_silly()
    myherb.report("byebye")
    
    with dummyc(firstname="Tanya",lastname="firmwaria") as mytan:
        mytan.report("locked and loaded")
        if tanfail:
            mytan.be_silly()
        mytan.report("do svidaniya")

    print("demofct end \n\n")
    
    
### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #demo(herbfail=1)
    
    demo()
    try:
        demo(tanfail=1)
        print("Never gonna give you up")
    except Exception as e:
        print("Exception "+str(e))
        print(" Ignoring... ")
        pass
    
    
    try:
        demo(herbfail=1)
        print("Never gonna give you up")
    except Exception as e:
        print("Exception: "+str(e))
        print(" Ignoring... ")
        pass
    