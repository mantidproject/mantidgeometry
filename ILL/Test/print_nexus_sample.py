#!/usr/bin/python

'''
Created on August 2012

@author: ricardo.leal@ill.fr

Use this to look for nexus files in a directory. E.g. :

cd /net/serdon/illdata/121/in6
python ~/workspace/PyTests/src/print_nexus_sample.py '*.nxs'

'''

import nxs, os, sys
import numpy as np
import glob
'''



'''

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
    
    # /entry0/title
    try:
        f.opendata('title')
    except:
        f.opendata('experiment_title')
    print ';', f.getdata(),
    # /entry0
    f.closedata()
    
    # /entry0/sample
    f.opengroup('sample')
    # /entry0/sample/chemical_formula
    try :
        f.opendata('chemical_formula')
        print '; Chem:', f.getdata(),
        # /entry0/sample
        f.closedata()
    except:
        pass
        
    
    # /entry0
    f.closegroup()
    
    try :
        # /entry0/walength
        f.opendata('wavelength')
        print ';', f.getdata(), 'A',
        # /entry0
        f.closedata()
    except:
        pass
    
    try:
        # /entry0/experiment_identifier
        f.opendata('experiment_identifier')
    except:
        f.opendata('sample_description')
        
    print '; Id:', f.getdata(),
    
    # /entry0
    f.closedata() 
    
    # /
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

