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
import InfiniiVision_thvisa


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

    osc=InfiniiVision_thvisa("CN5727",qdelay=0.5,myprint=print)

    osc.clear()
    osc.initialize()


    osc.setup_trigger_edge(ch=1,level=1.5,slope="positive"):
    # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note
    osc.setup_channel(ch=1,scale=0.5,offset=1.5,probe=10.0)
    osc.setup_channel(ch=2,scale=10,offset=0,probe=1.0)# probe is coax, actually

    # setup wgen
    osc.wgen_setup(fct="sinusoid",freq="2E3",VL=3.0,VH=0.0)   # setup test signal
    osc.wgen_output(True)

    #osc.autoscale()

    # set horizontal scale
    osc.setup_timebase(scale=0.0002, pos=0.0)

    # aquire data with trigger type normal
    osc.capture(type="normal")

    # get and plot
    myplot(osc,2)
    myplot(osc,1)
