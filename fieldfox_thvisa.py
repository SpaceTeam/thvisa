#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
## general class for common mode independent fieldfox commands ##

Created on Sun May 02 2021

@author: thirschbuechler
"""

import thvisa as thv
import time


class fieldfox(thv.thInstr):

    # overwrite class inherited defaults
    myprintdef = print
    instrnamedef = "TCPIP::K-N9914A-71670.local::inst0::INSTR" # full name since no autodetection 
    qdelaydef = 0.5
        
    def __init__(self, instrname = instrnamedef, qdelay = qdelaydef, myprint = myprintdef):
        ## set defaults or overrides as given to init() ##
        self.timeout = 10000 # "https://pyvisa.readthedocs.io/en/1.8/resources.html#timeout"
        self.instrname=instrname 
        self.myprint=myprint
        self.qdelay=qdelay
        
        ## call parent init ##
        # .. righthand stuff has to be "self." properties and unusually, has no ".self" prefix
        super(fieldfox, self).__init__(myprint=myprint,instrname=instrname, qdelay=qdelay, timeout=10000) 
        
        
        self.do_command("*CLS")#clear any old errors
        #self.reset() dependent on application - do in subclass or actual script
    
    
    def __exit__(self, exc_type, exc_value, tb):# "with" context exit: call del
        self.unlock()
        self.instr.clear()
        super(fieldfox, self).__exit__( exc_type, exc_value, tb) # self.instr.close() and so on


    # frontpanel input access control
    def lock(self,state=1):
        if state:
            self.do_command("INSTR:GTR")
        else:
            self.do_command("INSTR:GTL")
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

    def do_command(self, cmd, qdelay=None):
        if qdelay==None:
            qdelay=self.qdelay # self undefined above
            
        #super(fieldfox, self).do_command(cmd)
        #return self.instr.write("*OPC?")
        
        self.instr.write(cmd+";*OPC?")
        #self.instr.write(cmd)
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

    

    # enable trigger and get data #
    #def capture(self): # mode depentent unfortunately, see ff_vna (exists) and ff_speccy (todo)
        #pass
        

    def ff_title(self, title):
        cmd=str("DISPlay:TITLe:DATA \'"+title+"\'")
        print(cmd)
        self.do_command(cmd)
        self.do_command("disp:TITL 1")



#### test this library using semi Unit Testing ####
if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    
    myff = fieldfox() # read IDN
    myff.errcheck() # because why not

    myff.ff_title("..testing general fieldfox class..")
    
 