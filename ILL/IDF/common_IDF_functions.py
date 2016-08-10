"""This Python script contains a number of utility functions for
   creating IDF files for the ILL.
"""

from __future__ import print_function
from time import gmtime, strftime
import math
import numpy
from scipy.constants import degree
from shutil import copyfile
import os


def read_detector_box_list(filename):
    """Reads a text file containing rows with box Number, Theta, Detector IDs and Phi angle. The first
       line is ignored (column headings).

       returns: A list of tuples containing box_number, theta angle, a list of detector ids, phi angle
    """

    box_number = []
    theta = []
    detector_ids = []
    phi = []

    with open(filename) as detector_box_list:
        next(detector_box_list)  # Skip header line

        for line in detector_box_list:
            line_entries = line.split()

            box_number.append(int(line_entries[0]))
            theta.append(float(line_entries[1]))

            detector_id_line = []
            for value in line_entries[2].split(','):
                try:
                    detector_id_line.append(int(value))
                except:
                    pass
            detector_ids.append(detector_id_line)
            phi.append(float(line_entries[3]))

    return zip(box_number, theta, detector_ids, phi)


def write_header(output_file, instrument_name, authors, valid_from='1900-01-31 23:59:59'):
    output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output_file.write(
        '<!-- For help on the notation used to specify an Instrument Definition File see '
        'http://www.mantidproject.org/IDF -->\n')
    output_file.write('<!-- This file is automatically generated by one of the scripts found in '
                      'https://github.com/mantidproject/mantidgeometry/tree/master/ILL/IDF -->\n')
    output_file.write('<instrument xmlns="http://www.mantidproject.org/IDF/1.0" '
                      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    output_file.write('xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" name="{0}"\n'
                      .format(instrument_name))
    output_file.write('valid-from="{}" last-modified="{}">\n'.format(valid_from, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    output_file.write('<!-- Authors: {} -->\n'.format(authors))
    output_file.write('  <defaults>\n')
    output_file.write('    <length unit="meter" />\n')
    output_file.write('    <angle unit="degree" />\n')
    output_file.write('    <reference-frame>\n')
    output_file.write('      <!-- The z-axis is set parallel to and in the direction of the beam. the\n')
    output_file.write('       y-axis points up and the coordinate system is right handed. -->\n')
    output_file.write('      <along-beam axis="z" />\n')
    output_file.write('      <pointing-up axis="y" />\n')
    output_file.write('      <handedness val="right" />\n')
    output_file.write('    </reference-frame>\n')
    output_file.write('  </defaults>\n')


def write_moderator(output_file):
    output_file.write('  <component type="moderator">\n')
    output_file.write('    <location z="-2.0" />\n')
    output_file.write('  </component>\n')
    output_file.write('  <type name="moderator" is="Source" />\n')


def write_sample_position(output_file):
    output_file.write('  <component type="sample_position">\n')
    output_file.write('    <location y="0.0" x="0.0" z="0.0" />\n')
    output_file.write('  </component>\n')
    output_file.write('  <type name="sample_position" is="SamplePos" />\n')


def box_coordinates(radius, theta, phi, orientation):
    """Computes cartesian coordinates for a detector box.
    """
    theta = theta * degree
    phi = phi * degree
    x = orientation * radius * numpy.sqrt(numpy.sin(theta) ** 2 - numpy.sin(phi) ** 2)
    y = radius * numpy.sin(phi)
    z = radius * numpy.cos(theta)
    return (x, y, z)


def tilting_angle(theta, phi, orientation):
    theta = theta * degree
    phi = phi * degree
    rotation_angle = orientation * (
    (numpy.arccos(numpy.cos(theta) / numpy.sin(theta) * numpy.sin(phi) / numpy.cos(phi)))) / degree - 90.0
    return rotation_angle


def write_detectors(output_file, detector_box_list, radius, detector_gap, orientation):
    """Generates a set of detectors in boxes, according to the contents of detector_box_list.

       detector_box_list: A list of tuples containing box_number, theta angle, a list of detector ids, phi angle
       radius: Sample to detector distance
       detector_gap: Gap between detectors in a box
       orientation: +1 indicates anti-clockwise from the z-axis, -1 clockwise
    """

    output_file.write("<!-- Detector boxes -->")

    for box_number, theta, detector_ids, phi in detector_box_list:

        (x, y, z) = box_coordinates(radius, theta, phi, orientation)

        print(box_number, detector_ids, 'x=', x, 'y=', y, 'z=', z, )
        print(box_number, 'r=', radius, 'theta=', theta, 'phi', phi)

        if len(detector_ids) == 3:
            output_file.write("""<component type="box_3_dets" name="box_{0}" idlist="det_id_list_{0}">
                         <location x="{1}" y="{2}" z="{3}">
                             <rot val="{4}" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="{5}" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="{6}" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>
                         </location/>
                       </component>""".format(box_number, x, y, z, math.degrees(math.atan2(x, z)) + 180.0, phi,
                                              tilting_angle(theta, phi, orientation) + 180.0))

            output_file.write("""<idlist idname="det_id_list_{number}">
                         <id val="{ids[0]}" />
                         <id val="{ids[1]}" />
                         <id val="{ids[2]}" />
                       </idlist>""".format(number=box_number, ids=detector_ids))
        elif len(detector_ids) == 4:
            output_file.write("""<component type="box_4_dets" name="box_{0}" idlist="det_id_list_{0}">
                         <location x="{1}" y="{2}" z="{3}"> 
							<rot val="{4}" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="{5}" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="{6}" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>
						 </location>
                       </component>""".format(box_number, x, y, z, math.degrees(math.atan2(x, z)) + 180.0, phi,
                                              tilting_angle(theta, phi, orientation) + 180.0))
            output_file.write("""<idlist idname="det_id_list_{number}">
                         <id val="{ids[0]}" />
                         <id val="{ids[1]}" />
                         <id val="{ids[2]}" />
                         <id val="{ids[3]}" />
                       </idlist>""".format(number=box_number, ids=detector_ids))
        else:
            raise ValueError('Unexpected number of dectors in box')

    output_file.write("""<type name="box_3_dets">
                 <component type = "tube">
                   <location x="{0}" y="0.0" z="0.0" name="tube_1" />
                   <location x="{1}" y="0.0" z="0.0" name="tube_2" />
                   <location x="{2}" y="0.0" z="0.0" name="tube_3" />
                 </component>                          
               </type>""".format(orientation * detector_gap * 1.0, orientation * detector_gap * 0.0,
                                 orientation * detector_gap * -1.0))

    output_file.write("""<type name="box_4_dets">
                 <component type = "tube">
                   <location x="{0}" y="0.0" z="0.0" name="tube_1" />
                   <location x="{1}" y="0.0" z="0.0" name="tube_2" />
                   <location x="{2}" y="0.0" z="0.0" name="tube_3" />
                   <location x="{3}" y="0.0" z="0.0" name="tube_4" />
                 </component>                 
               </type>""".format(orientation * detector_gap * 1.5, orientation * detector_gap * 0.5,
                                 orientation * detector_gap * -0.5, orientation * detector_gap * -1.5))


def write_end(output_file):
    output_file.write("</instrument>\n")


def clean_up_xml(output_filename):
    # Requires tidy, available on Ubuntu 14.04
    temp_filename = output_filename + '_temp'
    copyfile(output_filename, temp_filename)
    os.remove(output_filename)
    os.system('tidy -utf8 -xml -w 255 -i -c -q -asxml {0} > {1}'.format(temp_filename, output_filename))
    os.remove(temp_filename)