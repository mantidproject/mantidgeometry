'''
Created on 21/06/2017

@author: bush@ill.fr

Run as:

cd mantidgeometry/ILL/IDF; python d2b_generateIDF.py | tidy -utf8 -xml -w 255 -i -c -q -asxml > D2B_Definition.xml

'''

import math
import time

instrumentName = 'D2B'
distance_to_detector = 1.296

monochromator_distance = 2.997
monitor_distance = 1.594
monitor_size = 0.01

number_of_tubes = 128
"""These angles are arbitary, the correct start value is always read from the NeXus file."""
tube_theta_angles_start = 165.0
tube_theta_angles_end = 6.25

number_of_pixels = 128
detector_tube_length = 0.3545
pixel_height = detector_tube_length / number_of_pixels
"""This is the effective radius of a detector tube. The actual dimater of the tubes are
   2.54 mm (1 inch), but the collimators mean they only see 0.05 degrees in sold angle,
   not the 1.25 degrees that would be expected."""
pixel_radius = distance_to_detector * math.sin(math.radians(0.05)) * 0.5


def tube_theta_angles():
    """Returns a list of theta angles, corresponding to the azimuthal angle in Mantid's spherical-polar coordinate system"""
    tube_theta_angles = []
    tube_theta_delta = (tube_theta_angles_start - tube_theta_angles_end) / (number_of_tubes - 1)

    for tube_number in range(number_of_tubes):
        tube_theta_angles.append(tube_theta_angles_start - tube_theta_delta * tube_number)

    return tube_theta_angles


def pixel_height_positions():
    """Returns a list of the position of a pixel, in terms of height, within a tube"""
    pixel_height_positions = []
    pixel_heigh_delta = detector_tube_length / number_of_tubes

    for pixel_number in range(number_of_pixels):
        pixel_height_positions.append(-detector_tube_length * 0.5 + pixel_height * 0.5 + pixel_height * pixel_number)

    return pixel_height_positions


def printHeader():
    print("""<?xml version="1.0" encoding="UTF-8"?>
             <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
             <instrument xmlns="http://www.mantidproject.org/IDF/1.0"
                         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd"
                         name="{0}"
                         valid-from="1900-01-31 23:59:59"
                         valid-to="2100-01-31 23:59:59" last-modified="{1}">"""\
        .format(instrumentName, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))

    print("""<!-- Author: bush@ill.fr -->""")

    print("""<defaults>
               <length unit="meter" />
               <angle unit="degree" />
               <reference-frame>
                 <!-- The z-axis is set parallel to and in the direction of the beam. The y-axis points up and the coordinate system is right handed. -->
                 <along-beam axis="z" />
                 <pointing-up axis="y" />
                 <handedness val="right" />
              </reference-frame>
            </defaults>""")


def printMonochromator():
    print("""<!-- Source position -->
             <component type="monochromator">
               <location z="-{0}" />
             </component>

           <type name="monochromator" is="Source"/>""".format(monochromator_distance))


def printMonitor():
    print("""<!-- Monitor position -->
             <component type="monitor" idlist="monitors">
               <location z="-{0}" name="monitor" />
             </component>

             <type name="monitor" is="monitor">
               <cuboid id="shape">
                 <left-front-bottom-point  x="-{1}" y="-{1}" z="-{1}"   />
                 <left-front-top-point     x="-{1}" y="{1}" z="-{1}" />
                 <left-back-bottom-point   x="-{1}" y="-{1}" z="{1}"   />
                 <right-front-bottom-point x="{1}" y="-{1}" z="-{1}"   />
               </cuboid>
               <algebra val="shape" />
             </type>

             <idlist idname="monitors">
               <id val="0" />
             </idlist>""".format(monitor_distance, monitor_size * 0.5))


def printSample():
    print("""<!-- Sample position -->
             <component type="sample-position">
               <location x="0.0" y="0.0" z="0.0" />
             </component>
             <type name="sample-position" is="SamplePos" />""")


def printDetectorInformation():
    print("""<!-- Detector IDs -->
             <idlist idname="detectors">
               <id start="1" end="{0}" />
             </idlist>
             <!-- Detector list def -->
             <component type="detectors" idlist="detectors">
               <location x="0.0" y="0.0" z="0.0" />
             </component>""".format(number_of_tubes * number_of_pixels))


def printDetectors():
    print("""<type name="detectors">
               <component type="standard_tube">""")

    tube_angles = tube_theta_angles()

    for tube_number in range(number_of_tubes):
        print """<location r="{0}" t="{1}" name="tube_{2}" />""".format(distance_to_detector, tube_angles[tube_number], tube_number + 1)

    print("""  </component>
             </type>""")


def printTubeDefinition():
    print("""<!-- Definition of standard_tube -->
             <type name="standard_tube" outline="yes">
               <component type="standard_pixel">""")

    pixel_positions = pixel_height_positions()

    for pixel_number in range(number_of_pixels):
        print("""<location y="{0}" />""").format(pixel_positions[pixel_number])

    print("""  </component>
             </type>""")


def printPixelDefinition():
    print("""<type name="standard_pixel" is="detector">
             <cylinder id="shape">
               <centre-of-bottom-base x="0.0" y="{0}" z="0.0" />
               <axis x="0.0" y="1.0" z="0.0" />
               <radius val="{1}" />
               <height val="{2}" />
             </cylinder>
             <algebra val="shape" />
           </type>""".format(-pixel_height * 0.5, pixel_radius, pixel_height))


def printEnd():
    print "</instrument>"


if __name__ == '__main__':
    printHeader()
    printMonochromator()
    printMonitor()
    printSample()
    printDetectorInformation()
    printDetectors()
    printTubeDefinition()
    printPixelDefinition()
    printEnd()
