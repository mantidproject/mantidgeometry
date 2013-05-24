'''
Created on Feb 22, 2013

@author: leal

Run as:

cd  ~/git/mantidgeometry/SINQ/IDF; python focus_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/FOCUS_Definition.xml; rm  ~/git/Mantid/Code/Mantid/instrument/FOCUS_Definition.vtp 

'''

import sys
import numpy as np
from collections import Counter
from time import gmtime, strftime
import math 


bank1Theta = [9.64,10.42,11.22,12,12.78,13.57,14.36,9.64,10.42,11.22,17.5,18.29,19.08,19.86,20.64,21.44,22.22,23.01,23.79,24.57,25.37,26.15,26.94,27.72,28.51,29.3,30.08,30.87,31.65,32.44,33.23,34.01,34.8,35.58,36.37,37.16,37.94,38.73,39.52,40.3,41.09,41.87,42.66,43.45,44.23,45.02,45.8,46.59,47.38,48.16,48.95,49.73,50.52,51.31,52.09,52.88,53.67,54.45,55.24,56.02,56.81,57.6,58.38,59.17,59.95,60.74,61.53,62.31,63.1,63.88,64.68,65.46,66.24,67.03,67.81,71.23,72.02,72.81,73.59,74.38,75.16,75.95,76.74,77.52,78.31,79.09,79.88,80.67,81.45,82.24,83.02,83.82,84.6,85.38,86.17,86.95,87.75,88.53,89.31,90.1,90.89,91.67,92.46,93.24,94.03,94.82,95.6,96.39,97.17,97.97,98.75,99.53,100.32,101.1,101.9,102.68,103.46,104.25,105.03,105.83,106.61,107.39,108.18,108.97,109.76,110.54,111.32,112.11,112.9,113.69,114.47,115.25,116.05,116.83,117.62,118.4,119.18,119.98,120.76,121.55,122.33,123.12,123.91,124.69,125.48,126.26,127.05,127.84,128.62,129.4]
lowerBankTheta = [18.35,19.175,20,20.825,21.65,23.35,24.175,25,25.825,26.65,28.35,29.175,30,30.825,31.65,33.35,34.175,35,35.825,36.65,38.35,39.175,40,40.825,41.65,42.85,43.675,44.5,45.325,46.15,47.35,48.175,49,49.825,50.65,51.85,52.675,53.5,54.325,55.15,56.35,57.175,58,58.825,59.65,60.85,61.675,62.5,63.325,64.15,70.35,71.175,72,72.825,73.65,74.85,75.675,76.5,77.325,78.15,79.35,80.175,81,81.825,82.65,83.85,84.675,85.5,86.325,87.15,88.35,89.175,90,90.825,91.65,92.85,93.675,94.5,95.325,96.15,97.35,98.175,99,99.825,100.65,101.85,102.675,103.5,104.325,105.15,106.35,107.175,108,108.825,109.65,110.85,111.675,112.5,113.325,114.15,115.35,116.175,117,117.825,118.65,119.85,120.675,121.5,122.325,123.15,124.35,125.175,126,126.825,127.65]
upperBankTheta = [18.35,19.175,20,20.825,21.65,23.35,24.175,25,25.825,26.65,28.35,29.175,30,30.825,31.65,33.35,34.175,35,35.825,36.65,38.35,39.175,40,40.825,41.65,42.85,43.675,44.5,45.325,46.15,47.35,48.175,49,49.825,50.65,51.85,52.675,53.5,54.325,55.15,56.35,57.175,58,58.825,59.65,60.85,61.675,62.5,63.325,64.15,65.35,66.175,67,67.825,68.65,79.35,80.175,81,81.825,82.65,83.85,84.675,85.5,86.325,87.15,88.35,89.175,90,90.825,91.65,92.85,93.675,94.5,95.325,96.15,97.35,98.175,99,99.825,100.65,101.85,102.675,103.5,104.325,105.15,106.35,107.175,108,108.825,109.65,110.85,111.675,112.5,113.325,114.15,115.35,116.175,117,117.825,118.65,119.85,120.675,121.5,122.325,123.15,124.35,125.175,126,126.825,127.65]

