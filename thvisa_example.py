#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 19:47:52 2019

@author: thirschbuechler
"""

# ToDo:
    # regex replace 3 capital letter words with lowercase (better readability)
    # this only matters to signify that the uppercase is needed
    # whilst the lowercase is for readability, but is used always anyway


import matplotlib.pyplot as plt
import InfiniiVision_thvisa as oscc
import spd3303c_thvisa as psuc

#fineexponents = np.vectorize(np.format_float_scientific) didn't work to auto-reformat a vector

def myplot(osc, ch):
    [times, voltages] = osc.data_dl(ch)
    plt.figure()
    plt.xticks(rotation=90)
    plt.xlabel("s")
    plt.ylabel("V")
    plt.plot(times,voltages)
    plt.show()



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    with oscc.InfiniiVision() as osc,  psuc.spd3303c() as psu:        
        #todo: insert code to measure test signal
        #todo: test all functions

        psu.set_settletime(1)
        psu.set(False,False)
        psu.set(ch1_clim =0.1,ch1_volt=30) #major range change to make it kachunck (relais action)
        psu.set(True,False)
        
        osc.setup_trigger_edge(ch=1,level=1.5,slope="positive")
        # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note
        osc.setup_channel(ch=1,scale=0.5,offset=1.5,probe=10.0)
        #osc.setup_channel(ch=2,scale=10,offset=0,probe=1.0) # probe is yellow coax
        osc.setup_channel(ch=2,scale=1,offset=0,probe=10.0) 

    
        # setup wgen
        osc.wgen_setup(fct="sinusoid",freq="2E3",VL=0.0,VH=3.0) # setup test signal
        osc.wgen_output(True)
    
        #osc.autoscale()
    
        # set horizontal scale
        osc.setup_timebase(scale=0.0002, pos=0.0)
    
        # aquire data with trigger type normal
        osc.capture(type="normal")
    
        psu.set(False,False)

    
        # get and plot
        myplot(osc,2)
        myplot(osc,1)
        
