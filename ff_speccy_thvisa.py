#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## specific class for fieldfox speccy (spectrum analyzer) mode operations ##

Created on 29.7.2021

@author: thirschbuechler
"""

import numpy as np #math
#import matplotlib.pyplot as plt
import pandas as pd #tables
from pandas import DataFrame as df
from time import perf_counter

#-#-# module test #-#-#
testing=False # imports don't seem to traverse this before reaching EOF and complaining about undef_bool !?
if __name__ == '__main__': # test if called as executable, not as library    
    testing=True
    #tester()#since this is no fct definition, can't call this, also py has no forward-declaration option

try:
    import fieldfox_thvisa as ff # import common functions
except:
    try:
        import thvisa.fieldfox_thvisa as ff # if called as module
    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


class speccy(ff.fieldfox):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "TCPIP::K-N9914A-71670.local::inst0::INSTR" # TCPIP: full name since no autodetection 
    instrnamedef = "USB0::10893::23576::MY57271670::0::INSTR" # USB: not fullname required but whatever
    
    
    def __init__(self, instrname = instrnamedef, myprint = myprintdef, qdelay = 0, wdelay=0):
        ## set defaults or overrides as given to init() ##
        #super(speccy, self).super(fieldfox, self).instr.timeout = 10000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout" $$ does this really go here or into instr.timeout somehow..
        self.instrname=instrname 
        self.myprint=myprint
        self.qdelay=qdelay
        self.role="SA" # for super.setup()
        
        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(speccy, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) # call parent

        self.traces = []
        
        self.setup_done = False


    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        super(speccy, self).__exit__( exc_type, exc_value, tb) # call parent


    def setup(self, hard=True, numPoints = 1001, startFreq = 2.4E9, stopFreq = 2.5E9, span="", avgs=1):
        super(speccy, self).setup(hard=hard, numPoints = numPoints, startFreq = startFreq, stopFreq = stopFreq, avgs=avgs) # call parent
        
        if span!="":
            self.span = span
            self.do_command("FREQ:SPAN " + str(self.span))

        self.setup_done = True


    def set_sweeptime(self,stime):
        """ 
        SWEep:ACQuisition <num>
        (Read-Write) Set and query the sweep acquisition parameter. This effectively sets the sweep time in SA
        mode. Adjust this setting in order to increase the probability of intercepting and viewing pulsed RF
        signals. (page 450)

            Also set [:SENSe]:SWEep:ACQuisition:AUTO to 0 (OFF).Command Reference
        
            Relevant Modes SA, RTSA
        Parameters
        - <num> Choose a relative acquisition value between 1 and 5000, where:
        - 1 = Fastest sweep possible
        - 5,000 = Slowest sweep possible.

        Examples SWE:ACQ 25

        Default 1
        """

        if int(self.span)!=0:
            raise Exception("can't set time unless Zero span!")

        self.do_command("SWEP:ACQ " + str(self.stime))#sweep:aquisition      
        self.stime=stime  


    def get_sweeptime(self):
        """ 
        [:SENSe]:SWEep:ACQuisition <num>
        (Read-Write) Set and query the sweep acquisition parameter. This effectively sets the sweep time in SA
        mode. Adjust this setting in order to increase the probability of intercepting and viewing pulsed RF
        signals. (page 450)

            Also set [:SENSe]:SWEep:ACQuisition:AUTO to 0 (OFF).Command Reference
        
            Relevant Modes SA, RTSA
        Parameters
        - <num> Choose a relative acquisition value between 1 and 5000, where:
        - 1 = Fastest sweep possible
        - 5,000 = Slowest sweep possible.

        Examples SWE:ACQ 25
        
        Query Syntax [:SENSe]:SWEep:ACQuisition?
        
        Return Type Numeric
        
        Default 1
        """
        
        #if int(self.span)!=0: # getting f-sweep time is probably possible as well
        #    raise Exception("can't get sweep time unless Zero span!")
    
        stime=self.do_query_string("SENS:sweep:acq?")#sense:sweep:aquisition
        self.stime=stime
        return stime


    def get_trace(self):
        """ get SA trace """
        trace_csv = self.do_query_string("TRACE:DATA?")
        trace_data = np.array(trace_csv.split(",")).astype(float)
        #trace_data=np.reshape(trace_data,(-1,2)) # now y1+y2 sit in same row
        
        return trace_data # k x 2 matrix


    def collect_traces(self):
        """ collect trace, same naming as in NA """
        self.traces=[]
        self.traces.append(self.get_trace())
        self.make_abscissa() #afterwards, to not prolong with aquisition if setup_done==True


    def save_csv(self,filename):
        """ save SA data - strictly speaking no dB but dBm but whatevs """ # HACK see if it works
        
        s2p_data = [df(self.abscissa)] # initialize concatenation array
        
        for trace in self.traces:
            # RE = trace[:,0]
            # IM = trace[:,1]
            #S_dB = 20*np.log10( np.sqrt(trace[:,0]*trace[:,0] + trace[:,1]*trace[:,1]) )
            #angle = 180/np.pi * (np.arctan(-trace[:,1] / trace[:,0])) #np.unwrap doesn't change anything; still different wrapping
            #s2p_data.append(df(S_dB))
            #s2p_data.append(df(angle))
            s2p_data.append(df(trace))
        
        
        s2p_frame = pd.concat(s2p_data, axis=1) # concat the concat array
        s2p_frame.to_csv(filename, index=False, sep ='\t', header=False) # save
        # notes:    abscissa is column not index so ignore index
        #           header is columname overwrite
        self.myprint("saved "+filename)


#### test this library using semi Unit Testing ####
if testing:
    
    with speccy() as spek:
        spek.ff_title("Hello")
        spek.errcheck() # because why not
    
        spek.ff_title("..testing speccy fieldfox class..")
        
        t1 = perf_counter() 
        spek.do_sweeps()
        t2 = perf_counter()

        spek.collect_traces()
        spek.save_csv("SA_data.csv")
        t3 = perf_counter()
        
        print("took {:.2f}s for sweeping, {:.2f}s for fetch 'n save".format(t2-t1,t3-t2))
        
        spek.ff_title(myvspekna.cal_str())#empty titlebar
        
        print(spek.query_setup())