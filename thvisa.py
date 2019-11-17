#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 18:23:02 2019

@author: thirschbuechler
"""

import sys
import visa
import numpy as np
from enum import Enum

# ToDo:
# more visa error types to see why oszi doesn't always behave on init (psu does now)

# how useful is it to directly use usbtmc, if it's in the backend of pyvisa anyway...? probably not very...
class drv(Enum):
	tmc = 'usbtmc'
	pyv = 'py-visa' # data read raw (graphs) does not work at the moment
    
    
lastcmd = ""
driver = drv.tmc
myprint = print
myinstruments = []


    
def init():
    global rm
    # this works always
    rm = visa.ResourceManager()
    instruments = np.array(rm.list_resources())
    
    
    # this only works sometimes.. pyvisa.. catch general exception
    # for some reason, it's lucky to query the keysight oszi first...
    
    myprint("querying instruments..")
    if len(instruments)<0:
        myprint("no instruments: sad puppy.")
    else:
        myprint("say hello")
        for instrument in instruments:
            print(instrument)
            try:
                delay=0.5
                if "NPD" in instrument:
                    delay=1
                    
                my_instrument = rm.open_resource(instrument, query_delay = delay) #spd3303c needs delay
                identity = my_instrument.query('*IDN?')
                myprint("Resource: '" + instrument + "' is")
                myprint(identity + '\n')
                myinstruments.append(instrument)
                
                print("cleanup after idn")
                my_instrument.close() # shut down
                del my_instrument
                
            except visa.VisaIOError:
               myprint('No connection to: ' + instrument)
            except:
                myprint("Unexpected error:", sys.exc_info()[0])
                myprint("maybe resource busy, i.e. increase query_delay or unplug-replug")


def getinstrument(name,qdelay=0): #name segment as input
    global myinstruments, rm
    
    for instrument in myinstruments:
        if name in instrument:
            return(rm.open_resource(instrument, query_delay=qdelay)) #exits on first find
    
    #else, this happens:        
    return(0)


def getrm():
    global rm
    return(rm)
    
def setprint(function): # to redirect print to pdf, etc.
	global myprint
	myprint=function



############# keysighthelper things
def writer(st):
	global instr, driver, lastcmd
	# same, regardless of pyvisa/tmc, for now
	
	try:
		lastcmd="write "+st
		#st+="\n" # not needed
		instr.write(st)

	except IOError as exc:
		myprint("write "+st+" rased an IO Error"+str(exc))
		#writer("*CLS")#clear error #doesn't work for non-triggered
		#myprint(askready())
		pass
	

def askready(): # should contain whether all operations have been finished
	# todo check whether trigger worked within exp. time
	return(ask("*OPC?"))


def ask(st):
	global instr, driver, lastcmd
	
	try:
		lastcmd="ask "+st
		#st+="\n" # not needed
		if driver == drv.tmc:
			return(instr.ask(st))
		elif driver == drv.pyv:
			return(instr.query(st))
	except IOError as exc:
		myprint("write "+st+" rased an IO Error"+str(exc))
		#myprint(askready()) # this calls itself, duh
		pass


def raw(st):
	global instr, driver
	
	if (driver == drv.tmc):
		return(instr.read_raw(st))
	elif (driver == drv.pyv):
		return(instr.query(st))#is this really how the visa driver handles raw data # no it throws some errors
        


### module test ###        
if __name__ == '__main__': # test if called as executable, not as library
    init()