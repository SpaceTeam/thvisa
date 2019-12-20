#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:35:30 2019

@author: thomas
"""
#import time
import struct
import numpy as np
import thvisa as thv
import matplotlib.pyplot as plt

class InfiniiVision(thv.thInstr):
# code guidelines: default setup has to measure testsignal with default probe

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "CN5727"
    qdelaydef = 0.5
        
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef):
        self.timeout = 15000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout"
        self.instrname=instrname # the defaults can't be used other than to become properties
        self.myprint=myprint
        self.qdelay=qdelay
        print(qdelay)
        
        # call parent init #
        # the righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(InfiniiVision, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay) 
        self.reset()
    
    
        # other common properties #
        self.acq_type_dict = {
            0 : "NORMal",
            1 : "PEAK",
            2 : "AVERage",
            3 : "HRESolution",
        }
        
        self.wav_form_dict = {
            0 : "BYTE",
            1 : "WORD",
            4 : "ASCii",
        }
        

    # reset the instrument to the known default setup #
    def reset(self):
        self.do_command("*CLS")
        self.do_command("*RST")
        # $$ are we in stop now?
        # $$ lock oszi as well!?


    # setup the function generator aka wave generator #
    def wgen_setup(self, fct, freq, VL, VH):
        self.do_command(":WGEN:MODulation:FUNCtion {}".format(fct))
        self.do_command(":WGEN:FREQuency {}".format(freq))
        self.do_command(":WGEN:VOLTage:HIGH {}".format(VH))
        self.do_command(":WGEN:VOLTage:LOW {}".format(VL))


    # set the state of the wave gen (default after reset: disable)
    def wgen_output(self,out_enable):
        if out_enable:
            self.do_command(":WGEN:OUTPut ON")
        else:
            self.do_command(":WGEN:OUTPut OFF")


    # setup the trigger without enabling it #
    def setup_trigger_edge(self,ch=1,level=1.5,slope="positive"):
        self.do_command(":TRIGger:MODE EDGE")
        self.do_command(":TRIGger:EDGE:SOURce CHANnel{}".format(ch))
        self.do_command(":TRIGger:EDGE:LEVel {}".format(level)) # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note
        self.do_command(":TRIGger:EDGE:SLOPe {}".format(slope))


    # setup the horizontal axis #
    def setup_timebase(self,scale=0.0002, pos=0.0):
        self.do_command(":TIMebase:SCALe 0.0002")
        self.do_command(":TIMebase:POSition 0.0") # leave the offset close to the trigger!


    # setup the channel #
    def setup_channel(self,ch=1,scale=0.5,offset=1.5,probe=10.0):
        self.do_command(":CHANnel{}:PROBe {}".format(ch,probe))
        self.do_command(":CHANnel{}:SCALe {}".format(ch,scale))
        self.do_command(":CHANnel{}:OFFSet {}".format(ch,offset))


    # take a screenshot image #
    def screenie(self,filename="screen_image.png"):
        # Download the screen image.
        # --------------------------------------------------------
        self.do_command(":HARDcopy:INKSaver OFF")

        sDisplay =self.do_query_ieee_block(":DISPlay:DATA? PNG, COLor")

        # Save display data values to file.
        f = open(filename, "wb")
        f.write(sDisplay)
        f.close()
        self.myprint("Screen image written to {}.".format(filename))


    # store instrument setup state in script dir #
    def store_setup(self, filename="setup.stp"):
        sSetup =self.do_query_ieee_block(":SYSTem:SETup?")
        f = open(filename, "wb")
        f.write(sSetup)
        f.close()
        self.myprint("Setup bytes saved: %d" % len(sSetup))


    # load instrument setup state from script dir #
    def load_setup(self, filename="setup.stp"):
        f = open(filename, "rb")
        sSetup = f.read()
        f.close()
        self.do_command_ieee_block(":SYSTem:SETup", sSetup)
        self.myprint("Setup bytes restored: %d" % len(sSetup))


    # enable trigger and get data #
    #$$assuming osci is in stop mode.. is it after reset and test sequence commands!?
    def capture(self,aqtype="normal", trigtype="single"): 
        
        self.do_command(":ACQuire:TYPE {}".format(aqtype)) 
                
        if trigtype=="normal":
            self.do_command(":Trigger:Sweep Normal") # if regular triggering on an edge is setup and wanted, i.e. a turnon-sequence or periodic signal
            self.do_command(":RUN")
        elif trigtype=="auto":
            self.do_command(":Trigger:Sweep Auto") # use if capture asap needed, no sync to some edge wanted, or when measureing DC only, i.e. using osci as DMM!!
            self.do_command(":RUN")
        else:
            self.do_command(":Single") # runs alone, once!
        
        #$todo: timeout and force via .. if no signal, as default option
        #self.do_command(":Trigger:Force")
                
        self.do_command(":digitize") # digitize all channels: now it's stored in the oszi


    # only use if you got an error and don't know what you are dealing with!! #
    def autoscale(self):
        self.myprint("Autoscale. this usually is bad practice, but you asked for it..")
        self.do_command(":AUToscale")


    # some DMM like single-valued readouts without graphs #
    def DMM_results(self, msr="Vamp"): # $todo: mooooaaar measurements!!!
        #$todo if-else or switch-case
        qresult = self.do_query_string(":MEASure:VAMPlitude?")
        return qresult


    # get the data after aquisition #
    def data_dl(self, channel):
        self.myprint("### getting channel "+str(channel)+" ###")

        self.do_command(":WAVeform:POINts:MODE RAW")
        # Get the number of waveform points available.
        self.do_command(":WAVeform:POINts 10240")
        # Set the waveform source before getting data, it is already saved in instrument, but specify what to get
        self.do_command(":WAVeform:SOURce CHANnel"+str(channel))
        self.do_command(":WAVeform:FORMat BYTE")


        # Display the waveform settings from preamble:
        preamble_string = self.do_query_string(":WAVeform:PREamble?")
        (
            wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
            x_reference, y_increment, y_origin, y_reference
        ) = preamble_string.split(",")

        self.myprint("Waveform format: %s" % self.wav_form_dict[int(wav_form)])
        self.myprint("Acquire type: %s" % self.acq_type_dict[int(acq_type)])
        self.myprint("Waveform points desired: %s" % wfmpts)
        self.myprint("Waveform average count: %s" % avgcnt)
        self.myprint("Waveform X increment: %s" % x_increment)
        self.myprint("Waveform X origin: %s" % x_origin)
        self.myprint("Waveform X reference: %s" % x_reference) # Always 0.
        self.myprint("Waveform Y increment: %s" % y_increment)
        self.myprint("Waveform Y origin: %s" % y_origin)
        self.myprint("Waveform Y reference: %s" % y_reference)

        # Get numeric values for later calculations.
        x_increment = self.do_query_number(":WAVeform:XINCrement?")
        x_origin = self.do_query_number(":WAVeform:XORigin?")
        y_increment = self.do_query_number(":WAVeform:YINCrement?")
        y_origin = self.do_query_number(":WAVeform:YORigin?")
        y_reference = self.do_query_number(":WAVeform:YREFerence?")

        # Get the waveform data.
        sData =self.do_query_ieee_block(":WAVeform:DATA?")

        # Unpack unsigned byte data.
        values = struct.unpack("%dB" % len(sData), sData)
        self.myprint("Number of data values: %d" % len(values))

        # make data vectors
        times=  + np.arange(x_origin,x_origin+len(values)*x_increment,x_increment)
        onevector = np.ones(len(values))
        voltages = ((values - y_reference*onevector) )*y_increment + y_origin*onevector
        return(times,voltages)


#### semi Unit Testing ####
### make sure all functions work ###
### (not class fct) ###
### shall only performed manually by someone who understands oszi inner workings ###

# plot helper #
def myplot_bare(osc, ch):
    [times, voltages] = osc.data_dl(ch)
    plt.figure()
    plt.xticks(rotation=90)
    plt.xlabel("s")
    plt.ylabel("V")
    plt.plot(times,voltages)
    plt.show()


def test_data_wavegen_DMM():
    # setup hardware to measure testsignal and wavegen #
    with InfiniiVision() as osc:        
        osc.setup_trigger_edge(ch=1,level=1.5,slope="positive")
        # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note
        osc.setup_channel(ch=1,scale=0.5,offset=1.5,probe=10.0)
        #osc.setup_channel(ch=2,scale=10,offset=0,probe=1.0) # probe is yellow coax
        osc.setup_channel(ch=2,scale=1,offset=0,probe=10.0) 
    
        # setup wgen
        osc.wgen_setup(fct="sinusoid",freq="2E3",VL=0.0,VH=3.0) # setup test signal
        osc.wgen_output(True)
    
        # set horizontal scale
        osc.setup_timebase(scale=0.0002, pos=0.0)
    
        # aquire data
        osc.capture(aqtype="normal", trigtype="normal")
    
        # also do DMM_results_testing on channel of wavegen
        # Dmm_results()
        
        # get and plot
        myplot_bare(osc,2)
        myplot_bare(osc,1)
        
        
# todo: implement #
def test_saveandload():
    # test both ways
    # also delete old screenie, get new one, test whether valid png
    pass


# todo: implement #
def test_autoscale():
    # implement autoscale as error measure, then config trigger wrong on purpose to "trigger" the try-except into autoscale and get some error and autoscale data
    pass


#### test this library using semu Unit Testing ####
if __name__ == '__main__': # test if called as executable, not as library
    test_data_wavegen_DMM()
    test_saveandload()
    test_autoscale()