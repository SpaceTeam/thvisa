#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## specific class for fieldfox VNA mode operations ##

Created on Sun May 02 2021

@author: thirschbuechler
"""

import fieldfox_thvisa as ff # import common functions
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame as df


class VNA(ff.fieldfox):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "TCPIP::K-N9914A-71670.local::inst0::INSTR" # full name since no autodetection 
    qdelaydef = 0.5 # initial query delay
        
    def __init__(self, instrname = instrnamedef, myprint = myprintdef, qdelay = qdelaydef):
         ## set defaults or overrides as given to init() ##
        #super(VNA, self).super(fieldfox, self).instr.timeout = 10000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout" $$ does this really go here or into instr.timeout somehow..
        self.instrname=instrname 
        self.myprint=myprint
        self.qdelay=qdelay
        
        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(VNA, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) # call parent

        ## definitions ##
        self.traces = []
        self.abscissa = []
        self.avgs=1 # default since always used

        self.setup_done = False


    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        super(VNA, self).__exit__( exc_type, exc_value, tb) # call parent


    def setup(self):
        # Preset the FieldFox  
        self.do_command("SYST:PRES")#"SYST:PRES;*OPC?" # docommand does opc inherited by fieldfox mainclass
        # Set mode to VNA   
        self.do_command("INST:SEL 'NA'")
        
                
        # abscissa
        self.numPoints = 1001
        self.startFreq = 2.4E9
        self.stopFreq = 2.5E9
        # further things
        self.ifbw=1E3
        self.avgs=1
        self.sourcepower = "high" # "max" - bad, since ADC overload in certain ranges on S11=0dB as well as in CAL - wtf
        
        
        ## msr setup ##
        self.do_command("SENS:SWE:POIN " + str(self.numPoints))
        self.do_command("SENS:FREQ:START " + str(self.startFreq))
        self.do_command("SENS:FREQ:STOP " + str(self.stopFreq))
        self.do_command("BWID " + str(self.ifbw))
        self.do_command("source:power " + str(self.sourcepower))
        self.do_command("AVER:COUNt " + str(self.avgs))
        
        self.setup_done = True


    # enable trigger and get data into instr memory
    def do_sweeps(self, continous="off"):
        # Set trigger mode to hold for trigger synchronization
        #continous="off" # during measurement.. anyway
        self.do_command("INIT:CONT "+str(continous)+"")
        
        self.myprint("aquiring data "+str(self.avgs)+" times, acc. to avg")
        for i in range(self.avgs): # have to manually trigger each run for the averaging..
            ret = self.do_command("INIT:IMM")  # opc baked into do_command
            self.myprint("Single Trigger complete, *OPC? returned : " + ret)


    def make_abscissa(self):
        if not self.setup_done:
            self.numPoints=self.do_query_string("SENS:SWE:POIN?")
            self.startFreq=self.do_query_string("SENS:FREQ:START?")
            self.stopFreq=self.do_query_string("SENS:FREQ:STOP?")
            
        # build
        self.abscissa = np.linspace(float(self.startFreq),float(self.stopFreq),int(self.numPoints)) 
        # notes
            #SCPI "SENSe:X?" probably unsupported
            # however Read X-axis values possible via-     [:SENSe]:FREQuency:DATA?


    def get_trace(self, trace=1):
        self.do_command("CALC:PAR"+str(trace)+":SEL") # select trace
        smiths = [1,4]
        
        if trace in smiths :
            self.do_command("calculate:format smith") # pretty smith
        else:
            self.do_command("calculate:format polar") # polar gives mag+phase of Gamma (linear)
        
  
        # p302 - format:data
        # p200 - calc:data:fdata: undefined for polar and smith. fdata - formatted display (mag only)
        # slight differences in decimals: aquisition - 
        #                           search online manual for "Data Chain: Standard vs 8510"
        #                           http://na.support.keysight.com/fieldfox/help/SupHelp/FieldFox.htm
        trace_csv = self.do_query_string("CALC:DATA:SDATa?")  # sdata - unformatted real+imag :)
        trace_data = np.array(trace_csv.split(",")).astype(float)
        trace_data=np.reshape(trace_data,(-1,2)) # now y1+y2 sit in same row
        
        return trace_data # k x 2 matrix


    def collect_traces(self):
        for i in [1,2,3,4]:
            self.traces.append(self.get_trace(trace=i))
            
        self.make_abscissa() #afterwards, to not prolong with aquisition if setup_done==True

    
    def save_csv(self,filename):
        
        s2p_data = [df(self.abscissa)] # initialize concatenation array
        
        for trace in self.traces:
            # RE = trace[:,0]
            # IM = trace[:,1]
            S_dB = 20*np.log10( np.sqrt(trace[:,0]*trace[:,0] + trace[:,1]*trace[:,1]) )
            angle = 180/np.pi * (np.arctan(-trace[:,1] / trace[:,0])) #np.unwrap doesn't change anything; still different wrapping
            s2p_data.append(df(S_dB))
            s2p_data.append(df(angle))
            
        
        s2p_frame = pd.concat(s2p_data, axis=1) # concat the concat array
        s2p_frame.to_csv(filename, index=False, sep ='\t', header=False) # save
        # notes:    abscissa is column not index so ignore index
        #           header is columname overwrite
    



#### test this library using semi Unit Testing ####
if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    
    myvna = VNA() # read IDN
    myvna.errcheck() # because why not

    myvna.ff_title("..testing VNA fieldfox class..")

    myvna.do_sweeps()
    
    myvna.collect_traces()
    myvna.save_csv("bb.s2p")
