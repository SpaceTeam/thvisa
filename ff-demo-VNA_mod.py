# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 13:58:10 2021

@author: thirschbuechler
"""

import numpy as np
import matplotlib.pyplot as plt
import pyvisa as visa
import pandas as pd


## definitions ##

numPoints = 1001
startFreq = 2.4E9
stopFreq = 2.5E9
ifbw=1E3
avgs=1
sourcepower = "high" # "max" - bad, since ADC overload in certain ranges on S11=0dB as well as in CAL - wtf
setup=False
dosweep=False


debug = True
do_fail = False
release = False # continous sweep after done?
continous="off" # during measurement.. anyway
save_trace = False


## functions ##

def myprint(args, **kwargs):
    if debug:
        print(args, **kwargs)

def Errcheck():
    myError = []
    ErrorList = myff.query("SYST:ERR?").split(',')
    Error = ErrorList[0]
    if int(Error) == 0:
        myprint ("+0, No Error!")
    else:
        while int(Error)!=0:
            myprint ("Error #: " + ErrorList[0])
            myprint ("Error Description: " + ErrorList[1])
            myError.append(ErrorList[0])
            myError.append(ErrorList[1])
            ErrorList = myff.query("SYST:ERR?").split(',')
            Error = ErrorList[0]
            myError = list(myError)
    return myError

def plot_ff(abszissa,csv_array, title="aquired data"):
    
    
    maxResponseVal= max(csv_array)
    minResponseVal = min(csv_array)
    
    myprint("Max value = " + maxResponseVal + " Min Value = " + minResponseVal)

    fig, ax = plt.subplots()
    y = np.array(csv_array).astype(np.float)
    ax.plot(abszissa,y)
    ax.set_title (title)
    ax.set_xlabel("Frequency (Hz(")
    ax.set_ylabel("Magnitude (dB)")
    
    plt.show()
        
        
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
    myprint (myff.read())
    # Define Error Check Function
    
    #myff.write("System:LOCK:REQ?;*OPC?")#not implemented on fieldfox
    #myff.read()
    
    # Call and myprint error check results
    myprint (Errcheck())


    if setup:
        # Preset the FieldFox  
        myff.write("SYST:PRES;*OPC?")
        myprint("Preset complete, *OPC? returned : " + myff.read())
        # Set mode to VNA   
        myff.write("INST:SEL 'NA';*OPC?")
        myff.read()
        
        ## msr setup ##
        myff.write("SENS:SWE:POIN " + str(numPoints))
        myff.write("SENS:FREQ:START " + str(startFreq))
        myff.write("SENS:FREQ:STOP " + str(stopFreq))
        myff.write("BWID " + str(ifbw))
        myff.write("source:power " + str(sourcepower))
        myff.write("AVER:COUNt " + str(avgs))
        
        
        # $$ this doesn't neatly display all traces - probably need to make 'em 1 by one
        #http://na.support.keysight.com/fieldfox/help/Programming/webhelp/CALCulate_PARameter_DEFine.htm
        #myff.write("CALCulate:PARameter1:DEFine S11")
        #myff.write("CALCulate:PARameter2:DEFine S22")
        #myff.write("CALCulate:PARameter3:DEFine S21")
        #myff.write("CALCulate:PARameter4:DEFine S12")
        myff.write("CALCulate:PARameter1:DEFine S21")
    else:
        myff.write("average:clear") # reset avg

    
    ## read msr setup ##
    # Determine, i.e. query, number of points in trace for ASCII transfer - query
    myff.write("SENS:SWE:POIN?")
    numPoints = myff.read()
    myprint("Number of trace points " + numPoints)
    # Determine, i.e. query, start and stop frequencies, i.e. stimulus begin and end points
    myff.write("SENS:FREQ:START?")
    startFreq = myff.read()
    myff.write("SENS:FREQ:STOP?")
    stopFreq = myff.read()
    myprint("FieldFox start frequency = " + startFreq + " stop frequency = " + stopFreq)
    
    ## check if user cal'd properly DOES NOT WORK THAT WAY ##
    myff.write("STATUS:QUESTIONABLE?") # more about internal issuesscpi 
    ffstatq = myff.read()
    myprint("Questionable: "+str(ffstatq))
    
    if dosweep:
        # Set trigger mode to hold for trigger synchronization
        myff.write("INIT:CONT "+str(continous)+";*OPC?")
        myff.read()
    
    
        
        myprint("aquiring data "+str(avgs)+" times, acc. to avg")
        for i in range(avgs): # have to manually trigger each run for the averaging..
            myff.write("INIT:IMM;*OPC?")
            myprint("Single Trigger complete, *OPC? returned : " + myff.read())
        
        
    
    
    
    # Query the FieldFox response data
    '''
    a comma separates response data items when a single query command returns multiple values
    FORM:DATA? 'Query
    ASC, +0 'Analyzer Response
    
    a semicolon separates response data when multiple queries are sent within the same messages
    
    SENS:FREQ:STAR?;STOP? --Example Query
    
    +1.23000000000E+008; +7.89000000000E+008<NL><^END> 'Analyzer Response
    '''
    #myff.write("FORM:DATA?") # works - ASC, 0 - slow but prototype
    #print(myff.read())

    
    #myff.write("TRAC1:DATA?")#For CAT mode and NA mode, use CALCulate:DATA:<type> commands.
    #myff.write("CALCulate:RDATA?") # no worky either
    #myff.write("CALC:MEAS:DATA:FDAT") #NOO - Relevant Modes SA
    #myff.write("CALC:PAR2:SEL 4") # select active vna traces (http://na.support.keysight.com/fieldfox/help/Programming/webhelp/CALCulate_PARameter_SELect.htm)
    #myff.write("CALC:DATA:FDAT 1,1,1") # send 3
    #TRACe:WAVeform<n>:DATA?    #(Read Only) Returns the RF envelope trace data (magnitude vs. power).     #Relevant Modes IQA
    #myff.write("CALC:DATA:SNP:PORTs? \"1,2\";*OPC?") # with opc undefined header
    #myff.write("CALCulate:RDATA?;*OPC?")
    #myff.write("calculate:measure:DATA:FDAT?;*OPC?") #NOO - Relevant Modes SA     
    #myff.write("trace:waveform1:data?;*OPC?") #NOO - Relevant Modes SA     
    #myff.write("CALC:MEAS:DATA?;*OPC?")
    myff.write("CALC:DATA:FDATa?") # correct form was in programming examples not manual.. grumble grumble
              
    ff_csv = myff.read()
    #myprint(ff_csv)# This is one long comma separated string list of values.
    
    csv_array = ff_csv.split(",")
    
    
    
    
    abszissa = np.linspace(float(startFreq),float(stopFreq),int(numPoints)) #SCPI "SENSe:X?" probably unsupported
    # however Read X-axis values possible via-     [:SENSe]:FREQuency:DATA?
    # Assert a single trigger and wait for trigger complete via *OPC? output of a 1
    
    plot_ff(abszissa,csv_array)
    
    if save_trace:
        a=pd.DataFrame(data={"f":abszissa, "Mag":csv_array})
        a.to_csv("trace.csv", index=False)
        
    
    
    
    
    
    ## cleanup ##
    
    if release:
        # Return the FieldFox back to free run trigger mode
        myff.write("INIT:CONT ON")
    
    ##Clear averaging
    # AVER:CLEar

    
    
    # Send a corrupt SCPI command end of application as a debug test
    if do_fail:
        myff.write("INIT:CONT OOOOOOOOOO")#corrupt on purpose (pg. 79)
    # Call the ErrCheck function and ensure no errors occurred between start of program
    # (first Errcheck() call and end of program (last Errcheck() call.
    myprint (Errcheck())
    
    
    # byby handle
    myff.clear()
    myff.close()