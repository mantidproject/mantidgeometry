#!/usr/bin/python

'''
@author: Ricardo Leal

Generates a file mask.xml for IN5.

Use it as:

maskFile = r'/home/leal/git/Mantid/Code/Mantid/instrument/masks/IN5_Mask.xml'
LoadMask(Instrument='IN5',InputFile=maskFile ,OutputWorkspace='IN5_Mask')
# Apply mask to the detector - data
MaskDetectors(Workspace='Data',MaskedWorkspace='IN5_Mask')
    
'''


import numpy as np
import sys
import os
mantidBinDir    = '/home/leal/git/Mantid/Build/bin/'
sys.path.append(mantidBinDir)
from mantidsimple import *
     
## Global variables
pixelsToRemoveTop=7
pixelsToRemoveBottom=8
numberOfTubes=384
numberOfPixelsPerTube=256
firstPixelDetectorID=1

##
pixelsToLimitBeamStopTop=66
pixelsToLimitBeamStopBottom=65
fixedMask = "87912-87960,88168-88216,88424-88472,88680-88728,88936-88984,89192-89240,89448-89496,89704-89752,89960-90008,90216-90264,90472-90520,90728-90776,90984-91032,91240-91288,91496-91544,91752-91800,92008-92056,92264-92312,92520-92568"
pixelsToRemoveFromMask = '94823,94882-94913' 
dataFile        = '/home/leal/Documents/Mantid/IN5/2013-02-08/102296.nxs'
tubesToConsiderForBeamStop = ['tube_%d'%(i) for i in range(334,372)]

outputMaskFile = '/tmp/mask_in5.xml'

maskedPixels = []

def initXmlFile():
    return """<?xml version="1.0"?>
<detector-masking>"""

def finaliseXmlFile():
    return """
</detector-masking>
"""


def initMask():
    return """
    <group>
        <detids>"""

def finaliseMask():
    return """
    </detids>
    </group>
"""

def maskTopAndBottom():
    thisPixel = firstPixelDetectorID;
    for i in range(numberOfTubes):
        for j in range(numberOfPixelsPerTube):
            if j < pixelsToRemoveBottom or j >= numberOfPixelsPerTube - pixelsToRemoveTop :
                maskedPixels.append(thisPixel)
            thisPixel+=1;


def convertStringToRangeList(s):
    """ 
    f('1,2,5-7,10')
    [1, 2, 5, 6, 7, 10]
    """
    return sum(((list(range(*[int(j) + k for k,j in enumerate(i.split('-'))]))
         if '-' in i else [int(i)]) for i in s.split(',')), [])

def maskFixedMask():
    global maskedPixels
    l = convertStringToRangeList(fixedMask)
    maskedPixels = maskedPixels + l
    
    
    
def maskBeamStop():
    global maskedPixels
    data = Load(Filename=dataFile,OutputWorkspace='Data')
    ws = data[0]
    
    thisPixel = firstPixelDetectorID
    for i in range(numberOfTubes):
        for j in range(numberOfPixelsPerTube):
            if j > pixelsToLimitBeamStopBottom and j <= numberOfPixelsPerTube - pixelsToLimitBeamStopTop :
                pixelIndex = thisPixel - firstPixelDetectorID
                det = ws.getDetector(pixelIndex)
                spectra = ws.readY(pixelIndex)
                sum = np.sum(spectra)
                if sum < 100 and det.getFullName().split('/')[-2] in tubesToConsiderForBeamStop:
                    maskedPixels.append(thisPixel)
            thisPixel+=1;
    
#     nHists = ws.getNumberHistograms()
#     for i in range(0, nHists):
#         det = ws.getDetector(i)
#         detId = det.getID()
#         spectra = ws.readY(i)
#         sum = np.sum(spectra)
#         if sum < 100 and det.getFullName().split('/')[-2] in tubesToConsiderForBeamStop:
#             listOfPixelsToMask.append(detId)
#     maskedPixels = maskedPixels + listOfPixelsToMask
        
    
def maskLastPanel():
    global maskedPixels
    maskedPixels = maskedPixels + range(90113,numberOfTubes * numberOfPixelsPerTube + 1)


if __name__ == "__main__":
    maskTopAndBottom()
    maskFixedMask()
    maskBeamStop()
    # maskLastPanel()
    
    f= open(outputMaskFile,'w')
    f.write(initXmlFile())
    f.write(initMask())
    
    s = set(maskedPixels)
    
    # remove a few pixels left by the beamstop mask in the last pannel
    # Comment this 2 lines out if maskLastPanel is used!
    l = convertStringToRangeList(pixelsToRemoveFromMask)
    s = s - set(l)
    
    for idx,i in enumerate(s):
        if idx == len(s)-1:
            f.write('%d'%i)
        else:
            f.write('%d,'%i)
    
    
    f.write(finaliseMask())
    f.write(finaliseXmlFile())
    f.close()
    
    print 'Mask File written to:', outputMaskFile
    
    
