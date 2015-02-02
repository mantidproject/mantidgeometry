#!/usr/bin/python

'''
Created on Feb 22, 2013

@author: leal, raoul

Run as:

cd ~/git/mantidgeometry/ILL/IDF
python in6_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/mantid/Code/Mantid/instrument/IN6_Definition.xml 

'''

import sys
import math
import numpy as np
from collections import Counter
from time import gmtime, strftime

azimuthalAngle = [10.33, 11.11, 11.89, 12.67, 13.73, 14.51, 15.29, 16.07, 17.13, 17.13, 17.13, 17.91, 17.91, 17.91, 18.69, 18.69, 18.69, 19.47, 20.53, 20.53, 20.53, 21.31, 21.31, 21.31, 22.09, 22.09, 22.09, 22.87, 23.93, 23.93, 23.93, 24.71, 24.71, 24.71, 25.49, 25.49, 25.49, 26.27, 27.33, 27.33, 27.33, 28.11, 28.11, 28.11, 28.89, 28.89, 28.89, 29.67, 30.73, 30.73, 30.73, 31.51, 31.51, 31.51, 32.29, 32.29, 32.29, 33.07, 34.13, 34.13, 34.13, 34.91, 34.91, 34.91, 35.69, 35.69, 35.69, 36.47, 37.53, 37.53, 37.53, 38.31, 38.31, 38.31, 39.09, 39.09, 39.09, 39.87, 40.93, 40.93, 40.93, 41.71, 41.71, 41.71, 42.49, 42.49, 42.49, 43.27, 44.33, 44.33, 44.33, 45.11, 45.11, 45.11, 45.89, 45.89, 45.89, 46.67, 46.67, 46.67, 47.73, 47.73, 47.73, 48.51, 48.51, 48.51, 49.29, 49.29, 49.29, 50.07, 50.07, 50.07, 51.13, 51.13, 51.13, 51.91, 51.91, 51.91, 52.69, 52.69, 52.69, 53.47, 53.47, 53.47, 54.53, 54.53, 54.53, 55.31, 55.31, 55.31, 56.09, 56.09, 56.09, 56.87, 56.87, 56.87, 57.93, 57.93, 57.93, 58.71, 58.71, 58.71, 59.49, 59.49, 59.49, 60.27, 60.27, 60.27, 61.33, 61.33, 61.33, 62.11, 62.11, 62.11, 62.89, 62.89, 62.89, 63.67, 63.67, 63.67, 64.73, 64.73, 64.73, 65.51, 65.51, 65.51, 66.29, 66.29, 66.29, 67.07, 67.07, 67.07, 68.13, 68.13, 68.13, 68.91, 68.91, 68.91, 69.69, 69.69, 69.69, 70.47, 70.47, 70.47, 71.53, 71.53, 71.53, 72.31, 72.31, 72.31, 73.09, 73.09, 73.09, 73.87, 73.87, 73.87, 74.93, 74.93, 74.93, 75.71, 75.71, 75.71, 76.49, 76.49, 76.49, 77.27, 77.27, 77.27, 78.33, 78.33, 78.33, 79.11, 79.11, 79.11, 79.89, 79.89, 79.89, 80.67, 80.67, 80.67, 81.73, 81.73, 81.73, 82.51, 82.51, 82.51, 83.29, 83.29, 83.29, 84.07, 84.07, 84.07, 85.13, 85.13, 85.13, 85.91, 85.91, 85.91, 86.69, 86.69, 86.69, 87.47, 87.47, 87.47, 88.53, 88.53, 88.53, 89.31, 89.31, 89.31, 90.09, 90.09, 90.09, 90.87, 90.87, 90.87, 91.93, 91.93, 91.93, 92.71, 92.71, 92.71, 93.49, 93.49, 93.49, 94.27, 94.27, 94.27, 95.33, 95.33, 95.33, 96.11, 96.11, 96.11, 96.89, 96.89, 96.89, 97.67, 97.67, 97.67, 98.73, 98.73, 98.73, 99.51, 99.51, 99.51, 100.29, 100.29, 100.29, 101.07, 101.07, 101.07, 102.93, 102.93, 102.93, 103.71, 103.71, 103.71, 104.49, 104.49, 104.49, 105.57, 105.57, 105.57, 106.35, 106.35, 106.35, 107.13, 107.13, 107.13, 108.21, 108.21, 108.21, 108.99, 108.99, 108.99, 109.77, 109.77, 109.77, 110.85, 110.85, 110.85, 111.63, 111.63, 111.63, 112.41, 112.41, 112.41, 113.49, 113.49, 113.49, 114.27, 114.27, 114.27, 115.05, 115.05, 115.05]
# reduced set used for debugging :
#azimuthalAngle = [10.33, 17.13, 17.13, 17.13, 30.73, 30.73, 30.73, 90.0, 90.0, 90.0, 110.0, 110.0, 110.0 ]

# # Global variables
numberOfDetectors = len(azimuthalAngle)
firstDetectorId = 3
firstBankId = 1
radius = 2.483  # meters
angle = 15  # degrees # vertical detection angle


