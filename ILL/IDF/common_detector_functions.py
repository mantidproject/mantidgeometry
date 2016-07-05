from time import gmtime, strftime
import math


def read_detector_bank_list(filename):

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

    
def tilting_angle(theta, phi, orientation):
    theta = math.radians(theta)
    phi = math.radians(phi)
    return 90 + (math.degrees(math.acos(math.cos(theta) / math.sin(theta) * math.sin(phi) / math.cos(phi)))) * orientation


def write_detectors(f, detector_bank_list, radius, detector_gap, orientation):
    """Generates a set of detectors in banks, according to the contents of detector_bank_list.
    
       detector_bank_list: A list of tuples containing bank_number, theta angle, a list of detector ids, phi angle
       radius: Sample to detector distance
       detector_gap: Gap between detectors in a box
       orientation: +1 indicates anti-clockwise from the z-axis, -1 clockwise    
    """
    

    first_bank_id = detector_bank_list[0][0]
    number_of_banks = detector_bank_list[-1][0]
    
    first_detector_id = detector_bank_list[0][2]
    print first_bank_id, number_of_banks, first_detector_id
    
    f.write("<!-- Detector Banks -->")
    
    for bank_number, theta, detector_ids, phi in detector_bank_list:
		
        print bank_number, theta, detector_ids, phi
        
        # Compute cartesian coordinates of bank
        x = orientation * radius * math.sqrt(math.sin(math.radians(theta))**2 - math.sin(math.radians(phi))**2)
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
                       </component>""" % (bank_number, bank_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi, orientation)))

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
                       </component>""" % (bank_number, bank_number, x, y, z, math.degrees(math.atan2(x, z)), -phi, tilting_angle(theta, phi, orientation)))
            f.write("""<idlist idname="det_id_list_%d">
                         <id val="%d" />
                         <id val="%d" />
                         <id val="%d" />
                         <id val="%d" />                         
                       </idlist>""" %(bank_number, detector_ids[0], detector_ids[1], detector_ids[2], detector_ids[3]))                       
        else:
            raise(ValueError('Unexpected number of dectors in bank'))
            
    f.write("""<type name="bank_3_dets">
                 <component type = "tube">
                   <location x="%f" y="0.0" z="0.0" name="tube_1" />
                   <location x="%f" y="0.0" z="0.0" name="tube_2" />
                   <location x="%f" y="0.0" z="0.0" name="tube_3" />
                 </component>                          
               </type>""" % (detector_gap * -1.0, detector_gap * 0.0, detector_gap * 1.0))
               
    f.write("""<type name="bank_4_dets">
                 <component type = "tube">
                   <location x="%f" y="0.0" z="0.0" name="tube_1" />
                   <location x="%f" y="0.0" z="0.0" name="tube_2" />
                   <location x="%f" y="0.0" z="0.0" name="tube_3" />
                   <location x="%f" y="0.0" z="0.0" name="tube_4" />
                 </component>                 
               </type>""" % (detector_gap * -1.5, detector_gap * -0.5, detector_gap * 0.5, detector_gap * 1.5))


def write_end(f):
    f.write("</instrument>")
