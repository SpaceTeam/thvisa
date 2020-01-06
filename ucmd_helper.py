#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 16:55:24 2020

@author: thomas
"""
## Important Note ##
# the "input"-function prevents exception throw
# found out by using the eggclock-helper

def askandreturn(question="Question", validresults=["yes","no"]):
    while 1:
        text = input(question+str(validresults))
        if text in validresults:
            return text # exit
        
        
def askandreturnindex(question="Question", validresults=["yes","no"]):
    return(validresults.index(askandreturn(question,validresults)))
            
        
if __name__ == '__main__': # test if called as executable, not as library
    options = ["yes","no","definitely"]
    options.append("maybe")
    
    print(askandreturn("Continue?",options))
    
    print(askandreturnindex("Continue?",options))