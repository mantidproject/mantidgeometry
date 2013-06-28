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

# Front Dets Side x2
numberOfPixelsInFrontSideDetectorsH = 256
numberOfPixelsInFrontSideDetectorsW = 32
numberOfPixelsInFrontSideDetectors = numberOfPixelsInFrontSideDetectorsH * numberOfPixelsInFrontSideDetectorsW 

# Front Dets Top Bottom x2
numberOfPixelsInFrontVerticalDetectorsH = 32
numberOfPixelsInFrontVerticalDetectorsW = 256
numberOfPixelsInFrontVerticalDetectors = numberOfPixelsInFrontVerticalDetectorsH * numberOfPixelsInFrontVerticalDetectorsW 

numberOfPixels = numberOfPixelsInBackDetector * 2 * numberOfPixelsInFrontSideDetectors * 2 * numberOfPixelsInFrontVerticalDetectors

firstDetectorId = 1
numberOfDetectors = numberOfPixels


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
    print """ <component type="back_detector" idstart="%d" idfillbyfirst="y" idstepbyrow="%d"> <location z='3'/>
    </component>""" % (firstDetectorId, numberOfPixelsInBackDetectorW)
    acc = firstDetectorId + numberOfPixelsInBackDetector
    
    print """ <component type="front_detector_right" idstart="%d" idfillbyfirst="y" idstepbyrow="%d"> 
    <location x='0.4' y='0' z='1' />
    </component>"""%(acc,numberOfPixelsInFrontSideDetectorsW)
    acc += numberOfPixelsInFrontSideDetectors
    
    print """ <component type="front_detector_left" idstart="%d" idfillbyfirst="y" idstepbyrow="%d">
    <location x='-0.4' y='0' z='1' />
    </component>"""%(acc,numberOfPixelsInFrontSideDetectorsW)
    acc += numberOfPixelsInFrontSideDetectors
    
    print """ <component type="front_detector_bottom" idstart="%d" idfillbyfirst="y" idstepbyrow="%d">
    <location x='0' y='-0.4' z='1' />
    </component>"""%(acc,numberOfPixelsInFrontVerticalDetectorsW)
    acc += numberOfPixelsInFrontVerticalDetectors
    
    print """ <component type="front_detector_top" idstart="%d" idfillbyfirst="y" idstepbyrow="%d">
    <location x='0' y='0.4' z='1'/>
    </component>"""%(acc,numberOfPixelsInFrontVerticalDetectorsW)
    
    print """</type>"""
    
    print "<!-- Definition of every bank -->"
    
    print """<!-- Back detector: 640 x 640 mm -->"""
    
    xstep = detLargeDim / numberOfPixelsInBackDetectorW
    xstart = - detLargeDim /2 + xstep /2 
    ystep = detLargeDim / numberOfPixelsInBackDetectorH
    ystart = - detLargeDim /2 + ystep /2
    print '''<type name="back_detector" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInBackDetectorW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInBackDetectorH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    
    print """<!-- Front detector: side pannels -->"""
    
    xstep = detShortDim / numberOfPixelsInFrontSideDetectorsW
    xstart = - detShortDim /2 + xstep /2 
    ystep = detLargeDim / numberOfPixelsInFrontSideDetectorsH
    ystart = - detLargeDim /2 + ystep /2
    print '''<type name="front_detector_right" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontSideDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontSideDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    print '''<type name="front_detector_left" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontSideDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontSideDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>''' 
    
    print """<!-- Front detector: top / buttom pannels -->"""
    
    xstep = detLargeDim / numberOfPixelsInFrontVerticalDetectorsW
    xstart = - detLargeDim /2 + xstep /2 
    ystep = detShortDim / numberOfPixelsInFrontVerticalDetectorsH
    ystart = - detShortDim /2 + ystep /2
    print '''<type name="front_detector_bottom" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontVerticalDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontVerticalDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>'''  
    print '''<type name="front_detector_top" is="rectangular_detector" type="pixel"''' 
    print ''' xpixels="%d" xstart="%f" xstep="%f"''' % (numberOfPixelsInFrontVerticalDetectorsW, xstart, xstep)
    print ''' ypixels="%d" ystart="%f" ystep="%f" >''' % (numberOfPixelsInFrontVerticalDetectorsH, ystart, ystep)
    print ''' <properties/>'''
    print '''</type>''' 
    
 

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
    
    
     
