'''
Created on Feb 22, 2013

@author: leal

Run as:

python ~/workspace/PyTests/src/in4_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/IN4_Definition.xml 

IN4
300 simple  dets 
96 in the rosace

'''
import sys
import numpy as np
from collections import Counter
from time import gmtime, strftime
# last 96 angles are the opening of the beam (rho)
azimuthalAngle = [-15.925, -14.975, -14.025, -13.075, 13.075, 14.025, 14.975, 15.925, 19.075, 20.025, 20.975, 21.925, 24.975, 25.925, 26.875, 27.825, 28.775, 29.725, 30.675, 31.625, 34.575, 35.525, 36.475, 37.425, 38.375, 39.325, 40.275, 41.225, 44.075, 45.025, 45.975, 46.925, 47.875, 48.825, 49.775, 50.725, 50.675, 52.625, 53.775, 54.525, 57.275, 58.225, 59.175, 60.125, 61.075, 62.025, 62.975, 63.925, 64.875, 65.825, 66.775, 67.725, 70.475, 71.425, 72.375, 73.325, 74.275, 75.225, 76.175, 77.125, 78.075, 79.025, 79.975, 80.925, 83.575, 84.525, 85.475, 86.425, 87.375, 88.325, 89.275, 90.225, 91.175, 92.125, 93.075, 94.025, 96.675, 97.625, 98.575, 99.525, 100.475, 101.425, 102.375, 103.325, 104.275, 105.225, 106.175, 107.125, 109.875, 110.825, 111.775, 112.725, 113.675, 114.625, 115.575, 116.525, 117.475, 118.425, 119.375, 120.325, 13.275, 14.225, 15.175, 16.125, 17.075, 18.025, 18.975, 19.925, 20.875, 21.825, 22.775, 23.725, 26.275, 27.225, 28.175, 29.125, 30.075, 31.025, 31.975, 32.925, 33.875, 34.825, 35.775, 36.725, 39.275, 40.275, 41.175, 42.125, 43.075, 44.025, 44.975, 45.925, 46.875, 47.825, 48.775, 49.725, 52.275, 53.225, 54.175, 55.125, 56.075, 57.025, 57.975, 58.925, 59.875, 60.825, 61.775, 62.725, 64.325, 65.275, 66.225, 67.175, 68.125, 69.075, 70.025, 70.975, 71.925, 72.875, 73.825, 74.775, 78.275, 79.225, 80.175, 81.125, 82.075, 83.025, 83.975, 84.925, 85.875, 86.825, 87.775, 88.725, 91.275, 92.225, 93.175, 94.125, 95.075, 96.025, 96.975, 97.925, 98.875, 99.825, 100.775, 101.725, 104.275, 105.225, 106.175, 107.125, 108.075, 109.025, 109.975, 110.925, 111.875, 112.825, 113.775, 114.725, 117.275, 118.225, 119.175, 120.125, -15.925, -14.975, -14.025, -13.075, 13.075, 14.025, 14.975, 15.925, 19.075, 20.025, 20.975, 21.925, 24.975, 25.925, 26.875, 27.825, 28.775, 29.725, 30.675, 31.625, 34.575, 35.525, 36.475, 37.425, 38.375, 39.325, 40.275, 41.225, 44.075, 45.025, 45.975, 46.925, 47.875, 48.825, 49.775, 50.725, 50.675, 52.625, 53.775, 54.525, 57.275, 58.225, 59.175, 60.125, 61.075, 62.025, 62.975, 63.925, 64.875, 65.825, 66.775, 67.725, 70.475, 71.425, 72.375, 73.325, 74.275, 75.225, 76.175, 77.125, 78.075, 79.025, 79.975, 80.925, 83.575, 84.525, 85.475, 86.425, 87.375, 88.325, 89.275, 90.225, 91.175, 92.125, 93.075, 94.025, 96.675, 97.625, 98.575, 99.525, 100.475, 101.425, 102.375, 103.325, 104.275, 105.225, 106.175, 107.125, 109.875, 110.825, 111.775, 112.725, 113.675, 114.625, 115.575, 116.525, 117.475, 118.425, 119.375, 120.325, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738, 2.435, 3.008, 3.581, 4.154, 4.727, 5.300, 5.873, 6.446, 7.019, 7.592, 8.165, 8.738]
# 398  ( SmalANGLE-Roscace=4  Bot=1 Medium=2 Top=3 Moni=0 )
detectorLocation = [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4]
# Roscace apperar to have 8 detectors (pie) of 12 tubes each.

