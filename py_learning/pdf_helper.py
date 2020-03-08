#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created 2018

@author: thirschbuechler

This is a really minimal pdf creator, if you want to temporarily avoid
https://github.com/mpastell/Pweave
which is superior in any way, and the way forward

"""

import os
import numpy as np

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import gridspec
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# from 015d645

# ToDo: scale image with photo=photo.subsample(3)#size down to 1/3 instead of graph, to be less pixely, or even svg:
#https://stackoverflow.com/questions/31452451/importing-an-svg-file-a-matplotlib-figure
# ToDo: ?shall linebreak also break strings without whitespace (to fit on pdf)? right now it doesn't!

img=None#if not defined
maxpagerows=45
maxlinelen=82
myprint=print #redirect to other print in main script

def getfiguresheet(): # create figure for graphs to nicely fit on A4
	A4x=8.27
	A4y=11.69
	return(plt.figure(figsize=(A4x,A4y)))

	
def pdftext(text): # make a page with a logo and text: gets called by linebreaker, which makes page-breaks
	global img, maxlinelen, ppi
	# monospaced font to calc how much fits on page width
	
	# Text pages with logo
	
	fig=getfiguresheet()#get one sheet
	# subplot ratios: rows, cols, height/width # todo: scale image with photo=photo.subsample(3)#size down to 1/3 instead of graph, to be less pixely
	gs = gridspec.GridSpec(2, 1, height_ratios=[1, 10])# below this it looks ugly, font max. rows HARDCODED to this size
	ax1=fig.add_subplot(gs[0])
	plt.axis('off') # turnoff for logo
	if not (type('img') == None):
		ax1.imshow(img) # logo
	
	ax3=fig.add_subplot(gs[1])
	plt.axis('off') # turnoff for text
	plt.axis([0, 10, 0, 10])# invisible alignment help for text
	

		
		
	## define font
	
	if os.name == 'nt': # For Windows
		font='Courier New'
	else:# os.name == 'posix': # For Linux, Mac, etc.
		font='DejaVu Sans'
	
	
	
	plt.text(5, 10, text, fontsize=12, style='oblique', ha='center',# hardcoded fontsize
	         va='top', wrap=True, family=font)
	         
	ppi.savefig(fig) # page1 (only text)
	# end pdftext

def splicelines(text,mx): # mx = maxline-len
	k=0
	m=len(text) # how many lines
	
	
	while k<m: # no "for", since dynamically changing length if strings spliced
		line=text[k]
		#myprint(k)
		#remove left and right whitespaces
		line.lstrip(' ')
		line.rstrip(' ')
		
		mylen=len(line)
		while mylen>mx:
			firstpart, secondpart = line[:len(line)//2], line[len(line)//2:]
			#myprint(line)
			text.insert(k,secondpart) # and move current element down
			text.insert(k,firstpart)
			#structure: [fistpart, secondpart, combined]
			text.pop(k+2) # remove combined
			line=firstpart
			mylen=len(line)
			#myprint(line)
			
			m=m+1 # this splice added a line
		k=k+1 # splicing on line complete, continue to next line
			

	return(text)

def linebreaker(text):
	global maxpagerows
	i=1 # line number, total
	k=1 # page number
	page=""
	#text=splicelines(text,maxlinelen)
	
	for item in text:
		page = page + item
		if i==maxpagerows:
			myprint("saving text page "+str(k))
			pdftext(page)
			page=""
			i=1 # reset lineNR for next page
			k=k+1
		else:
			i=i+1
			
	if i!=maxpagerows: #after an unsaved loop
			myprint("saving last text page "+str(k))
			pdftext(page)
			page=""	
#end linebreaker			
	

def create(logo,textlist,figurines,filepath):
	global ppi, img
	with PdfPages(filepath) as pp: #handles pdf open&close
		ppi=pp
		
		if os.path.isfile(logo):
			img=mpimg.imread(logo)# only png supported: ok
			#gets exported as global var into pdftext where it's used
		
		textlist=splicelines(textlist,maxlinelen)
		linebreaker(textlist)
		
		if not (figurines == None): # add graph pages
			for currentfig in figurines:
				myprint("saving figure-only page")
				pp.savefig(currentfig)
		
		#pp.close() # "with" closes it automatically
	
def testlinebreak():
	global maxlinelen
	t=("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmodd")
	t=t+"00"+t+"01"
	#myprint(splicestring(t))
	ls=[t,"hello"]
	ls=ls+ls
	myprint(splicelines(ls,maxlinelen))	
	
def toomanylines(over):
	
	if over:
		overlength="fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
	else:
		overlength=""
		
	t=("Lorem ipsum dolor sit amet, consetetur"+overlength+" sadipscing elitr, sed diam nonumy eirmodd")#as much as this until line breaks --> 80
	lst=[]
	t2=t[:-2]# remove 2 character to append 2pos int
	X = range(0,161)
	#t3 = [t2+str(i)+"\n" for i in X]
	for i in X:
		lst.append(t2+str(i)+"\n")
	return(lst)
		
def testmaxlines():
	global maxpagerows
	#text=''.join(t3)	
	#linebreaker_tst(toomanylines())#wants a list
	#myprint(splicelines(text,maxpagerows))
	
	
if __name__ == "__main__":
	logo = "white-quer2.png" # only pngs supported
	#testlinebreak()
	#testmaxlines()

	
	filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),"pdfhelper-test.pdf") # always chooses right slash depending on OS	
	myprint(filename)
	create(logo,toomanylines(1),None,filename) # always chooses right slash depending on OS
	
