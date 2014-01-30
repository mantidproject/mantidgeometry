'''
Created on Feb 22, 2013

@author: leal

Run as:

cd /home/leal/git/mantidgeometry/ILL/IDF; python d33_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/D33_Definition.xml 

TODO:
- IDs are not correct!!!
- Need to know correspondance between front detector position & ID and Nexus file data field 


        'D33':   begin                   
  ;         -------------------------------------- 
  ;        |             Front 5                  | [256*32]
  ;        |                                      |
  ;         --------------------------------------
  ;  -----  --------------------------------------  -----
  ; |     ||                                      ||     |             Detector distances
  ; |     ||                                      ||     |             idx54         ;Sample -> rear     detector (number 1)
  ; |     ||                                      ||     |             idx55         ;Sample -> bottom   detector (#4)
  ; |     ||                                      ||     |                           ;sample -> top      detector (#5)
  ; |     ||                                      ||     |             idx55 + idx56 ;Sample -> right    detector (#2)
  ; |     ||                                      ||     |                           ;sample -> left detector (#3)
  ; |     ||                                      ||     |             idx57 *1.e-3  ;Left      shift of detector #3  [in m]
  ; |     ||                                      ||     |             idx58 *1.e-3  ;Right     shift of detector #2  [in m]
  ; |     ||                                      ||     |             idx59 *1.e-3  ;Downwards shift of detector #4  [in m]
  ; | F3  ||             Rear 1 [256*128]         || F2  |             idx60 *1.e-3  ;Upwards   shift of detector #5  [in m]
  ; |     ||                                      ||     |
  ; |     ||                                      ||     | [32*256]
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ; |     ||                                      ||     |
  ;  -----  --------------------------------------  -----
  ;         -------------------------------------- 
  ;        |            Front 4                   | [256*32]
  ;        |                                      |
  ;         --------------------------------------
                  
'''
import sys
import numpy as np
import time

instrumentName = 'D33'

# detector dims
detLargeDim = 0.64 #m
detShortDim = 0.16


# Rear Det 1
numberOfPixelsInBackDetectorH = 128
numberOfPixelsInBackDetectorW = 256
numberOfPixelsInBackDetector = numberOfPixelsInBackDetectorH * numberOfPixelsInBackDetectorW

# Front Dets Side x2 and Dets Top Bottom x2
numberOfPixelsInFrontDetectorsH = 32
numberOfPixelsInFrontDetectorsW = 256
numberOfPixelsInFrontDetectors = numberOfPixelsInFrontDetectorsH * numberOfPixelsInFrontDetectorsW 

firstDetectorId = 1
numberOfDetectors = numberOfPixelsInBackDetector + 4 * numberOfPixelsInFrontDetectors


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

    <!--Moderator -->
    <component type="moderator">
      <location z="-22" />
    </component>
    <type name="moderator" is="Source"></type>

    <!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>
    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="-16.700" name="monitor1"/>
        <location z="-1.200" name="monitor2"/>
      </component>
    </type>

    <!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>
    <type name="sample-position" is="SamplePos" />"""

def printDetectors():
    
#     print """<idlist idname="detectors">
#         <id start="%d" end="%d" />
#     </idlist>""" % (firstDetectorId, numberOfDetectors)
#     
#     print """<!-- Detector list def -->
#     <component type="detectors" idlist="detectors">
#         <location />
#     </component>"""
    
    print """<component type="detectors">
     <location/>
    </component>"""
    
    print "<!-- Detector Panels -->"
    print """<type name="detectors">"""
    print """ <component type="back_detector" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1"> 
    <location z='3'/>
    </component>""" % (firstDetectorId, numberOfPixelsInBackDetectorW)
    acc = firstDetectorId + numberOfPixelsInBackDetector
    
    print """ <component type="front_detector_right" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1"> 
    <location x='0.4' y='0' z='1' rot="90.0" axis-x="0.0" axis-y="0.0" axis-z="1.0"/>
    </component>"""%(acc,numberOfPixelsInFrontDetectorsW)
    acc += numberOfPixelsInFrontDetectors
    
    print """ <component type="front_detector_left" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1">
    <location x='-0.4' y='0' z='1' rot="90.0" axis-x="0.0" axis-y="0.0" axis-z="1.0"/>
    </component>"""%(acc,numberOfPixelsInFrontDetectorsW)
    acc += numberOfPixelsInFrontDetectors
    
    
    print """ <component type="front_detector_bottom" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1">
    <location x='0' y='-0.4' z='1' />
    </component>"""%(acc,numberOfPixelsInFrontDetectorsW)
    acc += numberOfPixelsInFrontDetectors
    
    print """ <component type="front_detector_top" idstart="%d" idfillbyfirst="y" idstep="%d" idstepbyrow="1">
    <location x='0' y='0.4' z='1'/>
    </component>"""%(acc,numberOfPixelsInFrontDetectorsW)
    
    print """</type>"""
    
    print "<!-- Definition of every bank -->"
    
    print """<!-- Back detector: 640 x 640 mm -->"""
    
    xstep = detLargeDim / numberOfPixelsInBackDetectorW
    xstart = - detLargeDim /2 + xstep /2 
    ystep = detLargeDim / numberOfPixelsInBackDetectorH
    ystart = - detLargeDim /2 + ystep /2
    print '''<type name="back_detector" is="rectangular_detector" type="pixel_rectangular_vertical"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInBackDetectorW, -xstart, -xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInBackDetectorH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    
    print """<!-- Front detectors -->"""
    
    xstep = detLargeDim / numberOfPixelsInFrontDetectorsW
    xstart = - detLargeDim /2 + xstep /2 
    ystep =  detShortDim / numberOfPixelsInFrontDetectorsH
    ystart = - detShortDim /2 + ystep /2
    print '''<type name="front_detector_right" is="rectangular_detector" type="pixel_rectangular_vertical"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    print '''<type name="front_detector_left" is="rectangular_detector" type="pixel_rectangular_vertical"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>''' 
    print '''<type name="front_detector_bottom" is="rectangular_detector" type="pixel_rectangular_vertical"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontDetectorsW, -xstart, -xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    print '''<type name="front_detector_top" is="rectangular_detector" type="pixel_rectangular_vertical"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontDetectorsW, -xstart, -xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>''' 
    

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
    <id val="-1"/>
    <id val="0"/>
  </idlist>
  """ 

def printPixels():  

    ## TODO correct pixel shape for top and side detectors.
    print """<!-- Pixel for Detectors: 2.5x5 mm -->
    <type is="detector" name="pixel_rectangular_horizontal">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-0.0025" x="-0.00125" z="0.0"/>
      <left-front-top-point y="0.0025" x="-0.00125" z="0.0"/>
      <left-back-bottom-point y="-0.0025" x="-0.00125" z="-0.0001"/>
      <right-front-bottom-point y="-0.0025" x="0.00125" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
    </type>
    <!-- Pixel for Detectors: 5x2.5 mm -->
    <type is="detector" name="pixel_rectangular_vertical">
    <cuboid id="pixel-shape">
      <left-front-bottom-point y="-0.00125" x="-0.0025" z="0.0"/>
      <left-front-top-point y="0.00125" x="-0.0025" z="0.0"/>
      <left-back-bottom-point y="-0.00125" x="-0.0025" z="-0.0001"/>
      <right-front-bottom-point y="-0.00125" x="0.0025" z="0.0"/>
    </cuboid>
    <algebra val="pixel-shape"/>
    </type>
    """
    

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader()
    printDetectors()
    printMonitors()
    printPixels()
    printEnd()
    
    
     
