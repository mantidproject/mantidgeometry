'''
Created on 12/03/2014

@author: leal/raoul

Run as:

cd /home/raoul/git/mantidgeometry/ILL/IDF; python in16b_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/IN16B_Definition.xml 
                  
'''
import numpy as np
from collections import Counter
import time

# # Global variables
instrumentName='IN16B'
numberOfPixelsPerTube=128
firstDetectorId = 1
radius = 2 * 2.0 -0.0644 # meters

tubeHeight = 0.30
tubePixelStep =  tubeHeight / numberOfPixelsPerTube
totalTubeHeight = tubePixelStep * numberOfPixelsPerTube
numberOfTubes= 16

numberOfDetectors = numberOfPixelsPerTube * numberOfTubes
numberOfSingleDetectors = 8

azimuthalAngle = np.linspace(128,-13.7,numberOfTubes)
azimuthalSingleAngle = np.linspace(10,120,numberOfSingleDetectors)
singleDetectorRadius = 4.10

def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" 
    name="%s" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="%s">""" % (instrumentName, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print """<!-- Author: raoul@ill.fr -->"""
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

    <!--Moderator -->
    <component type="moderator">
      <location z="-36.41" />
    </component>
    <type name="moderator" is="Source"></type>

    <!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>
    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="0.0181" name="monitor1"/>
      </component>
    </type>

    <!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>
    <type name="sample-position" is="SamplePos" />"""

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
    for idx,angle in enumerate(azimuthalAngle):
        print """<location r="%f" t="%f" name="tube_%d" />"""%(radius,angle,idx+1)
    print """  </component>"""
    print """</type>"""
    
    print """<!-- Definition of standard_tube -->"""
    print """<type name="standard_tube" outline="yes">
        <component type="standard_pixel">"""
    pixelPositions = np.linspace(-totalTubeHeight/2,totalTubeHeight/2,numberOfPixelsPerTube)
    for  pos in pixelPositions :
        print """<location y="%f" />"""%(pos)
    print """</component> </type>"""
    


    
    
    
def printSimpleSingleDetectors():
    print """<idlist idname="single_detectors">
        <id start="%d" end="%d" />
    </idlist>""" % (numberOfDetectors+1, numberOfDetectors+numberOfSingleDetectors)

    print """<!-- Detector list def -->
    <component type="single_detectors" idlist="single_detectors">
        <location />
        <!--location x="0.0" y="0.0" z="0.0" rot="0.0" axis-x="1.0" axis-y="0.0" axis-z="0.0"/-->
    </component>"""
    
    print "<!-- Detector Banks -->"
    print """<type name="single_detectors">"""
    print """  <component type="bank_single_detectors"><location/></component>"""
    print "</type>"

    print "<!-- Definition of the bank_single_detectors -->"
    print """<type name="bank_single_detectors">"""
    
    print """  <component type="single_tube">"""
    
    
    for idx,angle in enumerate(azimuthalSingleAngle):
        print """<location r="%f" t="%f" p="0.0" rot="%f" axis-x="0.0" axis-y="1.0" axis-z="0.0" name="single_tube_%d" />"""%(singleDetectorRadius,angle,angle+90.0,idx+1)
    
    print """  </component>"""
    print """</type>"""

    print """<!-- Definition of single_tube -->"""
    print """<type name="single_tube" outline="yes">
             <component type="single_pixel">"""
    print """<location />"""
    print """</component> </type>"""

      
      
def printMonitors():
    print """<!--MONITOR SHAPE-->
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
    <id val="0"/>
    </idlist>
    """ 

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
        <cylinder id="cyl1">
            <centre-of-bottom-base x="0.0" y="-0.006144" z="0.0" />
            <axis x="0.0" y="1.0" z="0.0" />
            <radius val="0.0127" />
            <height val=".0114341328125" />
        </cylinder>
        <algebra val="cyl1" />
    </type>"""
        
    print """<type name="single_pixel" is="detector">
        <cylinder id="cyl2">
            <centre-of-bottom-base x="0.0" y="0.0" z="0.0" />
            <axis x="1.0" y="0.0" z="0.0" />
            <radius val="0.027" />
            <height val=".10" />
        </cylinder>
    </type>"""
    
def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printDetectors();
    printSimpleSingleDetectors();
    printMonitors()
    printPixels();
    printEnd();
    
    
     
