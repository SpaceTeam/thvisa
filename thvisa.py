#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 18:23:02 2019

@author: thirschbuechler
"""
# re-invent the wheel, because python-ivi seems pretty dead, unfortunately.
import sys
import visa
import numpy as np
#from enum import Enum

# ToDo:
# more visa error types to see why instr doesn't always behave on init (psu does now)

def printdummy(*args):
    pass


class thInstr:
# Python3 object orientation:
# first parameter "object" for inheritence can be ignored


    # Initializer / Instance Attributes
    def __init__(self, myprint = print):
        self.myinstruments = []
        self.rm = visa.ResourceManager()
        instruments = np.array(self.rm.list_resources())
        
        
        # this only works sometimes.. pyvisa.. catch general exception
        # for some reason, it's lucky to query the keysight oszi first...
        
        myprint("querying instruments..")
        if len(instruments)<0:
            myprint("no instruments: sad puppy.")
        else:
            myprint("say hello")
            for instrument in instruments:
                myprint(instrument)
                try:
                    delay=0.5
                    # toDo: don't 
                    if "NPD" in instrument: #spd3303c needs delay at init
                        delay=1
                        
                    with self.rm.open_resource(instrument, query_delay = delay) as my_instrument:
                        identity = my_instrument.query('*IDN?')
                        myprint("Resource: '" + instrument + "' is")
                        myprint(identity + '\n')
                        self.myinstruments.append(instrument)
                        
                        myprint("cleanup after idn")
                    # "with"context cleans class up after use / when dying
                    # better than deconstructor: https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
                    #my_instrument.close() # shut down # gets called by __del__ of rm (https://pyvisa.readthedocs.io/en/latest/_modules/pyvisa/highlevel.html#ResourceManager.close)
                    #del my_instrument
                    
                except visa.VisaIOError:
                   myprint('VisaError: No connection to: ' + instrument+", maybe chunk size or msg timeout, query_delay")
                   # like VisaIOError.VI_ERROR_INV_SETUP VisaIOError.VI_ERROR_CONN_LOST:               
                except visa.InvalidSession:
                    myprint("VisaError: session closed before access") # tested via closing session before "IDN?"
                except visa.VisaIOWarning:
                   myprint("VisaError:  VisaIOWarning")
                except OSError: # not of visa but OS
                   myprint("OS error, maybe library not found?")
                except:
                   myprint("VisaError:  Unexpected error:", sys.exc_info()[0])
                   myprint("maybe resource busy, i.e. increase query_delay or unplug-replug")


    def getinstrument(self, name,qdelay=0): #name segment as input
        
        for instrument in self.myinstruments:
            if name in instrument:
                return(self.rm.open_resource(instrument, query_delay=qdelay)) #exits on first find
        
        #else, this happens:        
        return(0)
    
    
    def getrm(self):
        return(self.rm)
        
    def setprint(self, function): # to redirect print to pdf, etc.
    	global myprint
    	myprint=function
    
    def visa_write_delayed(visa,msg,wait_time_ms = 100):
        err_flag = visa.write(msg)
        time.sleep(wait_time_ms/1000)
        return err_flag
    
    
    # =========================================================
    # Send a command and check for errors:
    # =========================================================
    def do_command(command, hide_params=False):
        global instr
        
        if hide_params: 
            (header, data) = string.split(command, " ", 1)
            if debug: print("\nCmd = '%s'" % header)
        else:
            if debug: print("\nCmd = '%s'" % command)
                
        instr.write("%s" % command)
        
        if hide_params:
            check_instrument_errors(header)
        else:
            check_instrument_errors(command)
        
        
    # =========================================================
    # Send a command and binary values and check for errors:
    # =========================================================
    def do_command_ieee_block(command, values):
        global instr
        
        if debug:
            print("Cmb = '%s'" % command)
        instr.write_binary_values("%s " % command, values, datatype='c')
        check_instrument_errors(command)
        
        
    # =========================================================
    # Send a query, check for errors, return string:
    # =========================================================
    def do_query_string(query):
        global instr
        
        if debug: print("Qys = '%s'" % query)
    
        result = instr.query("%s" % query)
        check_instrument_errors(query)
        return result
    
    
    # =========================================================
    # Send a query, check for errors, return floating-point value:
    # =========================================================
    def do_query_number(query):
        global instr
        
        if debug: print("Qyn = '%s'" % query)
        results = instr.query("%s" % query)
        check_instrument_errors(query)
        return float(results)
    
    
    # =========================================================
    # Send a query, check for errors, return binary values:
    # =========================================================
    def do_query_ieee_block(query):
        global instr
        
        if debug: print("Qys = '%s'" % query)
        result = instr.query_binary_values("%s" % query, datatype='s')
        check_instrument_errors(query)
        return result[0]
    
    
    # =========================================================
    # Check for instrument errors:
    # =========================================================
    def check_instrument_errors(command):
        global  instr
        
        while True:
            error_string = instr.query(":SYSTem:ERRor?")
            if error_string: # If there is an error string value.
                if error_string.find("+0,", 0, 3) == -1: # Not "No error".
                    print("ERROR: %s, command: '%s'" % (error_string, command))
                    print("Exited because of error.")
                    sys.exit(1)
                else: # "No error"
                    break
            else: # :SYSTem:ERRor? should always return string.
                print("ERROR: :SYSTem:ERRor? returned nothing, command: '%s'" % command)
                print("Exited because of error.")
                sys.exit(1)
    


### module test ###        
if __name__ == '__main__': # test if called as executable, not as library
    myinstr = thInstr()