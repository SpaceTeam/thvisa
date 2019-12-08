#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:35:30 2019

@author: thomas
"""
import struct
import numpy as np
import thvisa as thv


class InfiniiVision(thv.thInstr):
# code guidelines: default setup has to measure testsignal with default probe

    def initialize(self):
        # Get and display the device's *IDN? string.
        instr.timeout = 15000 # https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout
        idn_string = self.do_query_string("*IDN?")
        self.myprint("Identification string: '%s'" % idn_string)
        # Clear status and load the default setup.
        self.do_command("*CLS")
        self.do_command("*RST")


    def wgen_setup(self, fct, freq, VL, VH):
        self.do_command(":WGEN:MODulation:FUNCtion {}".format(fct))
        self.do_command(":WGEN:FREQuency {}".format(freq))
        self.do_command(":WGEN:VOLTage:HIGH {}".format(VH))
        self.do_command(":WGEN:VOLTage:LOW {}".format(VL))


    def wgen_output(self,out_enable):
        if out_enable:
            self.do_command(":WGEN:OUTPut ON")
        else:
            self.do_command(":WGEN:OUTPut OFF")


    def setup_trigger_edge(ch=1,level=1.5,slope="positive"):
        self.do_command(":TRIGger:MODE EDGE")
        self.do_command(":TRIGger:EDGE:SOURce CHANnel{}".format(ch))
        self.do_command(":TRIGger:EDGE:LEVel {}".format(level)) # note: trigger doesn't work if vscale out of range obviously.. catch somehow or just leave note
        self.do_command(":TRIGger:EDGE:SLOPe {}".format(slope))


    def setup_timebase(self,scale=0.0002, pos=0.0):
        self.do_command(":TIMebase:SCALe 0.0002")
        self.do_command(":TIMebase:POSition 0.0") # leave the offset close to the trigger!


    def setup_channel(ch=1,scale=0.5,offset=1.5,probe=10.0):
        osc.do_command(":CHANnel{}:PROBe {}".format(ch,probe))
        osc.do_command(":CHANnel{}:SCALe {}".format(ch,scale))
        osc.do_command(":CHANnel{}:OFFSet {}".format(ch,offset))


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


    def store_setup(self):
        sSetup =self.do_query_ieee_block(":SYSTem:SETup?")
        f = open("setup.stp", "wb")
        f.write(sSetup)
        f.close()
       self.myprint("Setup bytes saved: %d" % len(sSetup))


    def load_setup(self):
        sSetup = ""
        f = open("setup.stp", "rb")
        sSetup = f.read()
        f.close()
        instr.do_command_ieee_block(":SYSTem:SETup", sSetup)
       self.myprint("Setup bytes restored: %d" % len(sSetup))


    def capture(self,type="normal"): #normal,highres, ..
        osc.do_command(":ACQuire:TYPE {}".format(type))
        osc.do_command(":digitize") # digitize all channels: now it's stored in the oszi


    def autoscale(self):
        myprint("Autoscale. this usually is bad practice, but you asked for it..")
        osc.do_command(":AUToscale")


    def analyzetest(self): # todo: mooooaaar measurements!!!
        qresult = self.do_query_string(":MEASure:VAMPlitude?")
        return qresult

    def data_dl(self, channel=1):
       self.myprint("### getting channel "+str(channel)+" ###")

        self.do_command(":WAVeform:POINts:MODE RAW")
        # Get the number of waveform points available.
        self.do_command(":WAVeform:POINts 10240")
        # Set the waveform source before getting data, it is already saved in instrument, but specify what to get
        self.do_command(":WAVeform:SOURce CHANnel"+str(channel))
        self.do_command(":WAVeform:FORMat BYTE")


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

        preamble_string = self.do_query_string(":WAVeform:PREamble?")
        (
            wav_form, acq_type, wfmpts, avgcnt, x_increment, x_origin,
            x_reference, y_increment, y_origin, y_reference
    #    ) = string.split(preamble_string, ",")
        ) = preamble_string.split(",")

       self.myprint("Waveform format: %s" % wav_form_dict[int(wav_form)])
       self.myprint("Acquire type: %s" % acq_type_dict[int(acq_type)])
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



### module test ###
if __name__ == '__main__': # test if called as executable, not as library
    oszi = InfiniiVision()
    oszi.initialize()

    #todo: insert code to measure test signal
    #todo: test all functions
