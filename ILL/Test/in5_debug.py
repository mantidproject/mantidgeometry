#!/usr/bin/python

'''
@author: Ricardo Leal
'''

import nxs
import numpy as np
import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

""" CONSTS """

tubeToProbe = 192

l1=2.10855 #m
distanceSampleDetector = 4
wavelength = 5
eiIn = 3.27148
channelWidth = 14.6349  # microsec
#pixelSize = 0.011479 # meters
pixelSize =  0.0122 # meters



""" Calculates CONSTS : Don't edit """

# m/s
neutronSpeed = 6.626E-034 / (1.675E-027 * wavelength * 0.0000000001)



def peakdet(v, delta, x=None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []
       
    if x is None:
        x = np.arange(len(v))
    
    # v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not np.isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = np.Inf, -np.Inf
    mnpos, mxpos = np.NaN, np.NaN
    
    lookformax = True
    
    for i in np.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True
 
    return np.array(maxtab), np.array(mintab)

def epp(v):
    'Return Max EPP'
    maximaPeaks, minimaPeaks = peakdet(v, delta=5, x=None);
    #print maximaPeaks
    if len(maximaPeaks) > 0 :
        maxArr = np.max(maximaPeaks, 0)
        return maxArr[0]
    else :
        return np.NaN
    
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


def getSpectraEPPsForTube(data, tubeNr):
    """
    Reduce one dimension of the 3D array
    """
    
    thisTube = data[tubeNr, :, :]
    numberOfPixelsInTheTube = thisTube.shape[0];
    eppsForThisTube = np.zeros(numberOfPixelsInTheTube);
    for y in range(numberOfPixelsInTheTube):
        thisSpectrum = thisTube[y, :]
        thisEpp = epp(thisSpectrum)
        eppsForThisTube[y] = thisEpp;
    
    return eppsForThisTube

def getTofBins(pos, numberOfChannels):
    """
    pos - pos of the elastic peak
    """
    # v = d/t
    #print 'EPP=', pos,
    t = distanceSampleDetector / neutronSpeed * 1e6
    #print 't=', t
    bins = np.zeros(numberOfChannels)
    for i in range(numberOfChannels):
        bins[i] = t + channelWidth * (i - pos);
    
    return bins

def getDeltaE(ei,l1,l2,tof):
    m = 1.67e-027 # neutron mass
    mev = 1.6e-22
    ei=ei
    ef = 0.5 * m * (l2/ (tof - l1 * np.sqrt(m/(2*(ei*mev))) ))**2 / mev
    #ei=ei*mev
    #ef = 0.5 * m * (l2/ (tof - l1 * np.sqrt(m/(2*(ei))) ))**2
    #print 'ei=', ei, ' ef=', ef 
    return (ei - ef) 


    

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Debug IN5 tof')
    parser.add_argument('-f', '--file', help='Nexus file to parse', required=True)
    args = vars(parser.parse_args())

    data = readData(args['file']);
    print 'Shape of the parsed data:', 'X:', data.shape[0], 'Y:', data.shape[1], 'Z:', data.shape[2]
    xLen =  data.shape[0]
    yLen =  data.shape[1]
    zLen =  data.shape[2]
    
    # array of EPP found for every tube
    eppsForThisTube = getSpectraEPPsForTube(data, tubeToProbe)
    epp = eppsForThisTube[yLen / 2 ]# 
    
    # Plot tube EPPs
    plt1 = plt.figure('EPP')
    ax = plt1.add_subplot(111)
    ax.plot(data[tubeToProbe,yLen/2 , :])
    ax.plot(epp,data[tubeToProbe,yLen/2 ,epp],'o')   
    ax.set_xlim(eppsForThisTube[yLen/2]-20, eppsForThisTube[yLen/2]+20)
    ax.set_ylabel('Counts')
    ax.set_xlabel('Spectra position. EPP=' + str(epp))
    
    # get time bins
    
    timeBins = getTofBins(epp, zLen)
#    print 'timeBins.shape: ', timeBins.shape
#    print 'timeBins: ',timeBins
    #
    
    # get EPPs in time
    eppsInTime = np.zeros(yLen);
    for idx,e in enumerate(eppsForThisTube):
        if not np.isnan(e):
            eppsInTime[idx] = timeBins[int(e)]
        else :
            eppsInTime[idx] = np.NAN

    print 'eppsInTime.shape: ', eppsInTime.shape
    print 'eppsInTime: ',eppsInTime
                
    # Plot time differences
    eppInTime = eppsInTime[yLen/2]
    deltaEppsInTime = eppsInTime - eppInTime
    
    print 'deltaEppsInTime.shape: ', deltaEppsInTime.shape
    print 'deltaEppsInTime: ',deltaEppsInTime
    
    plt2 = plt.figure('Delta TOF vs Position')
    ax2 = plt2.add_subplot(111)
    ax2.plot(deltaEppsInTime,'o', label='DeltaTof')
    ax2.set_ylabel('Delta TOF (micro-sec)')
    ax2.set_xlabel('Tube position')
    
    #
    distanceInTime = np.zeros(yLen);
    pos = yLen/2
    for i in range(len(deltaEppsInTime)):
        thisDistance = np.sqrt( distanceSampleDetector*distanceSampleDetector +  ((i - pos)*pixelSize*(i - pos)*pixelSize) );
        distanceInTime[i] = thisDistance / neutronSpeed * 1e6
    
    deltaDistanceInTime = distanceInTime - distanceInTime[pos]
    
    ax2.plot( deltaDistanceInTime,'-', label='deltaDistanceInTime')
    
    # Let's do the delta energy:
    deltaE = np.zeros(yLen);
    pos = yLen/2
    for i in range(yLen):
        l2 = np.sqrt( distanceSampleDetector*distanceSampleDetector +  ((i - pos)*pixelSize*(i - pos)*pixelSize) );
        tof = ( l1 + l2 ) / neutronSpeed
        # getDeltaE(ei,l1,l2,tof):
        deltaE[i] = getDeltaE(eiIn, l1, l2, tof)
    
    plt3 = plt.figure('Delta Ei')
    ax3 = plt3.add_subplot(111)
    ax3.set_ylabel('Delta Ei')
    ax3.set_xlabel('Tube position')
    ax3.plot( deltaE,'.', label='deltaEi')
    
    
    # Let's do the delta energy with corrected distance
    deltaE = np.zeros(yLen);
    pos = yLen/2
    for i in range(yLen):
        l2 = np.sqrt( distanceSampleDetector*distanceSampleDetector +  ((i - pos)*pixelSize*(i - pos)*pixelSize) );
        print 'l2=',l2,
        tof = ( l1 + l2 ) / neutronSpeed
        print 'TOF=',tof*1e6,
        deltaL2 = np.abs(l2 -  distanceSampleDetector)
        print 'deltaL2=',deltaL2,
        deltaL2Tof = deltaL2 / neutronSpeed
        print 'deltaL2Tof=',deltaL2Tof*1e6         
        
        # getDeltaE(ei,l1,l2,tof):
        # This correct but I have no access to L2 in mantid
        # deltaE[i] = getDeltaE(eiIn, l1, l2-deltaL2, tof-deltaL2Tof)
        deltaE[i] = getDeltaE(eiIn, l1, l2-deltaL2, tof-deltaL2Tof)
    
    plt4 = plt.figure('Delta Ei Corr')
    ax4 = plt4.add_subplot(111)
    ax4.set_ylabel('Delta Ei')
    ax4.set_xlabel('Tube position')
    ax4.plot( deltaE,'.', label='deltaEi')


    
    
        
    
    # plot(timeBins, eppsForThisTube)
    # plot(eppsForThisTube)
    plt.show()
