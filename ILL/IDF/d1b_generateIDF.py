'''
Created on 20/01/2017

@author: vardanyan@ill.fr

Run as:

cd mantidgeometry/ILL/IDF; python d1b_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > D1B_Definition.xml

'''

import time

instrumentName = 'D1B'
nCells = 1280
radius = 1.500
cellHeight = 0.1
cellWidth = 0.0026
cellDepth = 0.001
starting2Theta = 0.85
cell2Theta = 0.1
L1 = 2.986
monitorZ = 0.476
monitorSize = 0.01


def printHeader():

    print """<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an
    Instrument Definition File see http://www.mantidproject.org/IDF
    -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0
    Schema/IDFSchema.xsd"
    name="{0}" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="{1}">"""\
        .format(instrumentName,
                time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

    print """<!-- Author: vardanyan@ill.fr -->"""

    print """<defaults>
      <length unit="meter" />
      <angle unit="degree" />
      <reference-frame>
        <!-- The z-axis is set parallel to and in the direction of the beam.
        the y-axis points up and the coordinate system is right handed. -->
        <along-beam axis="z" />
        <pointing-up axis="y" />
        <handedness val="right" />
      </reference-frame>
    </defaults>
    """

    print """<!-- Source position -->
    <component type="monochromator">
        <location z="-{0}" />
    </component>

    <type name="monochromator" is="Source">
      <properties />
    </type>""".format(L1)

    print """<!-- Monitor position -->
    <component type="monitor" idlist="monitors">
        <location z="-{0}" name="monitor" />
    </component>

    <type name="monitor" is="monitor">
      <cuboid id="shape">
        <left-front-bottom-point  x="-{1}"  y="-{1}" z="-{1}"   />
        <left-front-top-point     x="-{1}"  y="{1}" z="-{1}" />
        <left-back-bottom-point   x="-{1}" y="-{1}" z="{1}"   />
        <right-front-bottom-point x="{1}"  y="-{1}"  z="-{1}"   />
      </cuboid>
      <algebra val="shape" />
    </type>

    <idlist idname="monitors">
        <id val="1" />
    </idlist>

    """.format(monitorZ, monitorSize/2.)

    print """<!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>
    <type name="sample-position" is="SamplePos" />
    """


def printDetector():
    print """<!-- Detector IDs -->
    <idlist idname="detectors">
        <id start="2" end="{0}" />
    </idlist>
    <!-- Detector list def -->
    <component type="detector" idlist="detectors">
        <location name="detector"/>
    </component>
    <!-- Detector Cells -->
    <type name="detector">
      <component type="cell">""".format(nCells + 1)

    for cell in range(nCells):
        print """       <location name="cell_{0}" r="{1}" t="-{2}" p="0.0">
                    <facing r="0.0" t="0.0" p="0.0"/>
                </location>
        """.format(cell + 1, radius, starting2Theta + cell * cell2Theta)

    print """   </component>
    </type>
    """


def printCellType():
    print """<!-- Standard Cell -->
    <type is="detector" name="cell">
        <cuboid id="cell-shape">"""
    print """   <left-front-bottom-point x="{0}" y="{1}" z="{2}"/>"""\
        .format(-cellWidth/2., -cellHeight/2., 0)

    print """   <left-front-top-point x="{0}" y="{1}" z="{2}"/>"""\
        .format(-cellWidth/2., cellHeight/2., 0)

    print """   <left-back-bottom-point x="{0}" y="{1}" z="{2}"/>"""\
        .format(-cellWidth/2., -cellHeight/2., cellDepth)

    print """   <right-front-bottom-point x="{0}" y="{1}" z="{2}"/>"""\
        .format(cellWidth/2., -cellHeight/2., 0)
    print """   </cuboid>
      <algebra val="cell-shape"/>
    </type>
    """


def printEnd():
    print "</instrument>"


if __name__ == '__main__':
    printHeader()
    printDetector()
    printCellType()
    printEnd()