numberOfSimpleDetectors=300
simpleDetAngle=azimuthalAngle[0:numberOfSimpleDetectors]
simpleDetLocation=detectorLocation[0:numberOfSimpleDetectors] #len=300

rosaceDetAngle=azimuthalAngle[numberOfSimpleDetectors:]
rosaceDetLocation=detectorLocation[numberOfSimpleDetectors:] #len=96
numberOfSlicesInRosace=8

# # Global variables
numberOfDetectors = len(azimuthalAngle)
numberOfSimpleDets = len(simpleDetAngle)
firstDetectorId = 1
radius = 2.0  # meters
angle = 16  # degrees # vertical detection angle
# Don't touch!
uniqueDic = Counter(azimuthalAngle)
numberOfBanks = len(uniqueDic)
uniqueAngles = np.array([k for k, v in sorted(uniqueDic.iteritems())])
numberOfDetsPerBank = np.array([v for k, v in sorted(uniqueDic.iteritems())])
# Reverse sorted numpy arrays
uniqueAngles = uniqueAngles[ ::-1 ]
numberOfDetsPerBank = numberOfDetsPerBank[ ::-1 ] 



def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument name="IN4" valid-from="1900-01-31 23:59:59"
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
    print """ <component type="simple_detectors"><location/></component>"""
    print """ <component type="rosace"><location/></component>"""
    print """</type>"""
    
    print "<!-- Definition of every bank -->"
    
    print """<type name="simple_detectors">"""
    print """  <component type="pack">"""
    # let's iterate over the simple detectors
    detId = firstDetectorId
    for theta,loc in zip(simpleDetAngle,simpleDetLocation):
        #  Bot=1 Medium=2 Top=3
        if loc == 1:
            p = -angle
        elif  loc == 2:
            p = 0
        elif loc == 3 :
            p = angle
        else:
            sys.stderr.write("Invalid Loc: " + str(loc)) 
            sys.exit(0)
        #print """<location r="%f" t="%f" p="%f" name="det%d"></location>"""  % (radius,theta,p,detId)
        thetaRadians = theta * np.pi / 180 - np.pi;
        angleRadians = p * np.pi / 180 - np.pi / 2;
        z = radius * np.sin(angleRadians) * np.cos(thetaRadians)
        x = radius * np.sin(angleRadians) * np.sin(thetaRadians)
        y = radius * np.cos(angleRadians)
        print """<location x="%f" y="%f" z="%f" name="det%d"></location>""" % (x, y, z, detId)  #
        detId+=1
    print """  </component>"""
    print """</type>"""
    
    
    print """<type name="rosace">"""
    print """  <component type="point">"""
    # let's iterate for roseta
    rotationAngles = sorted(range(0,360,45)*12)
    for p,rot in zip(rosaceDetAngle,rotationAngles):
        #  
        #print """<location r="%f" t="0" p="%f" rot="%f" axis-x="0" axis-y="0" axis-z="1" name="det%d"></location>"""  % (radius,p,rot,detId)
        print """<location r="%f" t="%f" p="%f" name="det%d"></location>""" % (radius, p, rot, detId)  #
        
        detId+=1
    print """  </component>"""
    print """</type>"""
    

    

 

def printPixels():  

    print """ <type name="pack" is="detector">  
    <cuboid id="pack-pixel-shape">
      <left-front-bottom-point  z="-0.005" y="-0.2" x="-0.01"  />
      <left-front-top-point     z="-0.005" y="0.2"  x="-0.01"  />
      <left-back-bottom-point   z="-0.005" y="-0.2" x="0.01"  />
      <right-front-bottom-point z="0.005"  y="-0.2" x="-0.01"  />
    </cuboid>
    <algebra val="pack-pixel-shape" />     
    </type>"""
    
    print """ <type name="point" is="detector">  
    <cuboid id="point-pixel-shape">
      <left-front-bottom-point  z="-0.005" y="-0.005" x="-0.005"  />
      <left-front-top-point     z="-0.005" y="0.005"  x="-0.005"  />
      <left-back-bottom-point   z="-0.005" y="-0.005" x="0.005"  />
      <right-front-bottom-point z="0.005"  y="-0.005" x="-0.005"  />
    </cuboid>
    <algebra val="point-pixel-shape" />     
    </type>"""
        

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printDetectors();
    printPixels();
    printEnd();
    
    
     
