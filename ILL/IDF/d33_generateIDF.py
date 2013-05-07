'''
Created on Feb 22, 2013

@author: leal

Run as:

python ~/workspace/PyTests/src/d33_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/D33_Definition.xml 

TODO:
- IDs are not correct!!!
- Need to know correspondance between front detector position & ID and Nexus file data field 

'''
import sys
import numpy as np
import time

instrumentName = 'D33'

# Rear Det 1
numberOfPixelsInCentralDetector = 128 * 128
# Dront Det 2
numberOfPixelsInSurroundingDetectors = 32 * 128
numberOfSurroundingDetectors = 4
numberOfPixels = numberOfPixelsInCentralDetector * numberOfPixelsInSurroundingDetectors * numberOfSurroundingDetectors

firstDetectorId = 1
numberOfDetectors = numberOfPixels





def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument name="%s" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="%s">""" %(instrumentName,time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
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
#    print """<idlist idname="detectors">
#        <id start="%d" end="%d" />
#    </idlist>""" % (firstDetectorId, numberOfDetectors)
#    
#    print """<!-- Detector list def -->
#    <component type="detectors" idlist="detectors">
#        <location />
#    </component>"""
    
    print """<component type="detectors">
    <location/>
  </component>"""
    
    print "<!-- Detector Panels -->"
    print """<type name="detectors">"""
    print """ <component type="front_detectors"><location z='1.5'/></component>"""
    print """ <component type="back_detector" idstart="1" idfillbyfirst="y" idstepbyrow="128">
    <location z='3'/></component>"""
    print """</type>"""
    
    print """<type name="front_detectors">"""
    print """ <component type="front_detector" idstart="100000000" idfillbyfirst="y" idstepbyrow="128">
    <location x='0.4' y='0' z='0' rot="90.0" axis-x="0.0" axis-y="0.0" axis-z="1.0"/>
    </component>
    <component type="front_detector" idstart="200000000" idfillbyfirst="y" idstepbyrow="128">
    <location x='-0.4' y='0' z='0' rot="-90.0" axis-x="0.0" axis-y="0.0" axis-z="1.0"/>
    </component>
    <component type="front_detector" idstart="300000000" idfillbyfirst="y" idstepbyrow="128">
    <location x='0' y='0.4' z='0'/>
    </component>
    <component type="front_detector" idstart="400000000" idfillbyfirst="y" idstepbyrow="128">
    <location x='0' y='-0.4' z='0'/>
    </component>"""
    print """</type>"""
    
    
    print "<!-- Definition of every bank -->"
    
    print """<!-- Front detector: 160 x 640 mm (32 x 128 pixels) -->"""
    npixels = 128
    start =  -0.640/2. 
    step = 0.640 / npixels
    print '''<type name="front_detector" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"'''%(npixels,start,step)
    npixels = 32
    start =  -0.160/2. 
    step = 0.160 / npixels
    print ''' ypixels="%d" ystart="%f" ystep="%f" >'''%(npixels,start,step)
    print ''' <properties/>'''
    print """</type>"""  
    
    
    print """<!-- Back detector: 640 x 640 mm -->"""
    npixels = 128
    start =  -0.640/2. 
    step = 0.640 / npixels
    print '''<type name="back_detector" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"'''%(npixels,start,step)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >'''%(npixels,start,step)
    print ''' <properties/>'''
    print """</type>"""  
    
 

def printPixels():  

    print """<!-- Pixel for Detectors: 5x5 mm -->
    <type is="detector" name="pixel">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-0.0025" x="-0.0025" z="0.0"/>
      <left-front-top-point y="0.0025" x="-0.0025" z="0.0"/>
      <left-back-bottom-point y="-0.0025" x="-0.0025" z="-0.0001"/>
      <right-front-bottom-point y="-0.0025" x="0.0025" z="0.0"/>
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
    
    
     
