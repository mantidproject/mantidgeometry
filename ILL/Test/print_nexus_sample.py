#!/usr/bin/python

'''
Created on August 2012

@author: ricardo.leal@ill.fr

Use this to look for nexus files in a directory. E.g. :

cd /net/serdon/illdata/121/in6 
~/workspace/PyTests/src/print_nexus_sample.py '*.nxs'


'''

import nxs, os, sys
import numpy as np
import glob
'''



'''

def show(filename):
    print filename,
    f = nxs.open(filename)
    f.opengroup('entry0')

    f.opendata('start_time')
    print ';', f.getdata(),
    f.closedata()
    
    # print title
    f.opendata('title')
    print ';', f.getdata(),
    f.closedata()
    
    f.opengroup('sample')
    f.opendata('chemical_formula')
    print '; Chem:', f.getdata(),
    f.closedata()
    f.closegroup() #sample
    
    f.opendata('wavelength')
    print ';', f.getdata(), 'A',
    f.closedata()
    
    f.opendata('experiment_identifier')
    print '; Id:', f.getdata(),
    f.closedata() 
    
    f.closegroup() # entry0
    f.close()
    
    print
    
    
 

if __name__ == '__main__':
    
    if len(sys.argv) >= 2: 
        files = glob.glob(sys.argv[1])
        for file in files:
            show(file)
    else:
        print 'Use: %s <Nexus file pattern>' % sys.argv[0]

