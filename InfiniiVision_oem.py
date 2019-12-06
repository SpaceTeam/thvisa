#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 19:47:52 2019

@author: thirschbuechler
"""

# ToDo:
# replace do_command with obj. oriented call
# regex replace 3 capital letter words with lowercase (better readability)

import struct
import numpy as np
import matplotlib.pyplot as plt

import thvisa


# global variables
debug = 1



def osc_wgen_setup():
    do_command(":WGEN:MODulation:FUNCtion SINusoid")
    do_command(":WGEN:FREQuency 2E3")
    do_command(":WGEN:VOLTage:HIGH 3.0")
    do_command(":WGEN:VOLTage:LOW 0.0")
    #do_command(":WGEN:VOLTage:LOW 3.0")
    

def osc_wgen_output(out_enable):
    if out_enable:
        do_command(":WGEN:OUTPut ON")
    else:
        do_command(":WGEN:OUTPut OFF")
    
    
# =========================================================
# Initialize:
# =========================================================
def initialize():
    # Get and display the device's *IDN? string.
    idn_string = do_query_string("*IDN?")
    print("Identification string: '%s'" % idn_string)
    # Clear status and load the default setup.
    do_command("*CLS")
    do_command("*RST")


def setupTestcase():
    # Set trigger mode.
    do_command(":TRIGger:MODE EDGE")

    # Set EDGE trigger parameters.
    do_command(":TRIGger:EDGE:SOURce CHANnel1")

    do_command(":TRIGger:EDGE:LEVel 1.5") # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note

    do_command(":TRIGger:EDGE:SLOPe POSitive")

    
    # Set probe attenuation factor.
    do_command(":CHANnel1:PROBe 10.0")

    
    # Set vertical scale and offset.
    do_command(":CHANnel1:SCALe 0.5")
    do_command(":CHANnel1:OFFSet 1.5")
    
    do_command(":CHANnel2:SCALe 10")
    do_command(":CHANnel2:OFFSet 0")
    do_command(":CHANnel2:PROBe 1.0") # is coax
    
    
    # Set horizontal scale and offset.
    do_command(":TIMebase:SCALe 0.005")

    do_command(":TIMebase:POSition 0.0")
 
    do_command(":MEASure:SOURce CHANnel1")


# =========================================================
# Capture:
# =========================================================
def capture():
    
    # Use auto-scale to automatically set up oscilloscope.
    print("Autoscale.")
    do_command(":AUToscale")
    
    # Set trigger mode.
    do_command(":TRIGger:MODE EDGE")

    
    # Set EDGE trigger parameters.
    do_command(":TRIGger:EDGE:SOURce CHANnel1")
    do_command(":TRIGger:EDGE:LEVel 1.5")
    do_command(":TRIGger:EDGE:SLOPe POSitive")
  
    
    # Change oscilloscope settings with individual commands:
    # Set vertical scale and offset.
    do_command(":CHANnel1:SCALe 1")
    do_command(":CHANnel1:OFFSet 0")
    
    # Set horizontal scale and offset.
    do_command(":TIMebase:SCALe 0.0002")
    do_command(":TIMebase:POSition 0.0")

    
    # Set the acquisition type.
    do_command(":ACQuire:TYPE NORMal")
    
#    # Or, set up oscilloscope by loading a previously saved setup.
#    sSetup = ""
#    f = open("setup.stp", "rb")
#    sSetup = f.read()
#    f.close()
#    do_command_ieee_block(":SYSTem:SETup", sSetup)
#    print("Setup bytes restored: %d" % len(sSetup))
    
    # make an acquisition using :DIGitize of just one channel
    #do_command(":DIGitize CHANnel1")
    do_command(":digitize")
    
    
# =========================================================
# Analyze:
# =========================================================
def analyzetest():
    #do_command(":MEASure:SOURce CHANnel1")
    #qresult = do_query_string(":MEASure:SOURce?")
    #print("Measure source: %s" % qresult)
    do_command(":MEASure:VAMPlitude")
    qresult = do_query_string(":MEASure:VAMPlitude?")
    #print("Measured vertical amplitude on channel 1: %s" % qresult)
    return qresult
    

#fineexponents = np.vectorize(np.format_float_scientific) didn't work to auto-reformat a vector

def screenie():
    # Download the screen image.
    # --------------------------------------------------------
    do_command(":HARDcopy:INKSaver OFF")
    
    sDisplay = do_query_ieee_block(":DISPlay:DATA? PNG, COLor")
    
    # Save display data values to file.
    f = open("screen_image.png", "wb")
    f.write(sDisplay)
    f.close()
    print("Screen image written to screen_image.png.")


def store_oszi_setup():
    # Save oscilloscope setup.
    sSetup = do_query_ieee_block(":SYSTem:SETup?")
    f = open("setup.stp", "wb")
    f.write(sSetup)
    f.close()
    print("Setup bytes saved: %d" % len(sSetup))
    
    
def analyze(channel=1):
    print("### getting channel "+str(channel)+" ###")
    
    # Make measurements.
    # --------------------------------------------------------
    #do_command(":MEASure:SOURce CHANnel"+str(channel))
    #do_command(":MEASure:FREQuency")
    #do_command(":MEASure:VAMPlitude")

    #screenie()
    data_dl(channel)


def data_dl(channel=1):
    # Download waveform data.
    # --------------------------------------------------------
    # Set the waveform points mode.
    do_command(":WAVeform:POINts:MODE RAW")

    
    # Get the number of waveform points available.
    do_command(":WAVeform:POINts 10240")
    
    # Set the waveform source before getting data, it is already saved in instrument, but specify what to get
    do_command(":WAVeform:SOURce CHANnel"+str(channel))

    # Choose the format of the data returned:
    do_command(":WAVeform:FORMat BYTE")

    
    # Display the waveform settings from preamble:
    wav_form_dict = {
        0 : "BYTE",
        1 : "WORD",
        4 : "ASCii",
    }
    acq_type_dict = {
        0 : "NORMal",
        1 : "PEAK",
        2 : "AVERage",
        3 : "HRESolution",
    }

    preamble_string = do_query_string(":WAVeform:PREamble?")
    (
        wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
        x_reference, y_increment, y_origin, y_reference
#    ) = string.split(preamble_string, ",")
    ) = preamble_string.split(",")
    
    print("Waveform format: %s" % wav_form_dict[int(wav_form)])
    print("Acquire type: %s" % acq_type_dict[int(acq_type)])
    print("Waveform points desired: %s" % wfmpts)
    print("Waveform average count: %s" % avgcnt)
    print("Waveform X increment: %s" % x_increment)
    print("Waveform X origin: %s" % x_origin)
    print("Waveform X reference: %s" % x_reference) # Always 0.
    print("Waveform Y increment: %s" % y_increment)
    print("Waveform Y origin: %s" % y_origin)
    print("Waveform Y reference: %s" % y_reference)
    
    # Get numeric values for later calculations.
    x_increment = do_query_number(":WAVeform:XINCrement?")
    x_origin = do_query_number(":WAVeform:XORigin?")
    y_increment = do_query_number(":WAVeform:YINCrement?")
    y_origin = do_query_number(":WAVeform:YORigin?")
    y_reference = do_query_number(":WAVeform:YREFerence?")
    
    # Get the waveform data.
    sData = do_query_ieee_block(":WAVeform:DATA?")
    
    # Unpack unsigned byte data.
    values = struct.unpack("%dB" % len(sData), sData)
    print("Number of data values: %d" % len(values))
    
    # make data vectors
    times=  + np.arange(x_origin,x_origin+len(values)*x_increment,x_increment)
    onevector = np.ones(len(values))
    voltages = ((values - y_reference*onevector) )*y_increment + y_origin*onevector
   
    # plot
    plt.figure()
    plt.xticks(rotation=90)
    plt.xlabel("s")
    plt.ylabel("V")
    plt.plot(times,voltages)
    plt.show()



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    global instr
    
    thvisa.init()

    instr=0
    instr=thvisa.getinstrument("CN5727",0.5)
    
    
    instr.timeout = 15000 # https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout
    instr.clear()
    # Initialize the oscilloscope, capture data, and analyze.
    initialize()
    setupTestcase()
    
    osc_wgen_setup()   #enable the test signal
    osc_wgen_output(True) #make sure it is on

    capture()
    
    analyze(2)
    analyze(1)
    