#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  08 11:48:02 2020

@author: thirschbuechler

This is a really minimal pdf creator, if you want to temporarily avoid
https://github.com/mpastell/Pweave
which is superior in any way, and the way forward

"""
import matplotlib.pyplot as plt
import pdf_helper as pdf
import numpy as np
import os

figs = []
mytext = []


def myprint(*args):
	global mytext # this is bad practice and should be a property of a class object
	
	print(*args)
	s="".join(args)
	mytext.append(s+"\n")
	


# prep x-axis
x = np.arange(0,2*np.pi,np.pi/16)


# first plot
myprint("First figure shows a sine")
figure = plt.figure()
figs.append(figure)
plt.plot(x,np.sin(x)) # can happen after figure ref is added to list figs
# plt.show() # interrupts program flow and waits for user to close figure


# second plot
myprint("Second figure shows a cosine")
figure = plt.figure()
figs.append(figure)
plt.plot(x,np.cos(x))


# some text
t1 = "test xy yielded: "
t1res = "success"
myprint(t1, t1res)


# create the pdf #
logo = "white-quer2.png" # only pngs supported
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"pdfhelper-demo.pdf") # always chooses right slash depending on OS	
pdf.create(logo, mytext, figs, filename)