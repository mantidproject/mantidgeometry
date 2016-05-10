#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

GPSANS:
192 tubes

To test:
========
Load(Filename='/home/rhf/Documents/SANS/GPSANS/20160316-GPSANS/CG2_exp112_scan0001_0001.xml', OutputWorkspace='CG2_exp112_scan0001_0001')
ws = mtd['CG2_exp112_scan0001_0001']

source = ws.getInstrument().getSource()
sample = ws.getInstrument().getSample()
samplePos = sample.getPos()

# Get hold of the detector
detector = ws.getDetector(2)
# Find r, theta and phi
r = detector.getDistance(sample)
beamPos = samplePos - source.getPos()
PI = 3.1415926535
twoTheta = detector.getTwoTheta(samplePos, beamPos)*180.0/PI
print twoTheta
# Old geometry:
# 24.0664754693

i = ws.getInstrument()
det1 = i.getComponentByName("detector1")
det1.getDistance(sample)


To genereate:
=============
./generate_square_det.py > ~/git/mantid/instrument/CG2_Definition.xml


"""

from django.template import Template, Context
from django.conf import settings
from django import setup
from xml.etree import ElementTree as ET
import sys

from datetime import datetime
import numpy as np

# INIT
settings.configure()
setup()

# Values to replace in the template
values = {
    "last_modified" : str(datetime.now()),
    "monitor_1_id" : 1,
    "monitor_2_id" : 2,
    "main_detector_id_first" : 3,
    "main_detector_id_step" : 192,
}


# Template
template = """<?xml version='1.0' encoding='ASCII'?>
<instrument xmlns="http://www.mantidproject.org/IDF/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
            name="GPSANS"
            valid-from="1900-01-31 23:59:59"
            valid-to="2100-01-31 23:59:59"
		    last-modified="{{ last_modified }}">


  <defaults>
    <length unit="metre"/>
    <angle unit="degree"/>
    <reference-frame>
      <along-beam axis="z"/>
      <pointing-up axis="y"/>
      <handedness val="right"/>
    </reference-frame>
  </defaults>

  <!--SOURCE AND SAMPLE POSITION-->
  <component type="source">
    <location z="-1"/>
  </component>
  <type is="Source" name="source"/>

  <component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
  </component>
  <type is="SamplePos" name="sample-position"/>


  <!-- detector components (including monitors) -->

  <!-- ***************************************************************** -->
  <!--MONITOR 1 -->
  <component type="monitor1" idlist="monitor1">
    <location z="-0.5" />
  </component>
  <type name="monitor1" is="monitor" />
  <idlist idname="monitor1">
    <id val="1" />
  </idlist>

 <!--MONITOR 2 -->
  <component type="timer1" idlist="timer1">
    <location z="-0.5" />
  </component>
  <type name="timer1" is="monitor" />
   <idlist idname="timer1">
    <id val="2" />
  </idlist>

  <component type="sample_aperture">
    <location z="0.0"/>
    <parameter name="Size"> <value val="14.0" /> </parameter>
  </component>
  <type name="sample_aperture" />


<!-- ***************************************************************** -->
<!-- Main Detector -->
<component type="detector1" idstart="{{ main_detector_id_first }}" idfillbyfirst="x" idstep="{{main_detector_id_step}}" idstepbyrow="1">
    <location z='0' />
</component>

<!-- Detector: -->
<type name="detector1" is="rectangular_detector" type="pixel"
    xpixels="192" xstart="-0.491825" xstep="0.00515"
    ypixels="192" ystart="-0.491825" ystep="0.00515">
    <properties />
</type>

<!-- Pixel for Detector-->
<type name="pixel" is="detector">
    <cuboid id="shape">
      <left-front-bottom-point x="-0.002575" y="-0.002575" z="0.0"  />
      <left-front-top-point  x="-0.002575" y="0.002575" z="0.0"  />
      <left-back-bottom-point  x="-0.002575" y="-0.002575" z="-0.000005"  />
      <right-front-bottom-point  x="0.002575" y="-0.002575" z="0.0"  />
    </cuboid>
    <algebra val="shape" />
  </type>

</instrument>
"""

def to_string():
    """
    Render the template
    """
    t = Template(template)
    c = Context(values)
    content = t.render(c)
    return content

def is_xml_valid(xml_string):
    try:
        x = ET.fromstring(xml_string)
        return True
    except ET.ParseError as e:
        sys.stderr.write("XML not well-formed" + str(e))
        return False




if __name__ == '__main__':
    xml = to_string()
    print xml
    is_xml_valid(xml)
