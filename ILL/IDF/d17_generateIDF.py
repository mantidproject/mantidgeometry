#!/usr/bin/python

'''

@author: leal

Run as:

python ~/git/mantidgeometry/ILL/IDF/d17_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/mantid/Code/Mantid/instrument/D17_Definition.xml \
rm  ~/git/mantid/Code/Mantid/instrument/D17_Definition.vtp 

'''
import numpy as np
from collections import Counter
import time

# # Global variables
instrumentName='D17'

firstMonitorId = 1
firstDetectorId = 1
radius = 3 # meters

numberOfPixelsPerTube=256
numberOfTubes = 1
tubeHeight = 0.30

tubePixelStep =  tubeHeight / numberOfPixelsPerTube

numberOfDetectors = numberOfPixelsPerTube * numberOfTubes

    
def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" 
    name="%s" valid-from="1900-01-31 23:59:59"
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

def printMonitor():
    print """<!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>
    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="0.0181" name="monitor1"/>
      </component>
    </type>

    <!--MONITOR SHAPE-->
    <!--FIXME: Do something real here.-->
    <type is="monitor" name="monitor">
    <cylinder id="cyl-approx">
    <centre-of-bottom-base y="0.0" x="0.0" z="0.0"/>
    <axis y="0.0" x="0.0" z="1.0"/>
    <radius val="0.01"/>
    <height val="0.03"/>
    </cylinder>
    <algebra val="cyl-approx"/>
    </type>

    <!--MONITOR IDs-->
    <idlist idname="monitors">
    <id val="%d"/>
    </idlist>
    """%(firstMonitorId)

def printDetectors():
    print """<idlist idname="detectors">
        <id start="%d" end="%d" />
    </idlist>""" % (firstDetectorId, numberOfDetectors)
    
    print """<!-- Detector list def -->
    <component type="detectors" idlist="detectors">
        <location />
    </component>"""
    
    print "<!-- Detector Banks -->"
    print """<type name="detectors">"""
    print """  <component type="bank_uniq"><location/></component>"""
    print "</type>"
    
    print "<!-- Definition of the unique existent bank (made of tubes) -->"
    
    print """<type name="bank_uniq">"""
    print """  <component type="standard_tube">"""
    print """    <location r="%f" t="%f" name="tube_uniq" />"""%(radius,0)
    print """  </component>"""
    print """</type>"""
    
    print """<!-- Definition of standard_tube -->"""
    print """<type name="standard_tube" outline="yes">
        <component type="standard_pixel">"""
    pixelPositions = np.linspace(0,tubeHeight,numberOfPixelsPerTube)
    for  pos in pixelPositions :
        print """<location y="%f" />"""%(pos)
    print """</component> </type>"""
    

 

def printPixels():  
#    print """ <type name="pack" is="detector">  
#    <cuboid id="pack-pixel-shape">
#      <left-front-bottom-point x="0.0" y="-0.020" z="-0.0015"  />
#      <left-front-top-point  x="0.0" y="0.020" z="-0.0015"  />
#      <left-back-bottom-point  x="0.005" y="-0.020" z="-0.0015"  />
#      <right-front-bottom-point  x="0.0" y="-0.020" z="0.0015"  />
#    </cuboid>
#    <algebra val="pack-pixel-shape" />     
#    </type>"""
    print """<type name="standard_pixel" is="detector">
        <cylinder id="shape">
            <centre-of-bottom-base x="0.0" y="-0.006144" z="0.0" />
            <axis x="0.0" y="1.0" z="0.0" />
            <radius val="0.0127" />
            <height val=".0114341328125" />
        </cylinder>
        <algebra val="shape" />
    </type>"""
        

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printMonitor()
    printDetectors();
    printPixels();
    printEnd();
    
    
     
