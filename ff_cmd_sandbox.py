# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 13:58:10 2021

@author: hirschbuechler
"""

import numpy as np
import matplotlib.pyplot as plt
import pyvisa as visa#same as import visa apparently

#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library

    
    rm = visa.ResourceManager()
    myff = rm.open_resource("TCPIP::K-N9914A-71670.local::inst0::INSTR")#my fieldfox
    #Set Timeout - 10 seconds
    myff.timeout = 10000
    # Clear the event status registers and empty the error queue
    myff.write("*CLS")
    # Query identification string *IDN?
    myff.write("*IDN?")
    print(myff.read())
    # Define Error Check Function
    
    #myff.write("SYSTem?;*OPC?")
    myff.write("SYSTem:BEEP")
    myff.read()
    
 
    

    # byby handle
    myff.clear()
    myff.close()