#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:37:06 2019

@author: thomas
"""
import time
import math
import thvisa as thv

class spd3303c(thv.thInstr):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "NPD"
    qdelaydef = 1
    
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef):
        self.qdelay=qdelay
        self.myprint=myprint
        self.instrname=instrname
        super(spd3303c, self).__init__(myprint=myprint, instrname=instrname, qdelay=qdelay) # call parent init 
        
        
    def set_settletime(self,newsettletime):
            self.settletime = newsettletime

    def set(self,
                ch1_en = float('nan'), # defaults if no arguments given
                ch2_en = float('nan'),
                ch1_volt = float('nan'),
                ch2_volt = float('nan'),
                ch1_clim = float('nan'),
                ch2_clim = float('nan'),
                newsettletime = -1
                ):

        if newsettletime < 0: # init case
            self.settletime = 0
        else:
            self.settletime = newsettletime

        if isinstance(ch1_en,bool):    #control output
            if(ch1_en):
                self.visa_write_delayed(self.instr,'OUTP CH1, ON')
                self.myprint('PSU channel 1 enabled')
            else:
                self.visa_write_delayed(self.instr,'OUTP CH1, OFF')
                self.myprint('PSU channel 1 disabled')

        if isinstance(ch2_en,bool):
            if(ch2_en):
                self.visa_write_delayed(self.instr,'OUTP CH2, ON')
                self.myprint('PSU channel 2 enabled')
            else:
                self.visa_write_delayed(self.instr,'OUTP CH2, OFF')
                self.myprint('PSU channel 2 disabled')

        #todo: typecast float and check
        if not math.isnan(ch1_volt):
            self.visa_write_delayed(self.instr,'CH1:VOLTage, %2.2f' % (ch1_volt))
            self.myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))

        if not math.isnan(ch2_volt):
            self.visa_write_delayed(self.instr,'CH2:VOLTage, %2.2f' % (ch2_volt))
            self.myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))

        if not math.isnan(ch1_clim):
            self.visa_write_delayed(self.instr,'CH1:CURRent, %2.2f' % (ch1_clim))
            self.myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))

        if not math.isnan(ch2_clim):
            self.visa_write_delayed(self.instr,'CH2:CURRent, %2.2f' % (ch2_clim))
            self.myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))


        # todo: use egg timer to avoid UI freeze
        if (ch1_en != float('nan') or ch2_en != float('nan')):
            time.sleep(self.settletime)

        # test for error while settings
        self.check_instrument_errors("psu_set")




### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #psu = spd3303c("NPD",qdelay=1,myprint=print)
    with spd3303c() as psu:
        print("hello")
        psu.set_settletime(1)
        psu.set(False,False)
        psu.set(ch1_clim =0.1,ch1_volt=30) #major range change to make it kachunck (relais action)
        psu.set(True,False)
        psu.set(ch1_clim =0.1,ch1_volt=5)
        psu.set(False,False)
    #del psu # the "with" context automatically calls the de-constructur and ends the sessoin
