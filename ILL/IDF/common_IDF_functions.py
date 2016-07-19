from __future__ import print_function
from time import gmtime, strftime
import math
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


def write_header(f, instrument_name, authors):
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" name="{0}" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="{1}">""".format(instrument_name, strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    f.write("""<!-- Author: {0} -->""".format(authors))
    f.write("""<defaults>
      <length unit="meter" />
      <angle unit="degree" />
      <reference-frame>
        <!-- The z-axis is set parallel to and in the direction of the beam. the 
             y-axis points up and the coordinate system is right handed. -->
        <along-beam axis="z" />
        <pointing-up axis="y" />
        <handedness val="right" />
      </reference-frame>
    </defaults>)""")


def write_moderator(f):
    f.write("""<component type="moderator">
      <location z="-2" />
    </component>
    <type name="moderator" is="Source"></type>""")


def write_sample_position(f):
    f.write("""<!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>

    <type name="sample-position" is="SamplePos" />""")


def box_coordinates(radius, theta, phi, orientation):
    """Computes cartesian coordinates for a detector box.
    """
    x = orientation * radius * math.sqrt(numpy.sin(theta)**2 - math.sin(phi)**2)
    y = radius * math.sin(phi)
    z = radius * math.cos(theta)
    return (x, y, z)


def tilting_angle(theta, phi, orientation):
    theta = math.radians(theta)
    phi = math.radians(phi)
    return 90 - orientation * (math.degrees(math.acos(math.cos(theta) / math.sin(theta) * math.sin(phi) / math.cos(phi))))


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
    f.write("</instrument>")
    
def clean_up_xml(output_filename):
    # Requires tidy, available on Ubuntu 14.04
    temp_filename = output_filename + '_temp'
    copyfile(output_filename, temp_filename)
    os.remove(output_filename)
    os.system('tidy -utf8 -xml -w 255 -i -c -q -asxml {0} > {1}'.format(temp_filename, output_filename))
    os.remove(temp_filename)
