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
import time
import string
#from enum import Enum

# ToDo:
# more visa error types to see why instr doesn't always behave on init (psu does now)

def printdummy(*args):
    pass


class thInstr(object):
    # Python3 object orientation:
    # first parameter "object" for inheritence can be ignored
    # the "self" parameter of subfunctions can't be ingored internally, only externally
    # i.e. the __init__-constructor has do specify self,
    # but calling it from the main loop just ignore it,
    # i.e. instance = myclass(), then myclass.fct(parameter1, parameter2, ..)
    # , param0=self=omitted

    # default attributes for child-classes
    myprintdef = printdummy
    instrnamedef = 0
    qdelaydef = 1 # chose 1sec if not overridden to give slow instruments a chance
    # Initializer / Instance Attributes
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef):

        self.myprint=myprint
        self.myinstruments = []
        self.instr = 0
        self.instrname = instrname
        self.qdelay = qdelay
        
        self.myprint("looking for instr name {}.. listing instruments shortly..".format(self.instrname))
        try:
            self.rm = visa.ResourceManager()
            instruments = np.array(self.rm.list_resources())
        except OSError: # not of visa but OS
           self.myprint("OS error, maybe restart python script host, or library not found?")
           sys.exit(0)

        # this only works sometimes.. pyvisa.. catch general exception
        # for some reason, it's lucky to query the keysight oszi first...

        self.myprint("querying instruments..")
        if len(instruments)<0:
            self.myprint("no instruments: sad puppy.")
        else:
            self.myprint("say hello")
            for instrument in instruments:
                self.myprint(instrument)
                try:
                    with self.rm.open_resource(instrument, query_delay = self.qdelay) as my_instrument:
                        # "with"context cleans class up after use / when dying
                        # better than deconstructor: https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
                        identity = my_instrument.query('*IDN?')
                        self.myprint("Resource: '" + instrument + " is " + identity + '\n')
                        self.myinstruments.append(instrument)

                    #self.myprint("cleanup after idn")
                    #my_instrument.close() # shut down # gets called by __del__ of rm
                    # as seen here (https://pyvisa.readthedocs.io/en/latest/_modules/pyvisa/highlevel.html#ResourceManager.close)
                    #del my_instrument

                except visa.VisaIOError:
                   self.myprint('VisaError: No connection to: ' + instrument+", maybe chunk size or msg timeout, query_delay")
                   # like VisaIOError.VI_ERROR_INV_SETUP VisaIOError.VI_ERROR_CONN_LOST:
                except visa.InvalidSession:
                    self.myprint("VisaError: session closed before access") # tested via closing session before "IDN?"
                except visa.VisaIOWarning:
                   self.myprint("VisaError:  VisaIOWarning")
                except OSError: # not of visa but OS
                    self.myprint("OS error, maybe restart python script host, or library not found?")
                except:
                   self.myprint("VisaError:  Unexpected error:", sys.exc_info()[0])
                   self.myprint("maybe resource busy , i.e. increase query_delay or unplug-replug"+"\n"+"or already taken by other/older session, if you didn't use a \"with\"-context")


        # intendation level: __init__
        # now, if name specified, return thing
        if self.instrname:
            self.instr=(self.getinstrument(instrname, qdelay=qdelay))
            self.instrname=instrname
        else:
            self.myprint("you made no wish, so you aren't gettin' any!")#$do something?
            #return(0)

    # end __init__

    def getinstrument(self, name,qdelay=0): #name segment as input #$todo: inline if no other use 

        for instrument in self.myinstruments:
            if name in instrument:
                return(self.rm.open_resource(instrument, query_delay=qdelay)) #exits on first find

        #else, this happens:
        self.myprint("oh noes, requested instrument not found!")#$do something?
        sys.exit(0)


    # depreciated: do commands as class functions, not externally
    #def getrm(self):
    #    return(self.rm)


    # if needs some mod after init routine
    def setprint(self, function): # to redirect print to pdf, print, etc.
    	self.myprint=function


    def visa_write_delayed(self, visa,msg,wait_time_ms = 100):
        self.myprint("delayed Cmd = '%s'" % command)
        err_flag = visa.write(msg)
        time.sleep(wait_time_ms/1000)
        return err_flag


    # =========================================================
    # Send a command and check for errors:
    # =========================================================
    def do_command(self, command, hide_params=False):

        if hide_params:
            (header, data) = string.split(command, " ", 1)
            self.myprint("\nCmd = '%s'" % header)
        else:
            self.myprint("\nCmd = '%s'" % command)

        self.instr.write("%s" % command)

        if hide_params:
            self.check_instrument_errors(header)
        else:
            self.check_instrument_errors(command)


    # =========================================================
    # Send a command and binary values and check for errors:
    # =========================================================
    def do_command_ieee_block(self, command, values):

        self.myprint("Cmd block = '%s'" % command)
        self.instr.write_binary_values("%s " % command, values, datatype='c')
        self.check_instrument_errors(command)


    # =========================================================
    # Send a query, check for errors, return string:
    # =========================================================
    def do_query_string(self, query):

        self.myprint("Qys = '%s'" % query)
        result = self.instr.query("%s" % query)
        self.check_instrument_errors(query)
        return result


    # =========================================================
    # Send a query, check for errors, return floating-point value:
    # =========================================================
    def do_query_number(self, query):

        self.myprint("Qyn = '%s'" % query)
        results = self.instr.query("%s" % query)
        self.check_instrument_errors(query)
        return float(results)


    # =========================================================
    # Send a query, check for errors, return binary values:
    # =========================================================
    def do_query_ieee_block(self, query):

        self.myprint("Qys = '%s'" % query)
        result = self.instr.query_binary_values("%s" % query, datatype='s')
        self.check_instrument_errors(query)
        return result[0]


    # =========================================================
    # Check for instrument errors:
    # =========================================================
    def check_instrument_errors(self, command):

        while True:
            error_string = self.instr.query(":SYSTem:ERRor?")
            if error_string: # If there is an error string value.
                error_string = error_string.strip("ERROR: ") # remove that
                error_string = error_string.strip("+") # remove that
                if error_string.find("0", 0, 1) == -1: # Not "ERROR: 0  No Error"
                   self.myprint("ERROR: %s, command: '%s'" % (error_string, command))
                   self.myprint("Exiting on error.")
                   self.myprint("i can see my house from up here")
                   sys.exit(1)
                else: # "No error"
                    break
            else: # :SYSTem:ERRor? should always return string.
               self.myprint("ERROR: :SYSTem:ERRor? returned nothing, command: '%s'" % command)
               self.myprint("Exiting due to error.")
               sys.exit(1)
    
    
    def __del__(self):
        #self.instr.close() # shut down # gets called by __del__ of rm
        # as seen here (https://pyvisa.readthedocs.io/en/latest/_modules/pyvisa/highlevel.html#ResourceManager.close)
        if (self.instr):
            self.instr.close()
            self.myprint("say goodbye, instrument {}!".format(self.instrname))

    
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        self.__del__() # kill, kill!
        #return True
    
    
    def __enter__(self):# Qwith" context entered: do nothing other than init
        #self.__init__() # come to life
        #return True
        return self


### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    myinstr = thInstr(myprint=print)

    #todo: test all functions, or specify to run other module which does.. really!!
