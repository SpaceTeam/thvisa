#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 18:23:02 2019

@author: thirschbuechler
"""
# re-invent the wheel, because python-ivi seems pretty dead, unfortunately.
import sys # don't use sys.exit() , it  terminates a while_context_exit!! USE thvisa classes' exit() (no underlines required)
import visa
import numpy as np
import time
import string
#from enum import Enum

# ToDo:
# merge visa_write_delayed into do_command

def printdummy(*args):
    pass


statedict = {
        True: "ON",
        False: "OFF"}

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
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef, wdelay = 0):

        self.myprint=myprint
        self.myinstruments = []
        self.instr = 0
        self.instrname = instrname
        self.qdelay = qdelay # initial query delay
        self.wdelay = wdelay # write quer delay
        self.alwayscheck=True
        blacklist=["ASRL"] # asynchronous serial/parallel which fails on *IDN?
        
        self.myprint("looking for instr name {}.. listing instruments shortly..".format(self.instrname))
        try:
            self.rm = visa.ResourceManager()
            instruments = np.array(self.rm.list_resources())
        except OSError: # not of visa but OS
           self.myprint("OS error, maybe restart python script host, or library not found?")
           #ys.exit(0)
           self.exit() # re-raise expection

        # this only works sometimes.. pyvisa.. catch general exception
        # for some reason, it's lucky to query the keysight oszi first...

        self.myprint("querying instruments..")
        
        if len(instruments)<0:
            self.myprint("no instruments: sad puppy.")
            
        else:   # blacklisting & detection
            instruments = list(instruments)
            instruments2=instruments.copy()
            self.myprint("blacklisting bad handles..")
            # clean list
            for instrument in instruments:        
                if any(b in instrument for b in blacklist): # check substring
                    instruments2.remove(instrument)
                        
            instruments=instruments2
            
            self.myprint("say hello, instruments!")
            for instrument in instruments:
                self.myprint(instrument)
                try:
                    with self.rm.open_resource(instrument, query_delay = self.qdelay) as my_instrument:
                        # "with"context cleans class up after use / when dying
                        # better than deconstructor: https://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python/
                        identity = my_instrument.query('*IDN?') # raw access (no own fcts) only here
                        self.myprint("Resource: '" + instrument + " is " + identity + '\n')
                        self.myinstruments.append(instrument)

                    #self.myprint("cleanup after idn")
                    #my_instrument.close() # shut down # gets called by __del__ of rm
                    # as seen here (https://pyvisa.readthedocs.io/en/latest/_modules/pyvisa/highlevel.html#ResourceManager.close)
                    #del my_instrument

                except visa.VisaIOError:
                   e='VisaError: No connection to: ' + instrument+", maybe chunk size or msg timeout, query_delay"
                   self.exception(e)
                   # like VisaIOError.VI_ERROR_INV_SETUP VisaIOError.VI_ERROR_CONN_LOST:
                except visa.InvalidSession:
                    e=("VisaError: session closed before access") # tested via closing session before "IDN?"
                    self.exception(e)
                except visa.VisaIOWarning:
                   e=("VisaError:  VisaIOWarning")
                   self.exception(e)
                except OSError: # not of visa but OS
                    e=("OS error, maybe restart python script host, or library not found?")
                    self.exception(e)
                except ValueError as e: # e.g. wrong format, etc.
                    self.exception(e) # note: this was supposed to prevent osci-lockup on no_trigger scenario,
                    # but trigger:force proved to do that, reading wavedata when no aquisition happened remains bad
                except:
                   self.myprint("VisaError:  Unexpected error:", sys.exc_info()[0])
                   self.myprint("maybe resource busy , i.e. increase query_delay or unplug-replug"+"\n"+"or already taken by other/older session, if you didn't use a \"with\"-context")
                   self.exception()
               

        # intendation level: __init__
        # now, if name specified, return thing
        if self.instrname:
            self.instr=(self.getinstrument(instrname, qdelay=qdelay))
            self.instrname=instrname
        else:
            self.myprint("you made no wish, so you aren't gettin' any!")#$do something?
            #return(0)

    # end __init__

    def __del__(self):
        #self.instr.close() # shut down # gets called by __del__ of rm
        # as seen here (https://pyvisa.readthedocs.io/en/latest/_modules/pyvisa/highlevel.html#ResourceManager.close)
        if (self.instr):
            self.instr.close()
            self.myprint("say goodbye, instrument {}!".format(self.instrname))


    def exit(self): # shorthand to avoid sys.exit()
        #self.__exit__(None, None, None)
        
        # misguided understanding: to do an exit, this needs to raise an exception
        # not call __exit__ which only gets called on regular exit but doesn't cause it!!
        raise Exception("while-context exit dialed in")
    
    # misguided past understanding: this gets called on whith-exit #
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        self.myprint("closing instr. session..")
        self.__del__() # kill, kill!
        if not self.instr: # if the instr was closed already
            self.myprint("instr handle invalid in del routine, exiting...")
            sys.exit(0)
        
        #return True
    
    
    def __enter__(self):# Qwith" context entered: do nothing other than init
        #self.__init__() # come to life
        #return True
        return self
    
    def exception(self, e="lazyprogrammer"):
        self.myprint("Exception: ",e)
        self.exit()
        
    def getinstrument(self, name,qdelay=0): #name segment as input #$todo: inline if no other use 
        try:
            for instrument in self.myinstruments:
                if name in instrument:
                    return(self.rm.open_resource(instrument, query_delay=qdelay)) #exits on first find
        except Exception as e:
            self.exception(e)

            
        #else, this happens:
        s="oh noes, requested instrument not found!"
        self.myprint(s)
        self.exception(s)


    # depreciated: do commands as class functions, not externally
    #def getrm(self):
    #    return(self.rm)


    # if needs some mod after init routine
    def setprint(self, function): # to redirect print to pdf, print, etc.
        self.myprint=function

    # =========================================================
    # Send a command and check for errors:
    # =========================================================
    def do_command(self, command, hide_params=False):
        
        try:
            if hide_params:
                (header, data) = string.split(command, " ", 1)
                printy=header
            else:
                printy=command    
                
            self.myprint("\nCmd = '%s'" % printy)
            self.instr.write("%s" % command)
            
            if self.alwayscheck:
                time.sleep(self.wdelay)
                self.check_instrument_errors(printy)
                
        
        except Exception as e:
            self.exception(e)

        finally:
            time.sleep(self.wdelay)


    # =========================================================
    # Send a command and binary values and check for errors:
    # =========================================================
    def do_command_ieee_block(self, command, values):
       
        try:
            self.myprint("Cmd block = '%s'" % command)
            self.instr.write_binary_values("%s " % command, values, datatype='c')
            
            if self.alwayscheck:
                time.sleep(self.wdelay)
                self.check_instrument_errors(command)
            
        except Exception as e:
            self.exception(e)
            
        finally:
            time.sleep(self.wdelay)


    # =========================================================
    # Send a query, check for errors, return string:
    # =========================================================
    def do_query_string(self, query):

        try: # can cause VI_ERROR_TMO, so gate with "try"
            self.myprint("Qys = '%s'" % query)
            result = self.instr.query("%s" % query)
            
            if self.alwayscheck:
                time.sleep(self.wdelay)
                self.check_instrument_errors(query)
                
            return result
        except ValueError:
            self.print("Value Error has occured")
        except Exception as e:
            self.exception(e)

        finally:
            time.sleep(self.wdelay)
            
    # =========================================================
    # Send a query, check for errors, return floating-point value:
    # =========================================================
    def do_query_number(self, query):
        return float(self.do_query_string(query))


    # =========================================================
    # Send a query, check for errors, return binary values:
    # =========================================================
    def do_query_ieee_block(self, query):
        try:
            self.myprint("Qys = '%s'" % query)
            result = self.instr.query_binary_values("%s" % query, datatype='s')
            
            if self.alwayscheck:
                time.sleep(self.wdelay)
                self.check_instrument_errors(query)
                        
            return result[0]
        except Exception as e:
            self.exception(e)
        
        finally:
            time.sleep(self.wdelay)
            
    # =========================================================
    # Check for instrument errors:
    # =========================================================
    def check_instrument_errors(self, reference): # tested whether this clears the infiniivision TER bit, it doesn't

        while True:
            error_string = self.instr.query(":SYSTem:ERRor?")
            if error_string: # If there is an error string value.
               
                error_string = error_string.strip("ERROR: ") # remove that
                error_string = error_string.strip("+") # remove that
                
                if error_string.find("0", 0, 1) == -1: # Not "ERROR: 0  No Error"
                   self.myprint("ERROR: %s, reference: '%s'" % (error_string, reference))
                   self.myprint("i can see my house from up here")
                   self.exception(error_string + reference)

                else: # "No error"
                    break
            else: # :SYSTem:ERRor? should always return string.
               self.exception("Sys error no msg")



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    myinstr = thInstr(myprint=print)

    #todo: test all functions, or specify to run other module which does.. really!!
