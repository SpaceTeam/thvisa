#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2017/2018

@author: thirschbuechler
"""

import signal, datetime, time

# todo: make object oriented to have multiple timer option
# ToDo: mysleep: add "try" with egg-timer?
# ToDo: mysleep: async countdown?

sleepstatus="working"
sleephandler=print # pointer can be replaced with something else to update gui, etc.
timedout="Outta Time"

		
def mysleep(t): 
	global sleepstatus
    
	sleepstatus="Sleeping for %.3g s .." %t
	sleephandler(sleepstatus)
    
	time.sleep(t)
    
	sleepstatus="working .."
	sleephandler(sleepstatus)
	
    
def getsleepstatus():
	global sleepstatus
	return(sleepstatus)
    
    

def handler(signum ,frame):
	global timedout
	raise Exception(timedout)

def settimer(t):		
	signal.signal(signal.SIGALRM, handler)
	signal.alarm(t)
	
def cleartimer():
	signal.alarm(0)

def setstr(inp):
	global timedout
	timedout=inp


def mytime():
	d=datetime.datetime.now()
	return(d.strftime("%A, %d. %B %Y %H:%M"))

def myfoldertime():
	d=datetime.datetime.now()
	# format to be most path compatible and able to continue without error
	# if script gets aborted within 1min (include seconds, to avoid different runs in same folder)
	return(d.strftime("%d_%m_%Y_%H%M%S"))

def mymoment():
	d=datetime.datetime.now()
	return(d.strftime("%H:%M:%S.%f"))	



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
	settimer(3)
	try:
		while(1):
			print('sec')
			print(mytime())
			print(mymoment())
			time.sleep(1)
	except Exception as ex:
		print(ex)
		cleartimer()
		
	print('fin')