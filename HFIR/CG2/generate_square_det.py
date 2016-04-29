#!/usr/bin/python
# -*- coding: utf-8 -*-


"""

CG2:
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
    "main_detector_id_step" : 256,
}


# Template
template = """<?xml version='1.0' encoding='ASCII'?>
<instrument xmlns="http://www.mantidproject.org/IDF/1.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 http://schema.mantidproject.org/IDF/1.0/IDFSchema.xsd"
            name="CG2"
            valid-from="2016-04-22 00:00:00"
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
  <component type="moderator">
    <location z="-13.601"/>
  </component>
  <type is="Source" name="moderator"/>

  <component type="sample-position">
    <location y="0.0" x="0.0" z="0.0"/>
  </component>
  <type is="SamplePos" name="sample-position"/>


  <!-- detector components (including monitors) -->

  <!-- ***************************************************************** -->
  <!--MONITOR 1 -->
  <component type="monitor1" idlist="monitor1">
    <location z="-10.5" />
  </component>
  <type name="monitor1" is="monitor" />
  <idlist idname="monitor1">
    <id val="1" />
  </idlist>

 <!--MONITOR 2 -->
  <component type="timer1" idlist="timer1">
    <location z="-10.5" />
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
    xpixels="192" xstart="-0.52525" xstep="0.00550"
    ypixels="256" ystart="-0.54825" ystep="0.00430">
    <properties />
</type>

<!-- Pixel for Detector-->
<type is="detector" name="pixel">
    <cylinder id="cyl-approx">
      <centre-of-bottom-base p="0.0" r="0.0" t="0.0"/>
      <axis y="1.0" x="0.0" z="0.0"/>
      <radius val="0.00275"/>
      <height val="0.0043"/>
    </cylinder>
    <algebra val="cyl-approx"/>
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
