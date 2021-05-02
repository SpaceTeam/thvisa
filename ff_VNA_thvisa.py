#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## specific class for fieldfox VNA mode operations ##

Created on Sun May 02 2021

@author: thirschbuechler
"""

import fieldfox_thvisa as ff # import common functions
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ToDo: 
#- implement s2p transfer

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
        super(VNA, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) 



        ## definitions ##
        self.traces = []
        self.abszissa = []
        # abszissa
        self.numPoints = 1001
        self.startFreq = 2.4E9
        self.stopFreq = 2.5E9
        # further things
        self.ifbw=1E3
        self.avgs=1
        self.sourcepower = "high" # "max" - bad, since ADC overload in certain ranges on S11=0dB as well as in CAL - wtf


    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        super(VNA, self).__exit__( exc_type, exc_value, tb)


    # enable trigger and get data into instr memory#
    def do_sweeps(self, continous="off"):
        # Set trigger mode to hold for trigger synchronization
        #continous="off" # during measurement.. anyway
        self.do_command("INIT:CONT "+str(continous)+"")
        
        self.myprint("aquiring data "+str(self.avgs)+" times, acc. to avg")
        for i in range(self.avgs): # have to manually trigger each run for the averaging..
            ret = self.do_query_string("INIT:IMM")
            self.myprint("Single Trigger complete, *OPC? returned : " + ret)


    def make_abszissa(self):
        self.abszissa = np.linspace(float(self.startFreq),float(self.stopFreq),int(self.numPoints)) #SCPI "SENSe:X?" probably unsupported
        # however Read X-axis values possible via-     [:SENSe]:FREQuency:DATA?
        # Assert a single trigger and wait for trigger complete via *OPC? output of a 1


    def get_trace_mag(self, trace=1,save_trace=0):
        self.do_command("calculate:format mlog") # default - magnitude log # calc:sel:format
        '''
        % Trace 1 to measurement of S21 and select that measurement as active
        fprintf(fieldFox,'CALC:PAR1:DEF S21;SEL\n') ## does both calculate:paramater1:define s21 and calc:par1:sel
        % Hold off for operation complete to ensure settings
        fprintf(fieldFox,'*OPC?\n')
        '''

        self.do_command("CALC:PAR"+str(trace)+":SEL")

        trace_csv = self.do_query_string("CALC:DATA:FDATa?") # correct form was in programming examples not manual.. grumble grumble
        trace_data = trace_csv.split(",")
        
        if save_trace:
            a=pd.DataFrame(data={"f":self.abszissa, "Mag":trace_data})
            a.to_csv("trace"+trace+".csv", index=False)


        return trace_data


    def get_trace_(self, trace=1,save_trace=0):
        self.do_command("calculate:format polar") # polar gives mag+phase
        '''
        % Trace 1 to measurement of S21 and select that measurement as active
        fprintf(fieldFox,'CALC:PAR1:DEF S21;SEL\n') ## does both calculate:paramater1:define s21 and calc:par1:sel
        % Hold off for operation complete to ensure settings
        fprintf(fieldFox,'*OPC?\n')
        '''

        self.do_command("CALC:PAR"+str(trace)+":SEL")

        ff_csv = self.do_query_string("CALC:DATA:FDATa?") # correct form was in programming examples not manual.. grumble grumble
                        
        return ff_csv.split(",")

    # legacy function for MAG-only (default formatting)
    def collect_traces_mag(self):
        for i in [1,2,3,4]:
            self.traces.append(self.get_trace_mag(trace=i))


    def collect_traces(self):
        for i in [1,2,3,4]:
            self.traces.append(self.get_trace(trace=i))

    def plot_mag(self):
        fig, ax = plt.subplots()
        for trace in self.traces:
            y = np.array(trace).astype(np.float)
            ax.plot(self.abszissa,y)
            #ax.set_title (title)
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Magnitude (dB)")
            
        plt.show()



#### test this library using semi Unit Testing ####
if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    
    myvna = VNA() # read IDN
    myvna.errcheck() # because why not

    myvna.ff_title("..testing VNA fieldfox class..")

    #myvna.do_sweeps()
    myvna.make_abszissa()
    myvna.collect_traces_mag()
    myvna.plot_mag()

