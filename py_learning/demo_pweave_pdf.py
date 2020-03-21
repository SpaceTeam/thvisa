#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  08 12:09:57 2020

@author: thirschbuechler

Demo for accessing
https://github.com/mpastell/Pweave
	according to
	http://mpastell.com/pweave/pweave.html
	Code chunk formatting:
	http://mpastell.com/pweave/chunks.html
		if this is messed up, it will error out with something like:
		    chunkoptions =  dict(echo=False include=True)

	Direct output formats:
	http://mpastell.com/pweave/formats.html


Anaconda pweave install:
conda install -c conda-forge pweave

anaconda pdfkit install failed

pdf creation :
	https://www.geeksforgeeks.org/python-convert-html-pdf/
	--> todo: does "updateformat(pdf) work better?
		http://mpastell.com/pweave/customizing.html
"""
import pweave
import pdfkit

print("This might not run inside spyder, because it wants to open an ipython console itself")
print("and there apparently can only be one")
print("")
print("note: executing this doesn't throw an error if the python code there itself is faulty")
print("the error will just be printed into the output doc")

# Weave a pandoc document with default options
#pweave.weave('FIR_designp.pmd', doctype = "pandoc") # makes markdown, works
#pweave.weave('FIR_designp.pmd', doctype = "md2html") # makes html, works
#pweave.weave('pywave_md.mdw', doctype = "md2html") # makes html, works
pweave.weave('pywave_md.pmd', doctype = "md2html")# makes html, works

pdfkit.from_file('pywave_md.html', 'pywave_md_pdfkit.pdf') 

# NOTE: this seems to use online-resources, outdated wkhtmltopdf to be precise
# (pweave File failed to load: https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/jax/input/LaTeX/config.js)
# https://blog.rebased.pl/2018/07/12/wkhtmltopdf-considered-harmful.html

# toDo: try weasyprint
# https://weasyprint.readthedocs.io/en/stable/tutorial.html