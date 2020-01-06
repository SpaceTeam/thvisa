#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2017/2018

@author: thirschbuechler
"""

import signal, datetime, time
import ucmd_helper as ucmd

# todo: make object oriented to have multiple timer option
# ToDo: mysleep: add "try" with egg-timer?
# ToDo: mysleep: async countdown?

def dummyring():
    pass # nothing todo

class eggclock():
    
    def __init__(self, t, timedout="ring ring", myprint=print, name="_",
                 ringer=dummyring, makeerror=True):
        self.t=t
        self.name=name
        self.ringer=ringer
        self.myprint=myprint
        self.timedout=timedout
        self.makeerror=makeerror
            
        self.myprint("setup eggclock ",self.name)
        
        
    def __del__(self):
        # no teardown necessary, unless a clear maybe??
        pass
    
    def __enter__(self):
        # assume it has to start right now when called as with-context
        self.start()
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.active:
            self.myprint("Eggclock ",self.name," got cancelled by with-context exit")
            #self.__del__() # if timedout in a with context, exit gets called so delete #no didn't work
    
    def start(self): # synonym-fct
    	self.myprint("starting eggclock ",self.name,"t=",self.t) 
    	signal.signal(signal.SIGALRM, self.ring)
    	signal.alarm(self.t)
    	self.active=1
          
    def stop(self): # synonym fct
        self.clear()
        
    def clear(self):
        self.myprint("stopping eggclock ",self.name)
        signal.alarm(0)
        self.active=0
        
    def ring(self,signum ,frame): # was handler
        self.myprint(self.timedout," by ",self.name)
        self.ringer() # do something if wanted
        if self.makeerror:
            raise Exception(self.timedout)
        self.active=0 # in case someone catches the exception
        
        
### module test ###
if __name__ == '__main__': # test if called as executable, not as library

    # traditional example #
	egg1 = eggclock(t=3)
	egg1.start()
	try:
		while(1):
			print('sec')
			time.sleep(1)
	except Exception as ex:
		print(ex)
		#egg1.clear()
		pass
    
    # testing a with-context #
	with eggclock(t=5, timedout="success", name="egg2", makeerror=False) as egg2:
		time.sleep(6)

    # testing with-context planned exit"
	with eggclock(t=1, timedout="you failed!", name="egg3", makeerror=True) as egg3:
		time.sleep(3)
		egg3.stop() # $$$ problemetic somehow
		time.sleep(3)
        
    # testing with-context premature exit"
	with eggclock(t=5, timedout="you failed!", name="egg4", makeerror=False) as egg4:
		time.sleep(3)
		1/0
		time.sleep(3)
        
	'''
	with eggclock(t=10, timedout="you failed!") as egg2:
		text="Can you type this in less than 10s?"
		stuff=ucmd.askandreturn(text,[text])
		if stuff:	
			egg2.stop()
			print("you are winner!#BigRigs")
	'''
	
	print('fin')