#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:37:06 2019

@author: thirschbuechler
"""
import time
import thvisa as thv

# ToDo: check system:status? to find out whether in cc mode, i.e. limited
# ToDo: series / parallel mode
# ToDo: find out whether lock-mode exists (spam commands, ref. manual doesn't say)
# ToDo: check for human goblins (i.e. measure voltage each time after it
#           got set to verify it hasn't been changed while 1s in unlocked mode)
#       maybe as locklevel (0=none, 1=lock, 2=lock + while(not confirmed when locked))
#       aka level=[engineer, user, toddler]

class spd3303c(thv.thInstr):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "NPD"
    qdelaydef = 1
    
    
    ## instrument setup ##
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef, settletime=1):
        self.qdelay=qdelay
        self.myprint=myprint
        self.instrname=instrname
        self.settletime=settletime
        
        # call parent init #
        # the righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(spd3303c, self).__init__(myprint=myprint, instrname=instrname, qdelay=qdelay)
        
        # define output state, should be off, but nonetheless:
        # can't do here, no handle open! make one with "with" or omit
        # self.disable(1)
        # self.disable(2)
        
        
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit
        self.visa_write_delayed(self.instr, "*unlock") # return full control, was partially locked anyhow
        super(spd3303c, self).__exit__( exc_type, exc_value, tb) # call inherited fct

            
    # auxiliary setup #
    def set_settletime(self,newsettletime): 
            self.settletime = newsettletime # waittime for transients to settle

    def test_undoc_cmd(self): # no {preset, reset, factory, *rst, *cls, *tst, syst:pres, *OPC?} comands
        self.visa_write_delayed(self.instr,"*unlock") # output can only be changed in unlocked state
        self.visa_write_delayed(self.instr, "*OPC?")
        #self.beep()
        
    def beep(self): # upset instrument by sending garbage
        self.visa_write_delayed(self.instr, "beep")

    ## control functions ##
    # outsourced from "set" to make user think whether to turn it on immediately after setting #        
    def output(self, ch, state=float("nan")):
        self.myprint('PSU channel {}:'.format(str(ch)))
        self.visa_write_delayed(self.instr,"*unlock") # output can only be changed in unlocked state
        self.visa_write_delayed(self.instr,'OUTP CH{}, {}'.format(str(ch), thv.statedict[state]))
        self.visa_write_delayed(self.instr,"*lock")
                
        # todo: $use eggtimer / mysleep to avoid UI freeze
        time.sleep(self.settletime) # wait for off-transient
        
    # synonyms #
    def enable(self, ch):
        self.output(ch=ch, state=True)
        
    def disable(self, ch):
        self.output(ch=ch, state=False)


    ## parameter setting ##
    # per channel, since independent #
    def set(self, ch=float('nan'), v_set = float('nan'), c_max = float('nan') ):
        
        self.myprint("Setting channel {} parameters:".format(str(ch)))
        
        self.visa_write_delayed(self.instr,"*unlock") # output can only be changed in unlocked state
        self.visa_write_delayed(self.instr,'CH%i:VOLTage, %2.2f' % (ch,v_set))
        self.visa_write_delayed(self.instr,'CH%i:CURRent, %2.2f' % (ch,c_max))
        self.visa_write_delayed(self.instr,"*lock") 


        self.check_instrument_errors("psu_set") # test for error after setting things

    ## DMM functions ##
    # approximate, take with grain of salt #
    
    def DMM_results(self, ch=float("nan")):
        #$todo if-else or switch-case
        v=self.visa_write_delayed("Measure: Voltage? CH{}".format(str(ch)))
        c=self.visa_write_delayed("Measure: Current? CH{}".format(str(ch)))
        return [v,c]

### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #psu = spd3303c("NPD",qdelay=1,myprint=print) # no, use with-context!
    with spd3303c() as psu:
        psu.disable(1)
        psu.disable(2)
        #psu.test_undoc_cmd()
        
        print("major range change to make it kachunck")
        psu.set(ch=1, v_set=30, c_max=0.1)
        psu.set(ch=2, v_set=5, c_max=0.1)
        
        psu.enable(ch=1)
        psu.set(ch=1, v_set=5, c_max=0.1)
        
        psu.disable(ch=1)
    #del psu # the "with" context automatically calls the de-constructur and ends the session
    # please use it to avoid dead sessions, which result in the necessity to reboot the instrument and also the PC at times!!
