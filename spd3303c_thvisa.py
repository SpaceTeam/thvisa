#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:37:06 2019

@author: thomas
"""

import thvisa as thv

class spd3303c(thv.thInstr):
    self.settletime = 0 #seconds

    def set_settletime(newsettletime):
            self.settletime = newsettletime

    def set(self.instr,
                ch1_en = float('nan'), # defaults if no arguments given
                ch2_en = float('nan'),
                ch1_volt = float('nan'),
                ch2_volt = float('nan'),
                ch1_clim = float('nan'),
                ch2_clim = float('nan'),
                newsettletime = self.settletime
                ):

        self.settletime = newsettletime

        if isinstance(ch1_en,bool):    #control output
            if(ch1_en):
                visa_write_delayed(self.instr,'OUTP CH1, ON')
                myprint('PSU channel 1 enabled')
            else:
                visa_write_delayed(self.instr,'OUTP CH1, OFF')
                myprint('PSU channel 1 disabled')

        if isinstance(ch2_en,bool):
            if(ch2_en):
                visa_write_delayed(self.instr,'OUTP CH2, ON')
                myprint('PSU channel 2 enabled')
            else:
                visa_write_delayed(self.instr,'OUTP CH2, OFF')
                myprint('PSU channel 2 disabled')

        #todo: typecast float and check
        if not math.isnan(ch1_volt):
            visa_write_delayed(self.instr,'CH1:VOLTage, %2.2f' % (ch1_volt))
            myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))

        if not math.isnan(ch2_volt):
            visa_write_delayed(self.instr,'CH2:VOLTage, %2.2f' % (ch2_volt))
            myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))

        if not math.isnan(ch1_clim):
            visa_write_delayed(self.instr,'CH1:CURRent, %2.2f' % (ch1_clim))
            myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))

        if not math.isnan(ch2_clim):
            visa_write_delayed(self.instr,'CH2:CURRent, %2.2f' % (ch2_clim))
            myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))


        # todo: use egg timer to avoid UI freeze
        if (ch1_en != float('nan') or ch2_en != float('nan')):
            time.sleep(self.settletime)

        # test for error while settings
        self.check_instrument_errors()




### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    psu=spd3303c_thvisa("NPD",qdelay=0.5,myprint=print)

    psu.set_settletime(1)

    psu.set(visa_PSU,False,False)
    psu.set(visa_PSU,ch1_clim =0.1,ch1_volt=30) #major range change to make it kachunck (relais action)
    psu.set(visa_PSU,True,False)
    psu.set(visa_PSU,ch1_clim =0.1,ch1_volt=5)
    psu.set(visa_PSU,False,False)
