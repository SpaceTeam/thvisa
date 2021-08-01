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
        #self.span="" # for zerospan checks lateron, needs init by setup() # nope do it here after "super"
        

        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(speccy, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) # call parent

        # we have an instrument, ask for the span, needs to be init for span-checks
        self.span=self.do_query_string("FREQ:SPAN?")
        self.traces = []
        
        self.setup_done = False


    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        super(speccy, self).__exit__( exc_type, exc_value, tb) # call parent


    def setup(self, hard=True, numPoints = 1001, startFreq = 2.4E9, stopFreq = 2.5E9, span="", centerfreq="", avgs=1):
        super(speccy, self).setup(hard=hard, numPoints = numPoints, startFreq = startFreq, stopFreq = stopFreq, avgs=avgs) # call parent
        
        # case span n centerfreq given (probably zerospan)
        if span!="":
            self.span = span
            self.centerfreq=centerfreq
            self.do_command("FREQ:SPAN " + str(self.span))
            self.do_command("FREQ:center {}".format(str(self.centerfreq)))

        self.setup_done = True


    def set_fd_sweeptime(self,stime):
        """ 
        SWEep:ACQuisition <num>
        (Read-Write) Set and query the sweep acquisition parameter. This effectively sets the sweep time in SA
        mode. Adjust this setting in order to increase the probability of intercepting and viewing pulsed RF
        signals. (page 450)

            Also set [:SENSe]:SWEep:ACQuisition:AUTO to 0 (OFF).Command Reference
        
            Relevant Modes SA, RTSA, NOT ZEROSPAN
        Parameters
        - <num> Choose a relative acquisition value between 1 and 5000, where:
        - 1 = Fastest sweep possible
        - 5,000 = Slowest sweep possible.

        Examples SWE:ACQ 25

        Default 1
        """

        if int(self.span)==0:
            raise Exception("use non-fd version of this command (or update self.span)!")

        # note: "sweep" needs to be written out, "SWE" seems to not work
        self.do_command("sweep:ACQ:AUTO 0") # $HACK dunno whether this is necessary
        self.do_command("sweep:ACQ " + str(stime))#sweep:aquisition      
        
        self.stime=stime  


    def get_fd_sweeptime(self):
        """ 
        [:SENSe]:SWEep:ACQuisition <num>
        (Read-Write) Set and query the sweep acquisition parameter. This effectively sets the sweep time in SA
        mode. Adjust this setting in order to increase the probability of intercepting and viewing pulsed RF
        signals. (page 450)

            Also set [:SENSe]:SWEep:ACQuisition:AUTO to 0 (OFF).Command Reference
        
            Relevant Modes SA, RTSA, NOT ZEROSPAN
        Parameters
        - <num> Choose a relative acquisition value between 1 and 5000, where:
        - 1 = Fastest sweep possible
        - 5,000 = Slowest sweep possible.

        Examples SWE:ACQ 25
        
        Query Syntax [:SENSe]:SWEep:ACQuisition?
        
        Return Type Numeric
        
        Default 1
        """

        if int(self.span)==0:
            raise Exception("use non-fd version of this command (or update self.span)!")        
    
        stime=self.do_query_string("SENS:sweep:acq?")#sense:sweep:aquisition
        self.stime=stime
        return stime


    def get_sweeptime(self):
        """ 
        [:SENSe]:SWEep:TIME <num>
        (Read-Write) Set and query the sweep time of the measurement. The actual sweep time that is displayed
        on the screen will usually be higher than this value due to the overhead sweep time.
        
        In SA mode, use this command for Zerospan measurements.
        To set and read sweep time for Non-zerospan measurements in SA mode, use
        [:SENSe]:SWEep:ACQuisition.
        
        Relevant Modes CAT, NA, SA, RTSA
        Parameters
        <num> Sweep time in seconds.
        
        Examples SWE:TIME .250
        Query Syntax [:SENSe]:SWEep:TIME?
        
        Return Type Numeric
        Default 0
        """

        if int(self.span)!=0:
            raise Exception("use fd version of this command (or update self.span)!")        
    
        stime=self.do_query_string("SENS:sweep:time?")
        self.stime=stime
        return stime


    def set_sweeptime(self,stime):
        """ 
        [:SENSe]:SWEep:TIME <num>
        (Read-Write) Set and query the sweep time of the measurement. The actual sweep time that is displayed
        on the screen will usually be higher than this value due to the overhead sweep time.
        
        In SA mode, use this command for Zerospan measurements.
        To set and read sweep time for Non-zerospan measurements in SA mode, use
        [:SENSe]:SWEep:ACQuisition.
        
        Relevant Modes CAT, NA, SA, RTSA
        Parameters
        <num> Sweep time in seconds.
        
        Examples SWE:TIME .250
        Query Syntax [:SENSe]:SWEep:TIME?
        
        Return Type Numeric
        Default 0
        """

        if int(self.span)!=0:
            raise Exception("use fd version of this command (or update self.span)!")        
    
        stime=self.do_command("SENS:sweep:time {}".format(str(stime)))
        self.stime=stime


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
        if self.span!=0:
            self.make_abscissa() #afterwards, to not prolong with aquisition if setup_done==True
        else:
            self.make_t_abscissa()


    def make_t_abscissa(self):
        """ fetch t-axis stuff from SA 
            (sidenote: zerospan csv export on fieldfox yields no usable axis)
        """
        if not self.setup_done:
            self.numPoints=self.do_query_string("SENS:SWE:POIN?")
            self.centerfreq=self.do_query_string("SENS:FREQ:center?")

        # always get:    
        self.get_sweeptime()#self.stime
            
        # build
        self.abscissa = np.linspace(float(0),float(self.stime),int(self.numPoints)) 
    

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
        
        spek.ff_title(spek.cal_str())#empty titlebar
        
        print(spek.query_setup())