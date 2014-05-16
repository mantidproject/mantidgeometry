#!/usr/bin/python

'''

@author: leal

Run as:

python ~/git/mantidgeometry/ILL/IDF/d17_generateIDF.py | \
tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/mantid/Code/Mantid/instrument/D17_Definition.xml;
rm  ~/git/mantid/Code/Mantid/instrument/D17_Definition.vtp


Going to assume a rectangular detector like in SANS 

'''
import time

# # Global variables
instrumentName='D17'

# 2 monitors
firstMonitorId = 0
firstDetectorId = 2
radius = 3.1 # meters #

# Tubes are horizontal!
numberOfPixelsPerTube=256
numberOfTubes = 1
tubePixelSize = 0.0012
tubeWidth = 0.0067

numberOfPixels = numberOfPixelsPerTube * numberOfTubes
 

    
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
    </defaults>"""

    print """<!-- Source -->"""
    print """<component type="chopper1">
      <location z="-4.16610003" />
    </component>
    <type name="chopper1" is="Source"></type>"""

    print """<!-- Sample position -->"""
    print """<component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>
    <type name="sample-position" is="SamplePos" />"""

def printMonitors():
    print """<!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>
    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="0.0181" name="monitor1"/>
        <location z="-0.5" name="monitor2" />
      </component>
    </type>"""

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
    </type>"""

    print """<!--MONITOR IDs-->
      <idlist idname="monitors">
        <id start="%d" end="%d" />
      </idlist>
    """%(firstMonitorId, firstDetectorId -1 )

def printDetectors():
    print """<component type="detectors">
     <location/>
    </component>"""
    
    print "<!-- Detector Panels -->"
    print """<type name="detectors">"""
    print """ <component type="uniq_detector" idstart="%d" idfillbyfirst="x" idstep="1" idstepbyrow="%d"> 
    <location z='%f'/>
    </component>
    </type>""" % (firstDetectorId, numberOfPixelsPerTube, radius)
    
    print "<!-- Definition of the detector -->"
    print "<!-- Back detector: 30.7 x 42.9 mm -->"
    
    
#     ystart = - ( tubePixelSize * numberOfPixelsPerTube ) /2
#     print '''<type name="uniq_detector" is="rectangular_detector" type="pixel"''' 
#     print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfTubes, 0 , tubeWidth)
#     print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsPerTube, ystart, tubePixelSize)
#     print ''' <properties/>'''
#     print '''</type>''' 
#     
    xstart = 0
    ystart = - ( tubeWidth * numberOfTubes ) / 2
    
    print '''<type name="uniq_detector" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsPerTube, xstart , tubePixelSize)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfTubes, ystart, tubeWidth)
    print ''' <properties/>'''
    print '''</type>''' 
    
 

def printPixels():  
    
    stepY = tubeWidth - 0.001
    stepX = tubePixelSize -0.0003
    print """<!-- Pixel size = tubePixelSize * tubeWidth-->
    <type is="detector" name="pixel">
    <cuboid id="pixel-shape">"""
    print """<left-front-bottom-point y="%f" x="%f" z="0.0"/>""" % (-stepY, -stepX)
    print """<left-front-top-point y="%f" x="%f" z="0.0"/>""" %(stepY, -stepX)
    print """<left-back-bottom-point y="%f" x="%f" z="-0.0001"/>""" %(-stepY,-stepX)
    print """<right-front-bottom-point y="%f" x="%f" z="0.0"/>""" %(-stepY,stepX)
    print """</cuboid>
    <algebra val="pixel-shape"/>
    </type>"""
        

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printMonitors()
    printDetectors();
    printPixels();
    printEnd();
    
    
     
