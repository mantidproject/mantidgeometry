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
    write_detectors(IDF_FILE, DETECTOR_BOX_LIST, RADIUS, DETECTOR_GAP, -1)
    write_in6_detector_shape(IDF_FILE)
    write_in6_monitor_shapes(IDF_FILE)
    write_end(IDF_FILE)

    IDF_FILE.close()

    clean_up_xml(OUTPUT_FILENAME)
