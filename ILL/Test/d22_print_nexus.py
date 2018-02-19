#!/usr/bin/python

'''
Created on August 2012

@author: ricardo.leal@ill.fr

Use this to look for nexus files in a directory. E.g. :

cd /net/serdon/illdata/121/in6
python ~/workspace/PyTests/src/print_nexus_sample.py '*.nxs'

'''

import nxs, sys
import glob


def show(filename):

    print filename,
    f = nxs.open(filename)
    
    # /entry0
    f.opengroup('entry0')

    # /entry0/start_time
    f.opendata('start_time')
    print ';', f.getdata(),
    # /entry0
    f.closedata()
    
    # /entry0/mode
    f.opendata('mode')
    print '; Mode=', f.getdata(),
    # /entry0
    f.closedata()
    
    # /entry0/D33
    f.opengroup('D22') # or 'D33'
    # /entry0/D33/selector
    f.opengroup('selector')
    # /entry0/D33/selector/wavelength 
    f.opendata('wavelength')
    print '; wavelength=', f.getdata(),
    f.closedata()
    f.closegroup()
    f.closegroup()
    
    # /entry0/sample_description
    f.opendata('sample_description')
    print ':', f.getdata(),
    # /entry0
    f.closedata()

    f.closegroup()
    f.close()
    
    print
    
    
 

if __name__ == '__main__':
    
    if len(sys.argv) >= 2: 
        files = glob.glob(sys.argv[1])
        for file in files:
            show(file)
    else:
        print 'Use: %s <Nexus file pattern>' % sys.argv[0]

