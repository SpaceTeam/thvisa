#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## specific class for fieldfox VNA mode operations ##

Created on Sun May 02 2021

@author: thirschbuechler
"""

import numpy as np #math
#import matplotlib.pyplot as plt
import pandas as pd #tables
from pandas import DataFrame as df
from time import perf_counter

try:
    import fieldfox_thvisa as ff # import common functions
except:
    try:
        from thvisa import fieldfox_thvisa as ff # if called as module
    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


#-#-# module test #-#-#
testing=False # imports don't seem to traverse this before reaching EOF and complaining about undef_bool !?
if __name__ == '__main__': # test if called as executable, not as library    
    testing=True
    #tester()#since this is no fct definition, can't call this, also py has no forward-declaration option

class VNA(ff.fieldfox):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "TCPIP::K-N9914A-71670.local::inst0::INSTR" # TCPIP: full name since no autodetection 
    instrnamedef = "USB0::10893::23576::MY57271670::0::INSTR" # USB: not fullname required but whatever
    
        
    def __init__(self, instrname = instrnamedef, myprint = myprintdef, qdelay = 0, wdelay=0):
        ## set defaults or overrides as given to init() ##
        #super(VNA, self).super(fieldfox, self).instr.timeout = 10000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout" $$ does this really go here or into instr.timeout somehow..
        self.instrname=instrname 
        self.myprint=myprint
        self.qdelay=qdelay
        self.role="NA" # for super.setup()
        
        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(VNA, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) # call parent
        
        self.traces = []

        self.setup_done = False


    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        super(VNA, self).__exit__( exc_type, exc_value, tb) # call parent


    def setup(self, hard=True, numPoints = 1001, startFreq = 2.4E9, stopFreq = 2.5E9, ifbw=1E3, avgs=1, sourcepower = "high" ):
        
        # first set freq range
        super(VNA, self).setup(hard=hard, numPoints = numPoints, startFreq = startFreq, stopFreq = stopFreq, ifbw=ifbw, avgs=avgs) # call parent
        
        # common rf settings
        self.ifbw=ifbw
        self.sourcepower = sourcepower

        self.do_command("BWID " + str(self.ifbw))
        
        # then change stimulus
        if self.sourcepower=="high":
            self.do_command("SOUR:POW:ALC HIGH")#autolevel high
        elif self.sourcepower=="low":
            self.do_command("SOUR:POW:ALC low")#autolevel low
        else:
            raise Exception("manual sourcepower setting is not implemented and discouraged")
            # e.g. "max" is bad, since ADC overload in certain ranges on S11=0dB as well as in CAL - wtf
            #self.do_command("source:power " + str(self.sourcepower))#for manual control only
        
        self.setup_done = True


    def logmag_all(self):# for cal and so on
        for i in [1,2,3,4]:
            self.do_command("CALC:PAR"+str(i)+":SEL") # select trace
            self.do_command("calculate:format Mlog") # set logmag
            
            
    
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
        
        s2p_data = [df(self.abscissa)] # initialize collect array
        
        for trace in self.traces:
            # RE = trace[:,0]
            # IM = trace[:,1]
            S_dB = 20*np.log10( np.sqrt(trace[:,0]*trace[:,0] + trace[:,1]*trace[:,1]) )
            angle = -180/np.pi * (np.arctan(-trace[:,1] / trace[:,0])) # "-" to run into correct direction
            angle = np.unwrap(2*angle)/2
            s2p_data.append(df(S_dB))
            s2p_data.append(df(angle))
            
        
        s2p_frame = pd.concat(s2p_data, axis=1) # concat the collect-array
        s2pheader="# Hz S DB R 50"
        #s2p_frame = pd.concat([pd.DataFrame(pd.Series(s2pheader)),s2p_data], ignore_index=True) # add header for s2p readers
        s2p_frame.to_csv(filename, index=False, sep ='\t', header=[s2pheader, "", "", "", "", "", "", "", ""]) # save
        # notes:    abscissa is column not index so ignore index
        #           header is columname overwrite
        self.myprint("saved "+filename)
    
    
    def is_cal_d(self):
        """ - query cal status
            - return bool
            """
        res=self.do_query_string("sense:correction:user:state?")
        if int(res):#cast to int
            return 1
        else:
            return 0


    def cal_str(self):
        """ - query cal status
            - make str
            """
        return ("usercal is done?: "+str(self.is_cal_d()))


    def save_cal(self, prefix="", suffix=""):
    # Set and read error term data [:SENSe]:CORRection:COEFficient[:DATA]
    # http://ena.support.keysight.com/e5071c/manuals/webhelp/eng/programming/command_reference/sense/scpi_sense_ch_correction_coefficient_data.htm
    
        # common definitions
        fields = ["ES",#: Source match
                  "ER",#: Reflection tracking
                  "ED",#: Directivity
                  "EL",#: Load match
                  "ET"]#: Transmission tracking]
        
        Sparams=["11","22","21","12"]
        
        for Sparam in Sparams:
            # local definitions
            res=[]
            filename=prefix+"errterms_"+Sparam+suffix+".csv"
            rx_p=str(Sparam[1])
            tx_p=str(Sparam[0])
            
            # get cal
            for field in fields:
                res.append(self.do_query_string(("SENS1:CORR:COEF? "+field+","+rx_p+","+tx_p)).split(","))
            
            # save cal
            csv=pd.DataFrame.from_records(res).transpose()#from_records takes it into columns so transpose
            csv.columns=fields
            csv.to_csv(filename)
        
        
        
    

#### test this library using semi Unit Testing ####
if testing:
    
    with VNA() as myvna:
        myvna.ff_title("Hello")
        myvna.errcheck() # because why not
    
        myvna.ff_title("..testing VNA fieldfox class..")
        
        t1 = perf_counter() 
        myvna.do_sweeps()
        t2 = perf_counter()

        myvna.collect_traces()
        myvna.save_csv("dmu75-parkedleft-called_on-air_closeddoor.s2p")
        t3 = perf_counter()
        
        print("took {:.2f}s for sweeping, {:.2f}s for fetch 'n save".format(t2-t1,t3-t2))
        
        myvna.ff_title(myvna.cal_str())#empty titlebar
        
        print(myvna.query_setup())
