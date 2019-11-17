#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2017/2018

@author: thirschbuechler
"""

import usbtmc
import visa

import matplotlib.pyplot as plt
import time
from enum import Enum

import eggclock_helper as egg
#import cmd_helper as mc
egg.timedout="Outta Time"

# ToDo: if not trig'd, autotrigger: timeout ok, script continues but usb-timeout prevents any further instructions!?
	# user reset required?

''' --- low priority --'''

# todo: use ":aquire" and/or ":digitize" to get all channels at same time

# ToDo: pyvisa raw read (usbtmc alternative w. LAN support (device option) but serialNr needed for handshake
# ToDo: query which driver is installed
	# import sys
	# ('usbtmc' in sys.modules)==1
# ToDo: outsource usbtmc/pyvisa


### global variable defaults ###

clearmsg = 1 # wait for "reset" msg to vanish?
myprint=print
mysleep=time.sleep
lastcmd=""
showfigure=0

### internal datatypes and functions ###

def setprint(function): # to redirect print to pdf, etc.
	global myprint
	myprint=function


class drv(Enum):
	tmc = 'usbtmc'
	pyv = 'py-visa' # data read raw (graphs) does not work at the moment


def writer(st):
	global instr, driver
	# same, regardless of pyvisa/tmc, for now
	
	try:
		lastcmd="write "+st
		#st+="\n" # not needed
		instr.write(st)

	except IOError as exc:
		myprint("write "+st+" rased an IO Error"+str(exc))
		#writer("*CLS")#clear error #doesn't work for non-triggered
		#myprint(askready())
		pass
		#return()
	
	mysleep(0)
	#if not st=="waveform:data?":
		#printerror()#this kills dataaquisition otherwise
	#print("writing: "+st) # catch where error is
	
#end fct writer	
	

def askready(): # should contain whether all operations have been finished
	# todo check whether trigger worked within exp. time
	return(ask("*OPC?"))


def ask(st):
	global instr, driver
	
	try:
		lastcmd="ask "+st
		#st+="\n" # not needed
		if driver == drv.tmc:
			return(instr.ask(st))
		elif driver == drv.pyv:
			return(instr.query(st))
	except IOError as exc:
		myprint("write "+st+" rased an IO Error"+str(exc))
		#myprint(askready()) # this calls itself, duh
		pass
	
#end fct ask


def raw(st):
	global instr, driver
	
	if (driver == drv.tmc):
		return(instr.read_raw(st))
	elif (driver == drv.pyv):
		return(instr.query(st))#is this really how the visa driver handles raw data # no it throws some error


def init(driv = drv.tmc):
	global instr, driver
	driver=driv
	
	myprint("driver: "+str(driver))
		
	if (driver == drv.tmc): # default
		try:
			instr = usbtmc.Instrument(10893,6039) # connect to first keysight found, serial-independent
			return(1)
		except Exception as exp:
			# UsbtmcException("Device not found", 'init')
			print("error when loading instrument") ##todo: test
			return(0)
	elif (driver == drv.pyv):
		try:
			rm = visa.ResourceManager('@py')
			#myprint(rm.list_resources())#only supports serial and usb
			#the usb has a langid-issue on rigol
			#myprint("sudo is required, not admin on win though")
			serial = 'CN57276214'# todo: open textbox
			instr = rm.open_resource('USB0::10893::6039::'+serial+'::INSTR')
			# can be looked up under utils - io
			# reference: http://zone.ni.com/reference/en-XX/help/370131S-01/ni-visa/visaresourcesyntaxandexamples/
			return(1)
		
		except visa.VisaIOError as e:
			myprint('visa i/o error')
			myprint(e.args)
			myprint(_rm.last_status)
			myprint(_rm.visalib.last_status)
			return(0)
	
	# instr is initialized
	try:
		myprint(ask('*IDN?'))
	except NameError:
		myprint("no DSOX1102G oscilloscope connected")
		return(0)
		#exception will trickle down to testrig-mainscript, as well
		
		
def getdatafrom(channel): # todo: use ":aquire" and/or ":digitize" to get all channels at same time
	global i, volt_range, points, ch1_ofs, timerange
	
	mytrigger()
	mysleep(1)
	
	#maybe if a usb-timeout occours, reset manually and autottigger
	#autotrigger()
	writer(":Single")
	#autotrigger()
		
	sleeper=timerange*1.1 # sleep bit longer than expected aquisition
		
	myprint("sleeping %.3g s for data aquisition into the Oszi... " %(sleeper))
	mysleep(sleeper)
	
	myprint("done waiting, get data from Oszi..")
	#printstatus()
	#printerror()
	if not askready(): 
		myprint("failed to finish, critical error!")
		writer(":STOP") # in case it didn't trigger
	# or ask(":AER?"):# "query unterminated" error appears
	#TER: trigger register?
	# or OPeration status register
		
	writer(":waveform:source channel"+str(channel))		
	success=0
	
	try:
		egg.settimer(3) # wait x sec before data collection timeouts
		writer("waveform:data?")
		puke = raw(points) 
		success=1
	except Exception as ex:
		myprint(ex) # print exception but soldier on
		
		if (ex==egg.timedout):
			myprint("trying to autotrigger..")
			autotrigger()
			writer("waveform:data?")
			puke = raw(points) 
			if len(puke)>0:
				success=1
			#myprint("resetting trigger to preconfigured state")
			#mytrigger()
			
	pass # don't crash python
				
	egg.cleartimer()
	
	if success: # process data
		
		data_bytes = [puke[i:i+2] for i in range(0, len(puke), 2)]
		nLength = len(data_bytes)
		#myprint("Number of data values: %d" % nLength)
		
		volt_range=float(ask(":channel"+str(channel)+":range?"))
		
		data=[int.from_bytes(data_bytes[i],byteorder='big',signed=0) for i in range (0,len(data_bytes))] #65535 is max y
		#myprint("data items: "+str(len(data)))
		xx=timerange/len(data)
		#myprint(xx)
		x=range(0,len(data),1)
		x=[float(x[i]*xx) for i in range(0,len(data))]
		
		#trim
		data = data[5:-5] #keep after index x till max_index-x
		x = x[5:-5]

		data=[(float(data[i]/65535*volt_range))-ch1_ofs for i in range(0,len(data))]
		
	else:
		[x,data]=[0,0]
	
	return(x,data)
#end getdatafrom(channel)


def mytrigger():
	writer(":trigger:mode edge")
	writer(":trigger:edge:source channel1")
	writer(":trigger:edge:level 1")
	writer(":trigger:edge:slope positive")
	writer(":trigger:sweep normal")


def autotrigger():
	writer("*CLS")#clear error if not triggered before
	writer(":trigger:force")
	
	
def myreset():
	mysleep(1)
	writer("*RST")#reset to factory settings
	#writer("*CLS")#clear screen, not msg unfortunately
	writer(":STOP")
	#writer(":system:lock") # lock device for user
	if clearmsg: # wait for "reset" msg to vanish?
		mysleep(5)	
	
def setup():
	global i, volt_range, points, ch1_ofs
	#printstatus()
	myreset()
	
	mytrigger()
	
	# measure
	#writer(":wav:points:mode raw")
	points=10240
	writer(":wav:points "+str(points))
	#writer(":waveform:source channel1")
	writer(":waveform:format byte")
	
		
	# setup channel1 for wavegen tracking
	writer(":channel1:coupling dc")
	writer(":channel1:scale 0.5V")#HAS TO COME BEFORE OFFSET OTHERWISE IT MAY LAG
	#THIS WAS THE RROR; HAVING IT IN ORDER LIKE THE PROG MANUAL SAID
	#BUT SCALE HAS TO BE DEFINED FIRST
	#ALSO; SOMEHWERE IT WAS LIKE ":wgen freq 1" which produced an identical error, sometimes
	ch1_ofs=1# 1v
	writer(":channel1:offset "+str(ch1_ofs)+"V")#offset -1 as maximum-test and findout why first
	writer(":channel1:display 1")#default but whatever
	
	# setup channel2 for client DAC tracking

	writer(":channel2:coupling dc")
	writer(":channel2:scale 0.5V")#HAS TO COME BEFORE OFFSET OTHERWISE IT MAY LAG
	#THIS WAS THE RROR; HAVING IT IN ORDER LIKE THE PROG MANUAL SAID
	#BUT SCALE HAS TO BE DEFINED FIRST
	#ALSO; SOMEHWERE IT WAS LIKE ":wgen freq 1" which produced an identical error, sometimes
	ch1_ofs=1# 1v
	writer(":channel2:offset "+str(ch1_ofs)+"V")#offset -1 as maximum-test and findout why first
	writer(":channel2:display 1")
	
	#end setup
def wavegen(f,fct,Vp, DC): # wavegen setup
	writer(":wgen:freq "+str(f))
	writer(":wgen:function "+fct)
	
	# WHY DOES THE ARGUMENT VP AND DC CAUSE IT TO NOT WORK
	#print(":wgen:voltage "+str(Vp))
	writer(":wgen:voltage "+str(Vp))#V
	writer(":wgen:voltage:offset "+str(DC))#V
	#print(":wgen:voltage:offset "+str(DC))
	
	#writer(":wgen:voltage:offset "+str(DC))#V
	#print(":wgen:voltage:offset "+str(DC))
	mysleep(1)
	myprint("outputting "+fct+" Vpp"+str(Vp)+", VDC"+str(DC)+" with freq "+str(f))
	writer(":wgen:output 1")
	mysleep(0) # no relais delay needed apparently
	

### a few one-liners ###	
def set_tb(tb):
	writer(":timebase:range "+str(tb))

def stop_wavegen():
	writer(":wgen:output 0")
	
def stop_btn():
	writer(":STOP")
			
#todo: test Event STatus Register (p.114) for command/execution/device/query errors		
'''
def printstatus():
	#res=ask(":OPEE?")
	#res=ask(":OPER:EVEN?") #neither changes whether oszi is in run-mode or stop-mode, or trig'd
	print(res)
	b=int(res)
	run_bit=mybit.isbitset(b,3)
	wait_trig=mybit.isbitset(b,5)
	mask_test=mybit.isbitset(b,9) # mask test: pass fail option, :MTESt commands
	overload_50ohm=mybit.isbitset(b,11)
	
	print("Trig armed?': "+str(wait_trig)+", Run?: "+str(run_bit)+", mask test: "+str(mask_test))

def printerror(): # this adds oter errors if errorcode fucked up so never mind
	res=ask(":system:error?")
	#myprint(res)
	errorcode=int(ff.findallfloats(res)[0]) # assume 1st float
	
	if errorcode == 0: # 0 float = 0 int
		#myprint("No error")
		mysleep(0)
	else:
		print("lastcmd: "+lastcmd)
		if errorcode == +109:
			myprint("no data for operation, e.g. not Trig'd")
		elif errorcode == -420:
			myprint("Query unterminated")
		else:
			myprint("unknown error: "+res)
		
#end printerror
'''	
		
def fetch(fig): # only the plotfigure is needed
	global timerange
	plotbase = 320 # 3x2 = 6 subplots
	plots = 6
	plt.subplots_adjust(wspace = 0.5, hspace = 1)

#do somewhere else			
#	init(drv.tmc)
	
	setup()
	
	
	freqs=[100,10,1]
	fcts=["sin","ramp","sin"] # sin and ramp work without redefining the trigger, square does not
	
	plotindex=1
	for freq in freqs:
		i=freqs.index(freq) # starts at 0
		timerange=2/freq

		amp=1.5
		off=1 
		wavegen(freq,fcts[i],amp,off)

		set_tb(timerange)
		
		# measure channels sequentially: limitation of "waveform:data?"
		CHs = [1,2]
		for CH in CHs:
			
			[x,data] = getdatafrom(CH)
			#datasets.append(getdatafrom(CH))
		
			myprint("data aquired, plotting to hidden figures..")
			
			plt.subplot(plotbase+plotindex)# e.g. subplot 221, 222,..
			
			plt.plot(x,data)
			plt.title(fcts[i]+" CH %i run %i" %(CH,plotindex))
			plt.xlabel('time [s]')
			plt.ylabel('mag [V]')
		
			#matlab/matplotlib stone of rosetta:
			#http://reactorlab.net/resources-folder/matlab/P_to_M.html
			#plt.ylim((0,65535))
			# ticks and so on
			# https://stackoverflow.com/questions/30482727/pyplot-setting-grid-line-spacing-for-plot
			#plt.grid(color='k',linestyle='-', linewidth=0.5, which='minor')
			#plt.minorticks_on()		
			plotindex+=1	

		stop_wavegen();
		stop_btn() # in case it didn't trigger and magically didn't raise an error or timeout
		
	#end for
	if showfigure:
		plt.show()
		myprint("done, show plot")
		
	return(fig)

def fetch2(fig): # only the plotfigure is needed
	global timerange
	plotbase = 320 # 3x2 = 6 subplots
	plots = 6
	plt.subplots_adjust(wspace = 0.5, hspace = 1)
			
	init(drv.tmc)
	
	setup()
	
	
	freqs=[100,10,1]
	fcts=["sin","ramp","sin"] # sin and ramp work without redefining the trigger, square does not
	
	plotindex=1
	for freq in freqs:
		i=freqs.index(freq) # starts at 0
		timerange=2/freq

		amp=1.5
		off=1 
		wavegen(freq,fcts[i],amp,off)

		set_tb(timerange)
		
		# measure channels sequentially: limitation of "waveform:data?"
		CHs = [1,2]
		for CH in CHs:
			if CH==2:
				print("ch2 not impolemented")
				[x,data] = getdatafrom(CH)
			else:
				[x,data] = getdatafrom(CH)
			#datasets.append(getdatafrom(CH))
		
			myprint("data aquired, plotting to hidden figures..")
			
			plt.subplot(plotbase+plotindex)# e.g. subplot 221, 222,..
			
			plt.plot(x,data)
			plt.title(fcts[i]+" CH %i run %i" %(CH,plotindex))
			plt.xlabel('time [s]')
			plt.ylabel('mag [V]')
		
			#matlab/matplotlib stone of rosetta:
			#http://reactorlab.net/resources-folder/matlab/P_to_M.html
			#plt.ylim((0,65535))
			# ticks and so on
			# https://stackoverflow.com/questions/30482727/pyplot-setting-grid-line-spacing-for-plot
			#plt.grid(color='k',linestyle='-', linewidth=0.5, which='minor')
			#plt.minorticks_on()		
			plotindex+=1	

		stop_wavegen();
		stop_btn() # in case it didn't trigger and magically didn't raise an error or timeout
		
	#end for
	if showfigure:
		plt.show()
		myprint("done, show plot")
		
	return(fig)
	
	
if __name__ == '__main__': # test if called as executable, not as library
	showfigure = 1
	#not tested here but works in mainscript: starting without oszi connected without dying
	init(drv.tmc)
	fetch(plt.figure())
