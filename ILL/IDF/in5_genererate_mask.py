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

import sys

## Global variables
pixelsToRemoveTop=7
pixelsToRemoveBottom=8
numberOfTubes=384
numberOfPixelsPerTube=256
firstPixelDetectorID=1

def init():
    print """<?xml version="1.0"?>
<detector-masking>
    <group>
        <detids>"""

def finalise():
    print """
    </detids>
    </group>
</detector-masking>
"""

def printMasketPixels():
    thisPixel = firstPixelDetectorID;
    for i in range(numberOfTubes):
        for j in range(numberOfPixelsPerTube):
            if j < pixelsToRemoveBottom or j >= numberOfPixelsPerTube - pixelsToRemoveTop :
                sys.stdout.write('%d'%thisPixel)
                if thisPixel != numberOfTubes * numberOfPixelsPerTube -1  + firstPixelDetectorID:
                    sys.stdout.write(',')
            thisPixel+=1;


    



if __name__ == "__main__":
    init()
    printMasketPixels()
    finalise()
    
