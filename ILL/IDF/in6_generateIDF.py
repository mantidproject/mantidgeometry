import os, sys
import math
from time import gmtime, strftime

"""This script is used to generate the IDF for IN6...

"""

def tilting_angle(theta, phi):
    theta = math.radians(theta)
    phi = math.radians(phi)
    return 90 + math.degrees(math.acos(math.cos(theta) / math.sin(theta) * math.sin(phi) / math.cos(phi)))

def read_input(filename):

    bank_number = []
    theta = []
    detector_ids = []
    phi = []

    with open(filename) as detector_bank_list:
        next(detector_bank_list) # Skip header line

        for line in detector_bank_list:
            line_entries = line.split()

            bank_number.append(int(line_entries[0]))
            theta.append(float(line_entries[1]))
            
            detector_id_line = []
            for value in line_entries[2].split(','):
                try:
                    detector_id_line.append(int(value))
                except:
                    pass
            detector_ids.append(detector_id_line)
            phi.append(float(line_entries[3]))
            
    return zip(bank_number, theta, detector_ids, phi)


def writeHeader(f):
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
    <!-- For help on the notation used to specify an Instrument Definition File see http://www.mantidproject.org/IDF -->
    <instrument xmlns="http://www.mantidproject.org/IDF/1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.mantidproject.org/IDF/1.0 Schema/IDFSchema.xsd" name="IN6" valid-from="1900-01-31 23:59:59"
    valid-to="2100-01-31 23:59:59" last-modified="%s">""" % strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    f.write("""<!-- Author: Ricardo Leal and Ian Bush -->""")
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
    </defaults>

    <component type="moderator">
      <location z="-2" />
    </component>
    <type name="moderator" is="Source"></type>

    <!--MONITORS-->
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
    </type>

    <!-- Sample position -->
    <component type="sample-position">
      <location y="0.0" x="0.0" z="0.0" />
    </component>

    <type name="sample-position" is="SamplePos" />""")


def writeDetectors(f, detector_bank_list):
    
    radius = 2.483
    detector_gap = 0.03380144566

    first_bank_id = detector_bank_list[0][0]
    number_of_banks = detector_bank_list[-1][0]
    
    first_detector_id = detector_bank_list[0][2]
    print first_bank_id, number_of_banks, first_detector_id
    
    f.write("<!-- Detector Banks -->")
    
    for bank_number, theta, detector_ids, phi in detector_bank_list:
		
        print bank_number, theta, detector_ids, phi
        
        # Compute cartesian coordinates of bank
#        x = - radius * math.sin(math.radians(theta)) * math.cos(math.radians(phi))
#        y = radius * math.sin(math.radians(phi))
#        z = radius * math.cos(math.radians(theta)) * math.cos(math.radians(phi))
        x = - radius * math.sqrt(math.sin(math.radians(theta))**2 - math.sin(math.radians(phi))**2)
        y = radius * math.sin(math.radians(phi))
        z = radius * math.cos(math.radians(theta))

        print bank_number, x, y, z, radius, theta
        
        if len(detector_ids) == 3:	
            f.write("""<component type="bank_3_dets" name="bank_%d" idlist="det_id_list_%d">
                         <location x="%f" y="%f" z="%f">
							<rot val="%f" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="%f" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="%f" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>                         
                         </location/>
                       </component>""" % (bank_number, bank_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi)))

            f.write("""<idlist idname="det_id_list_%d">
                         <id val="%d" />
                         <id val="%d" />
                         <id val="%d" />
                       </idlist>""" %(bank_number, detector_ids[0], detector_ids[1], detector_ids[2]))
        elif len(detector_ids) == 4:
            f.write("""<component type="bank_4_dets" name="bank_%d" idlist="det_id_list_%d">
                         <location x="%f" y="%f" z="%f"> 
							<rot val="%f" axis-x="0.0" axis-y="1.0" axis-z="0.0" >
								<rot val="%f" axis-x="1.0" axis-y="0.0" axis-z="0.0" >
									<rot val="%f" axis-x="0.0" axis-y="0.0" axis-z="1.0" />
						        </rot>
							</rot>
						 </location>
                       </component>""" % (bank_number, bank_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi)))
            f.write("""<idlist idname="det_id_list_%d">
                         <id val="%d" />
                         <id val="%d" />
                         <id val="%d" />
                         <id val="%d" />                         
                       </idlist>""" %(bank_number, detector_ids[0], detector_ids[1], detector_ids[2], detector_ids[3]))                       
        else:
            raise(ValueError('Unexpected number of dectors in bank'))
            
    f.write("""<type name="bank_3_dets">
                 <component type = "pixel">
                   <location x="%f" y="0.0" z="0.0" name="tube_1" />
                   <location x="%f" y="0.0" z="0.0" name="tube_2" />
                   <location x="%f" y="0.0" z="0.0" name="tube_3" />
                 </component>                          
               </type>""" % (detector_gap * -1.0, detector_gap * 0.0, detector_gap * 1.0))
               
    f.write("""<type name="bank_4_dets">
                 <component type = "pixel">
                   <location x="%f" y="0.0" z="0.0" name="tube_1" />
                   <location x="%f" y="0.0" z="0.0" name="tube_2" />
                   <location x="%f" y="0.0" z="0.0" name="tube_3" />
                   <location x="%f" y="0.0" z="0.0" name="tube_4" />
                 </component>                 
               </type>""" % (detector_gap * -1.5, detector_gap * -0.5, detector_gap * 0.5, detector_gap * 1.5))
               
    f.write("""<!-- Pixel for Detectors. Shape defined to be a (0.001m)^2 square in XY-plane with tickness 0.0001m -->
                 <type is="detector" name="pixel">
                   <cuboid id="pixel-shape">
                     <left-front-bottom-point y="-0.150" x="-0.016" z="0.0"/>
                     <left-front-top-point y="0.150" x="-0.016" z="0.0"/>
                     <left-back-bottom-point y="-0.150" x="-0.016" z="-0.016"/>
                     <right-front-bottom-point y="-0.150" x="0.016" z="0.0"/>
                   </cuboid>
                   <algebra val="pixel-shape"/>
                 </type>""")


def writeMonitors(f):
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


def writePixels(f):
    f.write(""" <type name="pack" is="detector">  
    <cuboid id="pack-pixel-shape">
        <left-front-bottom-point x="0.01" y="-0.2" z="0.0" />
        <left-front-top-point x="0.01" y="-0.2" z="0.01" />
        <left-back-bottom-point x="-0.01" y="-0.2" z="0.0" />
        <right-front-bottom-point x="0.01" y="0.2" z="0.0" />
    </cuboid>
    <algebra val="pack-pixel-shape" />     
    </type>""")


def writeEnd(f):
    f.write("</instrument>")


if __name__ == '__main__':
    detector_bank_list = read_input('IN6_detector_bank_list.txt')

    f = open('IDF_temp.xml ', 'w')
    writeHeader(f)
    writeDetectors(f, detector_bank_list)
    writeMonitors(f)
    writePixels(f)
    writeEnd(f)
    f.close()
    os.system('tidy -utf8 -xml -w 255 -i -c -q -asxml IDF_temp.xml\ > IN6_Definition.xml')
    

