from __future__ import print_function
from time import gmtime, strftime
import math
import numpy
from scipy.constants import degree
from shutil import copyfile
import os

"""This Python script contains a number of utility functions for
   creating IDF files for the ILL.
"""

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
        next(detector_box_list) # Skip header line

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


def write_header(f, instrument_name, authors, valid_from = '1900-01-31 23:59:59', valid_to = '2100-01-31 23:59:59'):
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->\n')
    f.write('<!-- This file is automatically generated by one of the scripts found in https://github.com/mantidproject/mantidgeometry/tree/master/ILL/IDF -->\n')
    f.write('<instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    f.write('xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" name="{0}"\n'.format(instrument_name))
    f.write('valid-from="{}" valid-to="{}" last-modified="{}">\n'.format(valid_from, valid_to, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    f.write('<!-- Authors: {} -->\n'.format(authors))
    f.write('  <defaults>\n')
    f.write('    <length unit="meter" />\n')
    f.write('    <angle unit="degree" />\n')
    f.write('    <reference-frame>\n')
    f.write('      <!-- The z-axis is set parallel to and in the direction of the beam. the\n')
    f.write('       y-axis points up and the coordinate system is right handed. -->\n')
    f.write('      <along-beam axis="z" />\n')
    f.write('      <pointing-up axis="y" />\n')
    f.write('      <handedness val="right" />\n')
    f.write('    </reference-frame>\n')
    f.write('  </defaults>\n')


def write_moderator(f):
    f.write('  <component type="moderator">\n')
    f.write('    <location z="-2.0" />\n')
    f.write('  </component>\n')
    f.write('  <type name="moderator" is="Source" />\n')


def write_sample_position(f):
    f.write('  <component type="sample_position">\n')
    f.write('    <location y="0.0" x="0.0" z="0.0" />\n')
    f.write('  </component>\n')
    f.write('  <type name="sample_position" is="SamplePos" />\n')


def box_coordinates(radius, theta, phi, orientation):
    """Computes cartesian coordinates for a detector box.
    """
    theta = theta * degree
    phi = phi * degree
    x = orientation * radius * numpy.sqrt(numpy.sin(theta)**2 - numpy.sin(phi)**2)
    y = radius * numpy.sin(phi)
    z = radius * numpy.cos(theta)
    return (x, y, z)


def tilting_angle(theta, phi, orientation):
    theta = theta * degree
    phi = phi * degree
    rotation_angle = orientation * (90 - ((numpy.arccos(numpy.cos(theta) / numpy.sin(theta) * numpy.sin(phi) / numpy.cos(phi)))) / degree)
    return rotation_angle


def write_detectors(f, detector_box_list, radius, detector_gap, orientation):
    """Generates a set of detectors in boxs, according to the contents of detector_box_list.
    
       detector_box_list: A list of tuples containing box_number, theta angle, a list of detector ids, phi angle
       radius: Sample to detector distance
       detector_gap: Gap between detectors in a box
       orientation: +1 indicates anti-clockwise from the z-axis, -1 clockwise    
    """
    
    first_box_id = detector_box_list[0][0]
    number_of_boxs = detector_box_list[-1][0]
    
    first_detector_id = detector_box_list[0][2]
    
    f.write("<!-- Detector boxs -->")
    
    for box_number, theta, detector_ids, phi in detector_box_list:
		        
        (x, y, z) = box_coordinates(radius, theta, phi, orientation)

        print(box_number, detector_ids, 'x=', x, 'y=', y, 'z=', z, )
        print(box_number, 'r=', radius, 'theta=', theta, 'phi', phi)
        
        if len(detector_ids) == 3:	
            f.write("""<component type="box_3_dets" name="box_{0}" idlist="det_id_list_{0}">
                         <location x="{1}" y="{2}" z="{3}">
							<rot val="{4}" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="{5}" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="{6}" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>                         
                         </location/>
                       </component>""".format(box_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi, orientation)))

            f.write("""<idlist idname="det_id_list_{0}">
                         <id val="{1}" />
                         <id val="{2}" />
                         <id val="{3}" />
                       </idlist>""".format(box_number, detector_ids[0], detector_ids[1], detector_ids[2]))
        elif len(detector_ids) == 4:
            f.write("""<component type="box_4_dets" name="box_{0}" idlist="det_id_list_{0}">
                         <location x="{1}" y="{2}" z="{3}"> 
							<rot val="{4}" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="{5}" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="{6}" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>
						 </location>
                       </component>""".format(box_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi, orientation)))
            f.write("""<idlist idname="det_id_list_{0}">
                         <id val="{1}" />
                         <id val="{2}" />
                         <id val="{3}" />
                         <id val="{4}" />                         
                       </idlist>""".format(box_number, detector_ids[0], detector_ids[1], detector_ids[2], detector_ids[3]))                       
        else:
            raise(ValueError('Unexpected number of dectors in box'))
            
    f.write("""<type name="box_3_dets">
                 <component type = "tube">
                   <location x="{0}" y="0.0" z="0.0" name="tube_1" />
                   <location x="{1}" y="0.0" z="0.0" name="tube_2" />
                   <location x="{2}" y="0.0" z="0.0" name="tube_3" />
                 </component>                          
               </type>""".format(orientation * detector_gap * -1.0, orientation * detector_gap * 0.0, orientation * detector_gap * 1.0))
               
    f.write("""<type name="box_4_dets">
                 <component type = "tube">
                   <location x="{0}" y="0.0" z="0.0" name="tube_1" />
                   <location x="{1}" y="0.0" z="0.0" name="tube_2" />
                   <location x="{2}" y="0.0" z="0.0" name="tube_3" />
                   <location x="{3}" y="0.0" z="0.0" name="tube_4" />
                 </component>                 
               </type>""".format(orientation * detector_gap * -1.5, orientation * detector_gap * -0.5, orientation * detector_gap * 0.5, orientation * detector_gap * 1.5))


def write_end(f):
    f.write("</instrument>\n")
    
def clean_up_xml(output_filename):
    # Requires tidy, available on Ubuntu 14.04
    temp_filename = output_filename + '_temp'
    copyfile(output_filename, temp_filename)
    os.remove(output_filename)
    os.system('tidy -utf8 -xml -w 255 -i -c -q -asxml {0} > {1}'.format(temp_filename, output_filename))
    os.remove(temp_filename)
