'''
Created on Feb 22, 2013

@author: leal

Run as:

cd  ~/git/mantidgeometry/LLB; python mibemol_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > ~/git/Mantid/Code/Mantid/instrument/MIBEMOL_Definition.xml; rm  ~/git/Mantid/Code/Mantid/instrument/MIBEMOL_Definition.vtp 

'''

import sys
import numpy as np
from collections import Counter
from time import gmtime, strftime
import math 

bankTheta = [0.0,23.5,24.8,26.1,27.5,36.499,37.594,38.692,40.162,41.269,42.38,43.868,44.989,46.114,47.623,48.759,52.202,53.36,54.525,56.087,57.266,58.452,60.044,61.246,62.456,63.674,64.899,67.792,69.047,69.889,71.586,72.442,73.884,75.473,76.35,77.677,79.015,79.915,84.04,85.445,86.39,87.822,89.272,90.248,91.729,92.727,94.241,95.263,96.814,98.921,99.991,101.62,102.721,103.836,104.965,106.109,107.853,108.443,110.237,110.845,112.695,115.235,116.538,117.866,119.22,120.602,121.304,122.732,124.193,125.69,126.453,128.009,131.262,132.107,132.967,134.732,135.639,136.565,138.475,139.462,141.484,141.509,143.666,147.157]
bankTheta.reverse()

bankLength = len(bankTheta)
numberOfDetectors =  bankLength

firstDetectorId = 1

sampleDetectorDistance = 3.58  # meters
sourceSampleDistance = 0.49

    
def printHeader():
    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument name="MIBEMOL" valid-from="1900-01-31 23:59:59"
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
    print """  <component type="bank"><location/></component>"""
    print "</type>"
    
    print "<!-- Definition of every bank -->"
    
    thisId = firstDetectorId
    
    print """<type name="bank">"""
    print """  <component type="pack">"""
    for theta in bankTheta:
        print """    <location r="%f" t="%f" p="%f" name="det%d"></location>"""  % (sampleDetectorDistance,theta,0,thisId) #
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
    
    
     
