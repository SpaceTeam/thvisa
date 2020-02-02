#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 21:05:04 2020

@author: thomas
"""

class dummyc(object):
    
    # to be overwritten by children
    firstnamedef=""
    lastnamedef=""
    def __init__(self, firstname=firstnamedef, lastname=lastnamedef):
        print("calling init")
        self.firstname=firstname
        self.lastname=lastname
        self.report("created")
        
        
    def __del__(self):
        self.report("delete called, session ended")
        #return
    
    def __enter__(self):
        #self.report("with-context entered")
        return self # unless this happens, tanya dies before reporting "locked and loaded"
    
    def __exit__(self, exc_type, exc_value, tb):
        #self.report("with-context exited")
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
    
    # this is badly coded but only an example, nothing to maintain.. #     
    def sillyguard(self):
        try:
            self.be_silly()
        except Exception as e:
            print(e)
            self.__exit__(None, None, None)

    def sillyguard2(self):
        try:
            self.be_silly()
        except Exception as e:
            print(e)
            self.__exit__(None, None, None)
            raise Exception
    
    def exittry(self):
        raise Exception
        print("hello exit")
        self.__exit__(None, None, None)

    
### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #demo(herbfail=1)
    
   print("guarding silly exception with try in class, what happens?")
   with herbert() as herb:
       herb.report("\nbananaa")
       
       herb.sillyguard()
       
       
       herb.report("##############bad if this shows up")
       
   
   print("guarding silly exception .. not.. what happens?")
   with herbert() as herb:
       herb.report("\nbananaa2")
       
       #herb.sillyguard()
       herb.be_silly()
       
       herb.report("##############bad if this shows up2")


   print("guarding silly exception with try in class BUT raising another afterwards, what happens?")
   with herbert() as herb:
       herb.report("\nbananaa3")
       
       herb.sillyguard2()
      
       
       herb.report("##############bad if this shows up3")
                   
                   
    