bank1Length = len(bank1Theta)
lowerBankLength = len(lowerBankTheta)
upperBankLength = len(upperBankTheta)
numberOfDetectors =  bank1Length + lowerBankLength + upperBankLength

firstDetectorId = 1

sampleDetectorDistance = 2.5  # meters
angle = 15  # degrees # vertical detection angle
sourceSampleDistance = 0.49
    
def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument name="FOCUS" valid-from="1900-01-31 23:59:59"
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
    </defaults>"""

    print """<component type="moderator">
      <location z="-%f" />
    </component>
    <type name="moderator" is="Source"></type>"""% sourceSampleDistance

    print """<!-- Sample position -->
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
    print """  <component type="bank1"><location/></component>"""
    print """  <component type="lowerBank"><location/></component>"""
    print """  <component type="upperBank"><location/></component>"""
    print "</type>"
    
    print "<!-- Definition of every bank -->"
    
    thisId = firstDetectorId
    
    print """<type name="bank1">"""
    print """  <component type="pack">"""
    for theta in bank1Theta:
        print """    <location r="%f" t="%f" p="%f" name="det%d"></location>"""  % (sampleDetectorDistance,-theta,0,thisId) #
        thisId += 1
    print """  </component>"""
    print """</type>"""
    
    print """<type name="lowerBank">"""
    print """  <component type="pack">"""
    for theta in lowerBankTheta:
        thetaRadians = -theta * np.pi / 180 - np.pi;
        angleRadians = -angle * np.pi / 180 - np.pi/2;
        z = sampleDetectorDistance * np.sin(angleRadians) * np.cos(thetaRadians)
        x = sampleDetectorDistance * np.sin(angleRadians) * np.sin(thetaRadians)
        y = sampleDetectorDistance * np.cos(angleRadians)
        print """<location x="%f" y="%f" z="%f" name="det%d"></location>"""  % (x,y,z,thisId) #
        thisId += 1
    print """  </component>"""
    print """</type>"""
    

    
    
    
    print """<type name="upperBank">"""
    print """  <component type="pack">"""
    for theta in upperBankTheta:
        thetaRadians = -theta * np.pi / 180 - np.pi;
        angleRadians = -angle * np.pi / 180 - np.pi/2;
        z = sampleDetectorDistance * np.sin(angleRadians) * np.cos(thetaRadians)
        x = sampleDetectorDistance * np.sin(angleRadians) * np.sin(thetaRadians)
        y = sampleDetectorDistance * np.cos(angleRadians)
        print """<location x="%f" y="%f" z="%f" name="det%d"></location>"""  % (x,-y,z,thisId) #
        thisId += 1
    print """  </component>"""
    print """</type>"""


 
#def sphericalToCartesian(rho, theta, phi):
#    """ theta,phi : angles in degrees """
#    thetaRadians = theta * np.pi / 180
#    angleRadians = phi * np.pi / 180
#    sampleDetectorDistance = rho
#    x = sampleDetectorDistance * np.sin(thetaRadians) * np.cos(angleRadians)
#    y = sampleDetectorDistance * np.sin(thetaRadians) * np.sin(angleRadians)
#    z = sampleDetectorDistance * np.cos(thetaRadians)
#    return x, y, z

def printPixels():  
    '''
    http://sinq.web.psi.ch/sinq/instr/detectors.html
    active length     :    40cm    
    cross-section     :    rectangular (3cm width x 1cm depth)    
    '''
    print """ <type name="pack" is="detector">  
    <cuboid id="pack-pixel-shape">
      <left-front-bottom-point  z="-0.005" y="-0.2" x="-0.01"  />
      <left-front-top-point     z="-0.005" y="0.2"  x="-0.01"  />
      <left-back-bottom-point   z="-0.005" y="-0.2" x="0.01"  />
      <right-front-bottom-point z="0.005"  y="-0.2" x="-0.01"  />
    </cuboid>
    <algebra val="pack-pixel-shape" />     
    </type>"""
        

def printEnd():
    print "</instrument>"

    

if __name__ == '__main__':
    printHeader();
    printDetectors();
    printPixels();
    printEnd();
    
    
     
