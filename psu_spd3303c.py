#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 16:54:04 2019

@author: thirschbuechler
"""


import pyvisa as visa

import math #nan-strings
import time #waiting

# global vars
myprint = print # pointer to redirect output of print, if desired
settletime = 0 #seconds

# fcts
def visa_write_delayed(visa,msg,wait_time_ms = 100):
    err_flag = visa.write(msg)
    time.sleep(wait_time_ms/1000)
    return err_flag

def set_settletime(newsettletime):
    global settletime
    try:
        settletime = newsettletime
    except:
        myprint("failed to set settling time")

def psu_set(PSU_visa, 
            ch1_en = float('nan'), 
            ch2_en = float('nan'),
            ch1_volt = float('nan'),
            ch2_volt = float('nan'),
            ch1_clim = float('nan'),
            ch2_clim = float('nan'),
            verbose = False
            ):
    global settletime;
    error_flag = False;

    if isinstance(ch1_en,bool):    #control output
        if(ch1_en):
            visa_write_delayed(PSU_visa,'OUTP CH1, ON')   
            if(verbose) : myprint('PSU channel 1 enabled')
        else:
            visa_write_delayed(PSU_visa,'OUTP CH1, OFF')
            if(verbose) : myprint('PSU channel 1 disabled')
            
    if isinstance(ch2_en,bool):
        if(ch2_en):
            visa_write_delayed(PSU_visa,'OUTP CH2, ON')   
            if(verbose) : myprint('PSU channel 2 enabled')
        else:
            visa_write_delayed(PSU_visa,'OUTP CH2, OFF')        
            if(verbose) : myprint('PSU channel 2 disabled')
                
    #todo: typecast float and check                   
    if not math.isnan(ch1_volt):
        visa_write_delayed(PSU_visa,'CH1:VOLTage, %2.2f' % (ch1_volt))
        if(verbose) : myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))
        
    if not math.isnan(ch2_volt):
        visa_write_delayed(PSU_visa,'CH2:VOLTage, %2.2f' % (ch2_volt))
        if(verbose) : myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))

    if not math.isnan(ch1_clim):
        visa_write_delayed(PSU_visa,'CH1:CURRent, %2.2f' % (ch1_clim))
        if(verbose) : myprint('PSU channel 1 set to %2.2fV' % (ch1_volt))
        
    if not math.isnan(ch2_clim):
        visa_write_delayed(PSU_visa,'CH2:CURRent, %2.2f' % (ch2_clim))
        if(verbose) : myprint('PSU channel 2 set to %2.2fV' % (ch2_volt))
        
        
    if (ch1_en != float('nan') or ch2_en != float('nan')):
        time.sleep(settletime)
        
    #test for error while settings    
    #visa_write_delayed(PSU_visa,'SYSTem: ERRor?')
    error_msg = PSU_visa.query('SYSTem:ERRor?')
    error_flag = error_flag or bool(int(error_msg[0]))
    if error_flag : myprint('setting the PSU returned an error')
        
    #myprint what is going on
    return error_flag



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    #rm = visa.ResourceManager()
    #rm.close()# doesn't help on busy ressource
    
    rm = visa.ResourceManager()
    visa_res = rm.list_resources()
    myprint(visa_res)

    #open the PSU
    myprint("say hello")
    # PSU 03 USB0::1155::30016::NPD3ECAC2R0019::0::INSTR
    visa_PSU = rm.open_resource('USB0::0x0483::0x7540::NPD3ECAC2R0019::INSTR', query_delay = 0.5)   
    myprint(visa_PSU)
    myprint(visa_PSU.query('*IDN?'))
    
    set_settletime(1)
        
    psu_set(visa_PSU,False,False)
    psu_set(visa_PSU,ch1_clim =0.1,ch1_volt=30) #major range change to make it kachunck (relais action)
    psu_set(visa_PSU,True,False) 
    psu_set(visa_PSU,ch1_clim =0.1,ch1_volt=5)
    psu_set(visa_PSU,False,False) 
    
    visa_PSU.close()
    del visa_PSU