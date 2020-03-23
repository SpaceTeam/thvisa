#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2017/2018

@author: thirschbuechler
"""

import sys
import signal, time

sys.path.append("..") # add topleveldir to import paths
import ucmd_helper as ucmd # import mysleep?

# ISSUES #
# sigalarm can only handle 1 thing at the time, see sigalarm_queue for rlief
# "zombiewith" issue: with-context keeps going after sheparded variable deleted
# "weirdpersistance": deletion of previous timer always happens when next one is called, 
#       even if this means the next launch of the script

# ToDo: make expeption optional, use ringer in example
# ToDo: mysleep: add "try" with egg-timer?
# ToDo: mysleep: async countdown?


def dummyfct(stuff=""):
    pass # nothing todo


class eggclock(): # "object-inheritance didn't help" with "zombiewith"
    
    def __init__(self, t, timedout="ring ring", myprint=print, name="_",
                 ringer=dummyfct, makeerror=True):
        self.t=t
        self.name=name
        self.ringer=ringer # call this function on alarm
        self.myprint=myprint # to redirect debug output to print, dummyfct or something else
        self.timedout=timedout
        self.makeerror=makeerror
        self.withcontext=0 # needed to exit with cleanly? didn't help with "zombiewith"-issue
            
        self.myprint("setup eggclock ",self.name)
        
        
    def __del__(self):
        # no teardown necessary, unless a clear maybe??
        #pass
       self.myprint("eggclock ",self.name," got deleted")
       return # didn't help with "zombiewith"
    
    def __enter__(self):
        # assume it has to start right now when called as with-context
        
        #$$ "zombiewith" issue abort start
        self.myprint("due to the \"zombiewith\"-issue with-contexts are not supported for eggclocks (yet)")
        raise Exception("invalid usage of eggclock")
        sys.exit(1)
        #$$ "zombiewith" issue abort end

        self.withcontext=1
        self.start()
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.active:
            self.myprint("eggclock ",self.name," got cancelled by with-context exit")
            self.__del__() # if timedout in a with context, exit gets called so delete
    
    def start(self):
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
        self.myprint(self.timedout," by ",self.name," calling ringer..")
        self.ringer() # do something if wanted
        
        if self.makeerror:
            raise Exception(self.timedout)
            
        self.active=0 # in case someone catches the exception
        
        if self.withcontext:
            self.__del__() # make handle invalid to exit with-context, trying to fix"zombiewith" issue
        
    def dummy(self): # stopps IDE-warning "unused var" in with-context
        pass
        

### semi unit-testing ###
## prints are alowed, since only unit-test, no myprint redirectors ##

# traditional o.o. instances #
def instancetests():
	print("\nlaunching instance testing..\n")

	print("single clock")
	egg1 = eggclock(t=3, name="egg1")
	egg1.start()
	try:
		while(1):
			print('sec')
			time.sleep(1)
	except Exception as ex:
		print(ex)
		#egg1.clear()
		pass

	#print("multiple clocks")
	egg12 = eggclock(t=3, name="egg12")
	egg12.start()
	egg11 = eggclock(t=5, name="egg11")
	egg11.start()
	try:
		while(1):
			print('sec')
			time.sleep(1)
	except Exception as ex:
		print(ex)
		#egg1.clear()
		pass

# testing a with-context #        
def withtests(): # $$broken due to "zombiewith" issue
	print("\nlaunching with-context testing..\n")

	# regular #
	with eggclock(t=5, timedout="success", name="egg2", makeerror=False) as egg2:
		time.sleep(6)#
        
        # "zombiewith" issue
		if egg2:
			egg2.dummy()
		else:
			print("why can this be executed?") # "zombiewith" issue
			egg2.dummy()

    # planned exit #
	with eggclock(t=1, timedout="success", name="egg3", makeerror=False) as egg3:
		time.sleep(3)
		egg3.stop() # $$$ problemetic because after done it gets deleted #
		time.sleep(3)
        
    # premature exit #
	try:
		with eggclock(t=5, timedout="you failed!", name="egg4", makeerror=False) as egg4:
			time.sleep(3)
			1/0
			time.sleep(3)  
			egg4.dummy() 
	except Exception:
		print("success if egg4 quit on leaving context")
        
	'''
	with eggclock(t=10, timedout="you failed!") as egg2:
		text="Can you type this in less than 10s?"
		stuff=ucmd.askandreturn(text,[text])
		if stuff:	
			egg2.stop()
			print("you are winner!#BigRigs")
	'''
        
### module test ###
if __name__ == '__main__': # test if called as executable, not as library

	instancetests()
	#withtests()
	print('fin')