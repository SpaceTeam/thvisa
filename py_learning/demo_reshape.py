#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 23:13:06 2021

@author: thomas
"""

stuff = "A1,B1,A2,B2,A3,B3"

import numpy as np

stuff=stuff.split(",") #now slist
arr = np.array(stuff)


b=np.reshape(arr,(-1,2)) # now Ai Bi sit in same row (therefore all As & Bs in respective columns)