# Don't touch!
uniqueDic = Counter(azimuthalAngle)
numberOfBanks = len(uniqueDic)
uniqueAngles = np.array([k for k, v in sorted(uniqueDic.iteritems())])
numberOfDetsPerBank = np.array([v for k, v in sorted(uniqueDic.iteritems())])
     


    
def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" name="IN6" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="%s">""" % strftime("%Y-%m-%d %H:%M:%S", gmtime())
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

    <!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>

    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="-0.6" name="monitor1"/>
      </component>
      <component type="monitor">
        <location z="-0.5" name="monitor2"/>
      </component>
      <component type="monitor">
        <location z="-0.4" name="monitor3"/>
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
    </idlist>""" % (firstDetectorId, numberOfDetectors+firstDetectorId-1)
    
    print """<!-- Detector list def -->
    <component type="detectors" idlist="detectors">
        <location />
    </component>"""
    
    print "<!-- Detector Banks -->"
    print """<type name="detectors">"""
    bankIDs = range(firstBankId, numberOfBanks + 1)
    for i in bankIDs:
        print """<component type="bank_%d"><location/></component>""" % (i)
    print "</type>"
    
    print "<!-- Definition of every bank -->"
    
    thisId = firstDetectorId
    for bankId, theta, detsPerBank in zip(bankIDs, uniqueAngles, numberOfDetsPerBank):
        print """<type name="bank_%d">""" % (bankId)
        print """  <component type="pack">"""
        # Compute cartesian coordinates of middle bank
        middle_x = radius * math.sin(math.radians(theta))
        middle_y = 0
        middle_z = radius * math.cos(math.radians(theta))
        if detsPerBank == 1:
            print """<location x="%.3f" y="%.3f" z="%.3f" name="det%d"></location>"""  % (-middle_x, middle_y, middle_z,thisId) # to the right, so minus on x axis
            thisId += 1
        elif detsPerBank == 3:
            # Compute cartesian coordinates of upper bank
            up_z = middle_z
            up_y = radius * math.sin(math.radians(angle))
            up_x_square =  middle_x**2 - up_y**2
            up_x = math.sqrt(up_x_square)
            up_angle = - math.degrees(math.atan2(up_y, up_x))
            detector_angle = - theta
            # Three step rotation, also using <facing> feature  
            print """<location x="%.3f" y="%.3f" z="%.3f" rot="%.3f" axis-x="0.0" axis-y="1.0" axis-z="0.0" name="det%d" >"""  % (-up_x, up_y, up_z, detector_angle,thisId) # to the right, so minus on x axis
            print """<facing x="0" y="0" z="0"/>"""
            print """<rot val="%.3f" axis-x="%.3f" axis-y="%.3f" axis-z="%.3f" /> """ % (up_angle, -up_x, up_y, up_z)
            print """</location>"""
            thisId += 1

            print """<location x="%.3f" y="%.3f" z="%.3f" rot="%.3f" axis-x="0.0" axis-y="1.0" axis-z="0.0" name="det%d" />"""  % (-middle_x, middle_y, middle_z, detector_angle, thisId)
            thisId += 1
            
            # lower bank is symetrical
            print """<location x="%.3f" y="%.3f" z="%.3f" rot="%.3f" axis-x="0.0" axis-y="1.0" axis-z="0.0" name="det%d" >"""  % (-up_x, -up_y, up_z, detector_angle, thisId)
            print """<facing x="0" y="0" z="0"/>"""
            print """<rot val="%.3f" axis-x="%.3f" axis-y="%.3f" axis-z="%.3f" /> """ % (-up_angle, -up_x, -up_y, up_z)
            print """</location>"""
            thisId += 1

        else :
            sys.stderr.write("Number of detectors per bank is invalid: " + str(detsPerBank))
        print """  </component>"""
        print """</type>"""

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
        <id start="0" end="2" />
    </idlist>
    """ 
 
#def sphericalToCartesian(rho, theta, phi):
#    """ theta,phi : angles in degrees """
#    thetaRadians = theta * np.pi / 180
#    angleRadians = phi * np.pi / 180
#    radius = rho
#    x = radius * np.sin(thetaRadians) * np.cos(angleRadians)
#    y = radius * np.sin(thetaRadians) * np.sin(angleRadians)
#    z = radius * np.cos(thetaRadians)
#    return x, y, z

def printPixels():  
    print """ <type name="pack" is="detector">  
    <cuboid id="pack-pixel-shape">
        <left-front-bottom-point x="0.01" y="-0.2" z="0.0" />
        <left-front-top-point x="0.01" y="-0.2" z="0.01" />
        <left-back-bottom-point x="-0.01" y="-0.2" z="0.0" />
        <right-front-bottom-point x="0.01" y="0.2" z="0.0" />
    </cuboid>
    <algebra val="pack-pixel-shape" />     
    </type>"""
 

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader()
    printDetectors()
    printMonitors()
    printPixels()
    printEnd()
    
    
     
