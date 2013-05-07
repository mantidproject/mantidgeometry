#!/usr/bin/python

'''
Created on 24 Nov 2012

@author: leal
'''
import nxs
import scipy.io as sio
import argparse

# http://docs.enthought.com/mayavi/mayavi/mlab_case_studies.html#mlab-case-studies

def readData(filePath='/home/leal/Documents/Mantid/IN5/094460.nxs'):
    f = nxs.open(filePath)
    f.opengroup('entry0')
    f.opengroup('data')
    f.opendata('data')
    a = f.getdata()
    f.closedata()
    f.closegroup()
    f.closegroup()
    f.close()
    # a.shape
    # Out[15]: (384, 256, 512)
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debug IN5 tof')
    parser.add_argument('-i', '--infile', help='Input Nexus file to parse', required=True)
    parser.add_argument('-o', '--outfile', help='Output matlab file', required=True)
    args = vars(parser.parse_args())
    
    print 'Reading data...'
    a = readData(args['infile'])
    print 'Saving data...'
    sio.savemat(args['outfile'], {'arr': a})
    print 'Done!'
