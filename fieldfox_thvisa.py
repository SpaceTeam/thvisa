#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## general class for common mode independent fieldfox commands ##

Created on Sun May 02 2021

@author: thirschbuechler
"""

import time
import numpy as np # abscissa

# import class not whole module
# - works both internally (called as __main__ f. testing)
# - and externally (called as submodule)
#from thvisa import thInstr as thi 

try:
    import thvisa as thv # import common functions
    from thvisa import thInstr # this should not do anything but otherwise calling subm fails as "name fieldfox not defined"
except:
    try:
        from thvisa import thvisa as thv # if called as module
    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")

if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    testing = True
else:
    testing = False



class fieldfox(thv.thInstr):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "TCPIP::K-N9914A-71670.local::inst0::INSTR" # TCPIP: full name since no autodetection 
    instrnamedef = "USB0::10893::23576::MY57271670::0::INSTR" # USB: not fullname required but whatever
    qdelaydef = 0.5
        
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef):
        
        ## set defaults or overrides as given to init() ##
        self.timeout = 10000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout"
        self.instrname=instrname 
        self.myprint=myprint
        self.qdelay=qdelay
        #self.role="bla" # NA=VNA, SA=speccy - both need be set by ff_VNA_thvisa or ff_speccy_thvisa children

        self.abscissa = []
        self.avgs=1 # default since always sent
        
        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(fieldfox, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay, timeout=10000) 
        
        self.do_command("*CLS")#clear any old errors
        #self.reset() dependent on application - do in subclass or actual script
    
    
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        self.unlock()
        if "TCPIP" in self.instrname:
            self.instr.clear()#clear seems unsupported by USBtmc, wtf
        super(fieldfox, self).__exit__( exc_type, exc_value, tb) # self.instr.close() and so on


    ## main shared functions ##
    def setup(self, hard=True, numPoints = 1001, startFreq = 2.4E9, stopFreq = 2.5E9, ifbw=1E3, avgs=1):
        """ parent setup class
            to be called and appended by ff_VNA or ff_speccy children"""
        if hard:
            # Preset the FieldFox  
            self.do_command("SYST:PRES")#"SYST:PRES;*OPC?" # docommand does opc inherited by fieldfox mainclass
            # Set mode to VNA   
            self.do_command("INST:SEL '{}'".format(self.role))
            
                
        # abscissa
        self.numPoints = numPoints
        self.startFreq = startFreq
        self.stopFreq = stopFreq
        
        ## msr setup ##
        self.do_command("SENS:SWE:POIN " + str(self.numPoints))
        self.do_command("SENS:FREQ:START " + str(self.startFreq))
        self.do_command("SENS:FREQ:STOP " + str(self.stopFreq))
        self.set_avgs(avgs)

        #self.setup_done = True # in childclasses


    def set_avgs(self,avgs):
        self.avgs = avgs
        self.do_command("AVER:COUNt 1")#reset to invalidate old avgs
        self.do_command("AVER:COUNt " + str(self.avgs))        
        

    def sweep_reset(self):
        """  manually reset avg!
        otherwise more than avg count required to get rid of old stuff"""
        # self.do_command("INIT:REST")# does not work
        
        # circumvent 
        #self.do_command("AVER:COUNt 1")# initate restart via reset to 0
        #self.do_command("AVER:COUNt 5")
        #self.do_command("INIT:IMM")#now dueto 

        self.set_avgs(self.avgs)#use the setter as it clears as well


    def do_sweeps(self, continous="off"):
        """ enable trigger and get data into instr memory """
        # Set trigger mode to hold for trigger synchronization
        #continous="off" # during measurement.. anyway
        self.do_command("INIT:CONT "+str(continous)+"")
        
        self.myprint("aquiring data "+str(self.avgs)+" times, acc. to avg")
        if self.avgs > 1:
            self.sweep_reset()
        for i in range(self.avgs): # manually trigger each run for the averaging..
            ret = self.do_command("INIT:IMM")  # opc baked into do_command
            #self.myprint("Single Trigger complete, *OPC? returned : " + ret)
            self.myprint("Trig'd({}/{})".format(i+1,self.avgs)) #, *OPC? returned : " + ret)


    def make_abscissa(self):
        """ fetch f-axis stuff from VNA """
        if not self.setup_done:
            self.numPoints=self.do_query_string("SENS:SWE:POIN?")
            self.startFreq=self.do_query_string("SENS:FREQ:START?")
            self.stopFreq=self.do_query_string("SENS:FREQ:STOP?")
            
        # build
        self.abscissa = np.linspace(float(self.startFreq),float(self.stopFreq),int(self.numPoints)) 
        # notes
            #SCPI "SENSe:X?" probably unsupported
            # however Read X-axis values possible via-     [:SENSe]:FREQuency:DATA?


    ## other helpers ##

    # frontpanel input access control
    def lock(self,state=1):
        if state:
            self.do_command("INST:GTR")
        else:
            self.do_command("INST:GTL")
    def unlock(self, state=1):
        self.lock(not state)


    # reset the instrument to the known default setup #
    # same as check_instrument_errors()?
    def errcheck(self):
        myError = []
        ErrorList = self.instr.query("SYST:ERR?").split(',')
        Error = ErrorList[0]
        if int(Error) == 0:
            self.myprint ("+0, No Error!")
        else:
            while int(Error)!=0:
                self.myprint ("Error #: " + ErrorList[0])
                self.myprint ("Error Description: " + ErrorList[1])
                myError.append(ErrorList[0])
                myError.append(ErrorList[1])
                ErrorList = self.instr.query("SYST:ERR?").split(',')
                Error = ErrorList[0]
                myError = list(myError)
        return myError


    def do_command(self, cmd, qdelay=None, OPC=1):
        if qdelay==None:
            qdelay=self.qdelay
            
        #super(fieldfox, self).do_command(cmd)
        
        if OPC: # 99% of all commands will cause "Query unterminated" without this
            cmd+=";*OPC?"

        self.instr.write(cmd)

        time.sleep(qdelay)
        return self.instr.read()

    
    # $ test invinivision stuff
    # $$ what happens to cal?
    # alternatively, MMEMory:LOAD:STATe "autosave1.sta"
    # or something like that
    # store instrument setup state in script dir #
    def store_setup(self, filename="setup.sta"):
        #sSetup =self.do_query_ieee_block(":SYSTem:SETup?")
        #f = open(filename, "wb")
        #f.write(sSetup)
        #f.close()
        #self.myprint("Setup bytes saved: %d" % len(sSetup))
        pass


    # load instrument setup state from script dir #
    def load_setup(self, filename="setup.sta"):
        #f = open(filename, "rb")
        #sSetup = f.read()
        #f.close()
        #self.do_command_ieee_block(":SYSTem:SETup", sSetup)
        #self.myprint("Setup bytes restored: %d" % len(sSetup))
        pass


    def center_on_peak_marker(self, nr=1, trace=1, center=True):
        """ make marker, goto peak, save values, center , ret values
        options
            - nr: marker nr
            - trace (NA): which trace to perform on?
        """
        #make marker
        self.do_command("CALC:MARK{}:ACTivate".format(nr)) # enough to create & activate
        #self.do_command("CALC:MARK{}:Norm".format(nr)) # fails
            #set type
            #self.do_command("CALCulate[:SELected]:MARKer:FORMat <char>")
        if self.role=="NA":# untested
            self.do_command("CALC:MARK{}:TRAC {}".format(nr,trace))
        #lock to maximum
        self.do_command("CALC:MARK{}:FUNC:MAX".format(nr))#(SA/NA no query)
        #query peek excursion (is it actually significant)
        q = self.do_query_string("CALC:MARK:FUNC:PEXC?")
        print(q)
        #read marker values x/y (pg 226)
        X = self.do_query_string("CALC:MARK{}:X?".format(nr))
        print(X)
        Y = self.do_query_string("CALC:MARK{}:Y?".format(nr))
        print(Y)
        if center:
            #read new center freq from marker
            self.do_command("CALC:MARK{}:SET:CENT".format(nr))

        #return X,Y



    def ff_title(self, title=None):
        if title!=None:
            self.do_command(str("DISPlay:TITLe:DATA \'"+title+"\'"))
            self.do_command("disp:TITL 1")
        else:
            self.do_command("disp:TITL 0")


    def askandlog(self, thing):
        return(thing+" "+self.do_query_string(thing))


    def query_setup(self):
        
        log=[]
        log.append(self.askandlog("SENS:SWE:POIN?"))
        log.append(self.askandlog("SENS:FREQ:START?"))
        log.append(self.askandlog("SENS:FREQ:STOP?"))
        
        log.append(self.askandlog("AVER:COUNt?"))
        
        if self.role=="NA":
            log.append(self.askandlog("BWID?"))
            log.append(self.askandlog("SOUR:POW:ALC?"))
            log.append(self.cal_str()) # ask usercal and report # HACK - calls fct defined in NA class variant (child)
        else: # SA speccy
            log.append(self.askandlog("SENS:FREQ:SPAN?"))


        log.append("all properties of class:")
        log.append(str(vars(self)))
                            
        return log



#### test this library using semi Unit Testing ####
if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    
    with fieldfox() as myff: # make object, autodispose afterward with-end, read IDN
        myff.errcheck() # because why not

        myff.ff_title("..testing general fieldfox class..")