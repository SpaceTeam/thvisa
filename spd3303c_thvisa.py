#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:37:06 2019

@author: thirschbuechler
"""
import time
import pandas as pd
import numpy as np
import thvisa as thv

# ToDo: check system:status? to find out whether in cc mode, i.e. limited 
# ToDo: series / parallel mode

# ----------------------------------------------------------------------- #
# ToDo: find out whether lock-mode exists (spam commands, ref. manual doesn't say)

# ToDo: check for human goblins (i.e. measure voltage each time after it
#           got set to verify it hasn't been changed while 1s in unlocked mode)
#       maybe as locklevel (0=none, 1=lock, 2=lock + while(not confirmed when locked))
#       aka level=[engineer, user, toddler]
# right now this is setp

class spd3303c(thv.thInstr):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "SPD"
    qdelaydef = 1
    
    
    
    # ----- Instrument Setup ----- #
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef, settletime=1):
        self.qdelay=qdelay
        self.myprint=myprint
        self.instrname=instrname
        self.settletime=settletime
        
        # call parent init #
        # the righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(spd3303c, self).__init__(myprint=myprint, instrname=instrname, qdelay=qdelay, wdelay = 0.1)
        self.alwayscheck=False # screw error checking every time, now we need wdelay=100ms instead of 10ms but are overall faster

        # define output state, should be off, but nonetheless:
        # can't do here, no handle open! make one with "with" or omit
        # self.disable(1)
        # self.disable(2)
        
    # ----- EXIT - With Context ----- #
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit
        self.do_command( "*unlock") # return full control, was partially locked anyhow
        super(spd3303c, self).__exit__( exc_type, exc_value, tb) # call inherited fct

    # -------------------------------------------------------- #
    # -------------------------------------------------------- #

    # ----- Importing the Testcases from a xlsx-File ----- #

    def load_testcases(self, fileName = 'cubesat_testcases_V0.1.xlsx'):
        
        self.testCases = pd.read_excel(fileName)

        # Renaming the Columns #

        colNameDic = list(self.testCases.iloc[0].values)
        self.testCases.columns = colNameDic

        self.testCases = self.testCases.drop([0],axis = 0)

        print(self.testCases.columns)
        print(self.testCases.iloc[1])

    # ----- Checking System-Status ----- #

    def check_systemstatus(self):
       
        # Could work, but could also be the case, that i need to convert the
        # hex-value which was returned, manually ( bin() )
        num = self.do_query_ieee_block('*SYSTem: STATus?')

        # Channel Power Switches (On or Off)
        switch_ch1, switch_ch2 = 'off'
        if(self.access_binarydigit(num,4)):
            switch_ch1 = 'on'
        if(self.access_binarydigit(num,5)):
            switch_ch1 = 'on'
        
        # Channel 1 - Mode (CV or CC)
        if(self.access_binarydigit(num,0)):
            self.myprint(f"Channel 1 is {switch_ch1} and in CC mode")
        else:
            self.myprint(f"Channel 1 is {switch_ch1} and in CV mode")

        # Channel 2 - Mode (CV or CC)
        if(self.access_binarydigit(num,1)):
            self.myprint(f"Channel 2 is {switch_ch2} and in CC mode")
        else:
            self.myprint(f"Channel 2 is {switch_ch2} and in CV mode")

        # PSU - Mode (independent, series or parallel)
        mode = self.access_binarydigit(num,2,True)
        mode_name = "independent"
        if(mode == bin(2)):
            mode_name = "parallel"
        elif (mode == bin(4)):
            mode_name = "serial"
        self.myprint(f"PSU is in {mode_name} mode")


    
    
    # --- Accessing digits of binary values ---
    # number: binary value you want to access digits of
    # index: index of the digits 
    # double (optional): False returns the bit with the index, 
    #                    True adds up bit with the index + the bit at position (index +1)
    def access_binarydigit(self,number = 1, index = 0, double = False):
        value = (number & (1 << index)) >> index
        if(double):
            return ((number & (1 << (index+1))) >> (index+1)) << value 
        else:
            return value


    # -------------------------------------------------------- #
    # -------------------------------------------------------- #

    # ----- Auxiliary Setup ----- #
    def set_settletime(self,newsettletime): 
            self.settletime = newsettletime # waittime for transients to settle

    def test_undoc_cmd(self): # no {preset, reset, factory, *rst, *cls, *tst, syst:pres, *OPC?} comands
        self.do_command("*unlock") # output can only be changed in unlocked state
        self.do_command( "*OPC?")
        #self.beep()
        
    def beep(self): # upset instrument by sending garbage
        self.do_command( "beep") # intentionally invalid command 


    # ----- Control Functions ----- #
    # outsourced from "set" to make user think whether to turn it on immediately after setting #        
    def output(self, ch, state=float("nan")):
        
        self.myprint('PSU channel {}:'.format(str(ch))) # ch = channel 
        #self.do_command("*unlock") # output can only be changed in unlocked state
        self.do_command('OUTP CH{}, {}'.format(str(ch), thv.statedict[state]))
        #self.do_command("*lock")
                
        # todo: $use eggtimer / mysleep to avoid UI freeze
        #time.sleep(self.settletime) # wait for off-transient

        
    # synonyms #
    def enable(self, ch):
        self.output(ch=ch, state=True)
        
    def disable(self, ch):
        self.output(ch=ch, state=False)


    # ----- Parameter Settings ----- #
    # per channel, since independent #
    def set(self, ch=float('nan'), v_set = float('nan'), c_max = float('nan')):
        
        self.myprint("Setting channel {} parameters:".format(str(ch)))
        
        self.do_command("*unlock") # output can only be changed in unlocked state
        self.do_command('CH%i:VOLTage, %2.2f' % (ch,v_set))
        self.do_command('CH%i:CURRent, %2.2f' % (ch,c_max))
        self.do_command("*lock") 
        


    # doesn't work due to dmm_results
    def setp(self, ch=float('nan'), v_set = float('nan'), c_max = float('nan')): # paranoid variant, assume someone may hit V/I wheel       
        while (not (self.DMM_results(ch)==[v_set,c_max])):
            self.set(ch , v_set, c_max)


    ## ---- DMM functions ---- ##
    # don't work reliably, for some reason, waiting doesn't seem to help,
    # also appends \n \x00 \x00 or something
    # approximate, take with grain of salt #
    def DMM_results(self, ch=float("nan")):
        
        #$todo if-else or switch-case
        v=self.do_query_number("Measure:Voltage? CH{}".format(str(ch)))
        time.sleep(1)
        c=self.do_query_number("Measure:Current? CH{}".format(str(ch)))
        time.sleep(1)
        
        self.myprint(v)
        self.myprint(c)
        return [float(v),float(c)]



### module test ###
if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    print("Step 0 - done")
    #psu = spd3303c("SPD",qdelay=1,myprint=print) # no, use with-context!
    with spd3303c() as psu:
        print("Entered successfully !")
        psu.set_settletime(1)
        print(print("Step 1 - done"))
        #psu.disable(1)
        print("Step 2 - done")
        #psu.disable(2)
        print("Step 3 - done")
        #psu.test_undoc_cmd()
        #print(psu.do_query_string("MEASure:VOLTage? CH{}".format(str(1))))
        #time.sleep(1)
        #print(psu.do_query_string("Measure:Voltage? CH{}".format(str(1))))
        print("major range change to make it kachunck")
        psu.set(ch=1, v_set=5, c_max=0.1)
        #print(psu.do_query_string("MEASure:VOLTage? CH{}".format(str(1))))
        psu.set(ch=2, v_set=5, c_max=0.1)
        #print(psu.do_query_string("Measure:Voltage? CH{}".format(str(2))))
        #print(psu.do_query_string("Measure:Voltage? CH{}".format(str(1))))
        #psu.enable(ch=1)
        
        #psu.set(ch=1, v_set=10, c_max=0.1)
        #print(psu.do_query_string("Measure:Voltage? CH{}".format(str(1))))
        #print(psu.do_query_string("Measure:Voltage? CH{}".format(str(1))))

        #psu.disable(ch=1)
    # del psu # the "with" context automatically calls the de-constructur and ends the session
    # please use it to avoid dead sessions, which result in the necessity to reboot the instrument and also the PC at times!!

