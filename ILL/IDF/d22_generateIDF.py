'''
Created on Feb 22, 2013

@author: leal

Run as:

cd /home/leal/git/mantidgeometry/ILL/IDF; python d22_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/D22_Definition.xml 


'''
import sys
import numpy as np
import time

instrumentName = 'D22'

# detector dims
detDim = 1.0 #m
# 
numberOfPixelsInDetectorH = 128
numberOfPixelsInDetectorW = numberOfPixelsInDetectorH
numberOfPixelsInDetector = numberOfPixelsInDetectorH * numberOfPixelsInDetectorW

firstDetectorId = 1


def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument name="%s" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="%s">""" % (instrumentName, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print """<!-- Author: ricardo.leal@ill.fr -->"""
    print """<defaults>
      <length unit="meter" />
      <angle unit="degree" />
      <reference-frame>
        <!-- The z-axis is set parallel to and in the direction of the beam. the 
             y-axis points up and the coordinate system is right handed. -->
        <along-beam axis="z" />
        <pointing-up axis="y" />
        <handedness val="right" />
      </reference-frame>
    </defaults>

    <component type="moderator">
      <location z="-2" />
    </component>
    <type name="moderator" is="Source"></type>

    <!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>
    <type name="sample-position" is="SamplePos" />"""

def printDetectors():
       
    print """<component type="detectors">
     <location/>
    </component>"""
    
    print "<!-- Detector Panels -->"
    print """<type name="detectors">"""
    print """ <component type="back_detector" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1"> 
    <location z='3'/>
    </component>""" % (firstDetectorId, numberOfPixelsInDetectorW)
    print """</type>"""
    
    print "<!-- Definition of every bank -->"
    
    
    xstep = detDim / numberOfPixelsInDetectorW
    xstart = - detDim /2 + xstep /2 
    ystep = detDim / numberOfPixelsInDetectorH
    ystart = - detDim /2 + ystep /2
    print '''<type name="back_detector" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInDetectorW, -xstart, -xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInDetectorH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    

    
 

def printPixels():  

    print """<!-- Pixel for Detectors: 8x8 mm -->
    <type is="detector" name="pixel">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-0.0040" x="-0.00125" z="0.0"/>
      <left-front-top-point y="0.0040" x="-0.00125" z="0.0"/>
      <left-back-bottom-point y="-0.0040" x="-0.00125" z="-0.0001"/>
      <right-front-bottom-point y="-0.0040" x="0.00125" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
    </type>"""
    

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printDetectors();
    printPixels();
    printEnd();
    
    
     
