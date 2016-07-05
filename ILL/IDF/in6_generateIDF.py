from common_detector_functions import *
import os, sys

"""This script is used to generate the IDF for IN6...

"""


def write_in6_monitor_positions(f):
    f.write("""<!--MONITORS-->
    <component type="monitors" idlist="monitors">
      <location/>

    </component>
    <type name="monitors">
      <component type="monitor">
        <location z="-0.6" name="monitor1"/>
      </component>
      <component type="monitor">
        <location z="-0.5" name="monitor2"/>
      </component>
      <component type="monitor">
        <location z="-0.4" name="monitor3"/>
      </component>
    </type>""")


def write_in6_detector_shape(f): 
    f.write("""<!-- Detector tube shape. Cuboids 32 x 16 mm, 300 mm long -->
                 <type is="detector" name="tube">
                   <cuboid id="pixel-shape">
                     <left-front-bottom-point y="-0.150" x="-0.016" z="0.0"/>
                     <left-front-top-point y="0.150" x="-0.016" z="0.0"/>
                     <left-back-bottom-point y="-0.150" x="-0.016" z="-0.016"/>
                     <right-front-bottom-point y="-0.150" x="0.016" z="0.0"/>
                   </cuboid>
                   <algebra val="pixel-shape"/>
                 </type>""")


def write_in6_monitor_shapes(f):
    f.write("""<!--MONITOR SHAPE-->
    <!--FIXME: Do something real here.-->
    <type is="monitor" name="monitor">
    <cylinder id="cyl-approx">
    <centre-of-bottom-base y="0.0" x="0.0" z="0.0"/>
    <axis y="0.0" x="0.0" z="1.0"/>
    <radius val="0.01"/>
    <height val="0.03"/>
    </cylinder>
    <algebra val="cyl-approx"/>
    </type>

    <!--MONITOR IDs-->
    <idlist idname="monitors">
        <id start="0" end="2" />
    </idlist>
    """)


if __name__ == '__main__':
    radius = 2.483
    detector_gap = 0.03380144566
    
    temp_file = 'temp.xml'
    detector_file_name = 'IN6_Definition.xml'
    detector_bank_list_name = 'in6_detector_bank_list.txt'
    
    detector_bank_list = read_detector_bank_list(detector_bank_list_name)
    f = open(temp_file, 'w')
    
    write_header(f, 'IN6', 'Riccardo Leal and Ian Bush')
    write_moderator(f)
    write_in6_monitor_positions(f)
    write_sample_position(f)
    write_detectors(f, detector_bank_list, radius, detector_gap, -1)
    write_in6_detector_shape(f)    
    write_in6_monitor_shapes(f)
    write_end(f)
    
    f.close()
    
    os.system('tidy -utf8 -xml -w 255 -i -c -q -asxml {0} > {1}'.format(temp_file, detector_file_name))
    os.remove(temp_file)
    
    

