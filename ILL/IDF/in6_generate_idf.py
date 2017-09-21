"""This script is used to generate the instrument definition for IN6.
   Note that this requires the output from in6_generate_detector_list.py
   as an input, to specify the detector positions and angles.
"""

from common_IDF_functions import *


def write_in6_source_chopper(output_file):
    output_file.write('  <component type="fermi_chopper">\n')
    output_file.write('    <location z="-0.395" />\n')
    output_file.write('  </component>\n')
    output_file.write('  <type name="fermi_chopper" is="Source" />\n')


def write_in6_monitor_positions(output_file):
    output_file.write("""<!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>

    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="-0.273" name="monitor1"/>
      </component>
      <component type="monitor">
        <location z="0.570" name="monitor2"/>
      </component>
      <component type="monitor">
        <location z="2.483" name="monitor3"/>
      </component>
    </type>""")


def write_in6_detector_shape(output_file):
    output_file.write("""<!-- Detector tube shape. Cuboids 32 x 16 mm, 300 mm long -->
                 <type is="detector" name="tube">
                   <cuboid id="pixel-shape">
                     <left-front-bottom-point y="-0.150" x="-0.016" z="0.0"/>
                     <left-front-top-point y="0.150" x="-0.016" z="0.0"/>
                     <left-back-bottom-point y="-0.150" x="-0.0155" z="-0.016"/>
                     <right-front-bottom-point y="-0.150" x="0.0155" z="0.0"/>
                   </cuboid>
                   <algebra val="pixel-shape"/>
                 </type>""")


def write_in6_monitor_shapes(output_file):
    output_file.write("""<!--MONITOR SHAPE-->
    <type is="monitor" name="monitor">
    <cylinder id="cyl-approx">
    <centre-of-bottom-base y="0.0" x="0.0" z="0.0"/>
    <axis y="0.0" x="0.0" z="1.0"/>
    <radius val="0.02"/>
    <height val="0.00"/>
    </cylinder>
    <algebra val="cyl-approx"/>
    </type>

    <!--MONITOR IDs-->
    <idlist idname="monitors">
        <id start="1001" end="1003" />
    </idlist>
    """)


def write_in6_detectors(output_file, detector_box_list, radius, orientation):
    """Generates a set of detectors in boxes, according to the contents of detector_box_list.

       detector_box_list: A list of tuples containing box_number, theta angle, a list of detector ids, phi angle
       radius: Sample to detector distance
       detector_gap: Gap between detectors in a box
       orientation: +1 indicates anti-clockwise from the z-axis, -1 clockwise
    """

    id_strings = []
    top_bank_written = False
    middle_bank_written = False
    bottom_bank_written = False

    for box_number, theta, detector_ids, phi in detector_box_list:

        if phi < 0 and not bottom_bank_written:
            output_file.write("""<type name="bottom_bank">""")
            bottom_bank_written = True
        elif phi == 0 and not middle_bank_written:
            output_file.write("""</type>""")
            output_file.write("""<type name="middle_bank">""")
            middle_bank_written = True
        elif phi > 0 and not top_bank_written:
            output_file.write("""</type>""")
            output_file.write("""<type name="top_bank">""")
            top_bank_written = True

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
                         </location>
                       </component>""".format(box_number, x, y, z, math.degrees(math.atan2(x, z)) + 180.0, phi,
                                              tilting_angle(theta, phi, orientation) + 180.0))

            id_strings.append("""<idlist idname="det_id_list_{number}">
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
            id_strings.append("""<idlist idname="det_id_list_{number}">
                         <id val="{ids[0]}" />
                         <id val="{ids[1]}" />
                         <id val="{ids[2]}" />
                         <id val="{ids[3]}" />
                       </idlist>""".format(number=box_number, ids=detector_ids))
        else:
            raise ValueError('Unexpected number of dectors in box')

    output_file.write("""</type>""")

    # Finally write the strings linking the detector box number to the appropriate detectors
    for string in id_strings:
        output_file.write(string)


def write_in6_box_types(output_file, detector_gap, orientation):
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


def write_in6_banks(output_file):
    """Writes the wide angle detector banks to the file.
    """
    output_file.write('<type name="detectors">\n')
    output_file.write('  <component type="top_bank">\n')
    output_file.write('    <location />\n')
    output_file.write('  </component>\n')
    output_file.write('  <component type="middle_bank">\n')
    output_file.write('    <location />\n')
    output_file.write('  </component>\n')
    output_file.write('  <component type="bottom_bank">\n')
    output_file.write('    <location />\n')
    output_file.write('  </component>\n')
    output_file.write('</type>\n')
    output_file.write('<component type="detectors">')
    output_file.write('  <location />')
    output_file.write('</component>')


if __name__ == '__main__':
    RADIUS = 2.483
    DETECTOR_GAP = 0.03380144566
    OUTPUT_FILENAME = 'IN6_Definition.xml'
    DETECTOR_BOX_LIST_FILENAME = 'in6_detector_box_list.txt'

    DETECTOR_BOX_LIST = read_detector_box_list(DETECTOR_BOX_LIST_FILENAME)
    IDF_FILE = open(OUTPUT_FILENAME, 'w')

    write_header(IDF_FILE, 'IN6', 'Riccardo Leal and Ian Bush')
    write_in6_source_chopper(IDF_FILE)
    write_in6_monitor_positions(IDF_FILE)
    write_sample_position(IDF_FILE)
    IDF_FILE.write("<!-- Detector boxes -->")
    write_in6_detectors(IDF_FILE, DETECTOR_BOX_LIST, RADIUS, -1)
    write_in6_box_types(IDF_FILE, DETECTOR_GAP, -1)
    write_in6_banks(IDF_FILE)
    write_in6_detector_shape(IDF_FILE)
    write_in6_monitor_shapes(IDF_FILE)
    write_end(IDF_FILE)

    IDF_FILE.close()

    clean_up_xml(OUTPUT_FILENAME)
