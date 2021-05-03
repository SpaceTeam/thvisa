#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 23:13:06 2021

@author: thomas
"""

stuff = "A1,B1,A2,B2,A3,B3"

import numpy as np
import pandas as pd

t = [stuff,stuff,stuff]
abszissa=["x1","x2","x3"]



df=pd.DataFrame(abszissa)
i=0
for trace in t:
    i+=1
    stuff=trace.split(",") #now list
    arr = np.array(stuff)
    b=np.reshape(arr,(-1,2)) # now Ai Bi sit in same row (therefore all As & Bs in respective columns)
    #txt=str(t.index(trace))
    txt=str(i)
    df2=pd.DataFrame(b, columns=[txt,txt+"j"]) # make sheet
    #df=df.append(b) # non-named stuff should be added as columns.. $test
    df=pd.concat([df, df2], axis=1) # concatenate sheets


#df=pd.merge(df,b) # non-named stuff should be added as columns.. $$ONLY if one column overlaps!!


# do i need column names? 
df3=pd.DataFrame(abszissa)
for trace in t:
    stuff=trace.split(",") #now list
    arr = np.array(stuff)
    b=np.reshape(arr,(-1,2)) # now Ai Bi sit in same row (therefore all As & Bs in respective columns)
    df2=pd.DataFrame(b) # make sheet
    df3=pd.concat([df3, df2], axis=1) # concatenate sheets

#seems no