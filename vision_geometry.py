#! /usr/bin/env python

import math

INCH_TO_METRE = 0.0254

# BACKSCATTERING ELASTIC
BS_ELASTIC_LONG_TUBE_INNER_RADIUS = 4.0 * INCH_TO_METRE
BS_ELASTIC_LONG_TUBE_OUTER_RADIUS = 22.0 * INCH_TO_METRE
BS_ELASTIC_LONG_TUBES_PER_BANK = 1
BS_ELASTIC_LONG_TUBE_NPIXELS = 256
BS_ELASTIC_LONG_TUBE_LENGTH = BS_ELASTIC_LONG_TUBE_OUTER_RADIUS - BS_ELASTIC_LONG_TUBE_INNER_RADIUS
BS_ELASTIC_LONG_TUBE_WIDTH = 0.5 * INCH_TO_METRE
BS_ELASTIC_LONG_TUBE_PRESSURE = ("tube_pressure", 30.0, "atm")
BS_ELASTIC_LONG_TUBE_THICKNESS = ("tube_thickness", (0.01 * INCH_TO_METRE), "metre")
BS_ELASTIC_LONG_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

BS_ELASTIC_SHORT_TUBE_INNER_RADIUS = 7.0 * INCH_TO_METRE
BS_ELASTIC_SHORT_TUBE_OUTER_RADIUS = 22.0 * INCH_TO_METRE
BS_ELASTIC_SHORT_TUBES_PER_BANK = 1
BS_ELASTIC_SHORT_TUBE_NPIXELS = 256
BS_ELASTIC_SHORT_TUBE_LENGTH = BS_ELASTIC_SHORT_TUBE_OUTER_RADIUS - BS_ELASTIC_SHORT_TUBE_INNER_RADIUS
BS_ELASTIC_SHORT_TUBE_WIDTH =  0.5 * INCH_TO_METRE
BS_ELASTIC_SHORT_TUBE_PRESSURE = ("tube_pressure", 30.0, "atm")
BS_ELASTIC_SHORT_TUBE_THICKNESS = ("tube_thickness",  (0.01 * INCH_TO_METRE), "metre")
BS_ELASTIC_SHORT_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

# ELASTIC (90 deg)
ELASTIC_TUBES_PER_BANK = 8
ELASTIC_TUBE_NPIXELS = 256
ELASTIC_TUBE_LENGTH = 7.5 * INCH_TO_METRE
ELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
ELASTIC_AIR_GAP = 0.14 *  INCH_TO_METRE    # Tube centres are 0.64" apart
ELASTIC_TUBE_PRESSURE = ("tube_pressure", 30.0, "atm")
ELASTIC_TUBE_THICKNESS = ("tube_thickness",  (0.01 * INCH_TO_METRE), "metre")
ELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

# INELASTIC 
INELASTIC_TUBES_PER_BANK = 8
INELASTIC_TUBE_NPIXELS = 128
INELASTIC_TUBE_LENGTH = 6.375 * INCH_TO_METRE
INELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
INELASTIC_AIR_GAP = 0.0
INELASTIC_TUBE_PRESSURE = ("tube_pressure", 8.0, "atm")
INELASTIC_TUBE_THICKNESS = ("tube_thickness",  (0.01 * INCH_TO_METRE), "metre")
INELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

def main():
    from helper import MantidGeom
    
    inst_name = "VISION"
    
    xml_outfile = inst_name+"_Definition.xml"
    
    comment = " Created by Stuart Campbell "
    valid_from = "2012-01-01 00:00:01"
    
    det = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(indirect=True)
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-16.0)
    det.addSamplePosition()

    # Backscattering Banks are 21-100

    BACKSCATTERING_NTUBES = 80

    det.addComponent("elastic-backscattering", "elastic-backscattering")
    handle = det.makeTypeElement("elastic-backscattering")

    idlist = []

    for k in range(BACKSCATTERING_NTUBES):
        id_start = 26624+(256*k)
        id_end = 26624 + (256*k) + 255
        angle = -(2.25 + 4.5*k)
        bankid = 21 + k
        bank_name = "bank%d" % bankid

        det.addComponent(bank_name, root=handle)

        z_coord = -0.998

        if k%2 == 0:
            # Even tube number (long)
            centre_offset = BS_ELASTIC_LONG_TUBE_INNER_RADIUS + (BS_ELASTIC_LONG_TUBE_LENGTH/2.0)
            #centre_offset = BS_ELASTIC_LONG_TUBE_INNER_RADIUS
            component_name = "tube-long-bs-elastic"
        else:
            # Odd tube number (short)
            centre_offset = BS_ELASTIC_SHORT_TUBE_INNER_RADIUS + (BS_ELASTIC_SHORT_TUBE_LENGTH/2.0)
            component_name = "tube-short-bs-elastic"

        x_coord = centre_offset * math.cos(math.radians(90-angle))
        y_coord = centre_offset * math.sin(math.radians(90-angle))

        det.addDetector(x_coord, y_coord, z_coord, 0, 0, -angle, bank_name, component_name)

        idlist.append(id_start)
        idlist.append(id_end)
        idlist.append(None)

    det.addDetectorIds("elastic-backscattering", idlist)


    # 90 elastic banks

    elastic_banklist = [3,6,9,12,15,18]
    elastic_bank_start = [2048,6144,10240,14336,18432,22528]
    elastic_angle = [157.5,-157.5,-67.5,-112.5,-22.5,22.5]

    sample_elastic_distance = 0.635

    det.addComponent("elastic", "elastic")
    handle = det.makeTypeElement("elastic")

    idlist = []
    elastic_index = 0

    for i in elastic_banklist:
        bank_name = "bank%d" % i
        det.addComponent(bank_name, root=handle)

        z_coord = 0.0
        x_coord = sample_elastic_distance * math.cos(math.radians(elastic_angle[elastic_index]))
        y_coord = sample_elastic_distance * math.sin(math.radians(elastic_angle[elastic_index]))

        det.addDetector(x_coord, y_coord, z_coord, -90.0, 180, 0., bank_name, "eightpack-elastic", facingSample=True)

        idlist.append(elastic_bank_start[elastic_index])
        idlist.append(elastic_bank_start[elastic_index]+2047)
        idlist.append(None)

        elastic_index += 1


    det.addDetectorIds("elastic", idlist)

    # Inelastic
    inelastic_banklist = [1,2,4,5,7,8,10,11,13,14,16,17,19,20]
    inelastic_bank_start=[0,1024,4096,5120,8192,9216,12288,13312,16384,17408,20480,21504,24576,25600]
    inelastic_angle = [45.0,45.0,0.0,0.0,-45.0,-45.0,-90.0,-90.0,-135.0,-135.0,180.0,180.0,135.0,135.0]
    inelastic_angle_for_rotation = [-45.0,-45.0,180.0,180.0,-135.0,-135.0,-90.0,-90.0,-225.0,-225.0,0.0,0.0,45.0,45.0]

    sample_inelastic_distance = 0.5174

    det.addComponent("inelastic", "inelastic")
    handle = det.makeTypeElement("inelastic")

    idlist = []
    inelastic_index = 0

    for i in inelastic_banklist:
        bank_name = "bank%d" % i
        bank_comp = det.addComponent(bank_name, root=handle, blank_location=True)
#        location_element = le.SubElement(bank_comp, "location")
#        le.SubElement(location_element, "rot", **{"val":"90", "axis-x":"0",
#                                              "axis-y":"0", "axis-z":"1"})

        # Neutronic Positions
        z_coord_neutronic = sample_inelastic_distance * math.tan(math.radians(45.0))

        if inelastic_index % 2 == 0:
            # Facing Downstream
            z_coord = 0.01
        else:
            # Facing to Moderator
            z_coord = -0.01
            z_coord_neutronic = -z_coord_neutronic

            # Physical Positions
        x_coord = sample_inelastic_distance * math.cos(math.radians(inelastic_angle[inelastic_index]))
        y_coord = sample_inelastic_distance * math.sin(math.radians(inelastic_angle[inelastic_index]))

        det.addDetector(-x_coord, y_coord, z_coord, 0, 0, inelastic_angle_for_rotation[inelastic_index]-90.0, bank_name,
            "eightpack-inelastic", neutronic=True, nx=-x_coord, ny=y_coord, nz=z_coord_neutronic)

        efixed = ("Efixed", "3.64", "meV")
        det.addDetectorParameters(bank_name, efixed )

        idlist.append(inelastic_bank_start[inelastic_index])
        idlist.append(inelastic_bank_start[inelastic_index]+1023)
        idlist.append(None)

        inelastic_index += 1


    det.addDetectorIds("inelastic", idlist)


    # 8 packs
    
    det.addComment("INELASTIC 8-PACK")
    det.addNPack("eightpack-inelastic", INELASTIC_TUBES_PER_BANK, INELASTIC_TUBE_WIDTH, 
                 INELASTIC_AIR_GAP, "tube-inelastic", neutronic=True)
    
    det.addComment("ELASTIC 8-PACK")
    det.addNPack("eightpack-elastic", ELASTIC_TUBES_PER_BANK, ELASTIC_TUBE_WIDTH, 
                 ELASTIC_AIR_GAP, "tube-elastic", neutronic=True, neutronicIsPhysical=True)
 
    # TUBES
    det.addComment("INELASTIC TUBE")
    det.addPixelatedTube("tube-inelastic", INELASTIC_TUBE_NPIXELS, 
                         INELASTIC_TUBE_LENGTH, "pixel-inelastic-tube", neutronic=True)
    
    det.addComment("BACKSCATTERING LONG TUBE")
    det.addPixelatedTube("tube-long-bs-elastic", BS_ELASTIC_LONG_TUBE_NPIXELS,
        BS_ELASTIC_LONG_TUBE_LENGTH, "pixel-bs-elastic-long-tube",
        neutronic=True, neutronicIsPhysical=True)
    det.addComment("BACKSCATTERING SHORT TUBE")
    det.addPixelatedTube("tube-short-bs-elastic", BS_ELASTIC_SHORT_TUBE_NPIXELS, 
        BS_ELASTIC_SHORT_TUBE_LENGTH, "pixel-bs-elastic-short-tube",
        neutronic=True, neutronicIsPhysical=True)

    det.addComment("ELASTIC TUBE (90 degrees)")
    det.addPixelatedTube("tube-elastic", ELASTIC_TUBE_NPIXELS, 
                         ELASTIC_TUBE_LENGTH, "pixel-elastic-tube", neutronic=True, neutronicIsPhysical=True)

    # PIXELS
    
    det.addComment("PIXEL FOR INELASTIC TUBES")
    det.addCylinderPixel("pixel-inelastic-tube", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (INELASTIC_TUBE_WIDTH/2.0), 
                         (INELASTIC_TUBE_LENGTH/INELASTIC_TUBE_NPIXELS))
    
    det.addComment("PIXEL FOR BACKSCATTERING ELASTIC TUBES (LONG)")
    det.addCylinderPixel("pixel-bs-elastic-long-tube", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 
                         (BS_ELASTIC_LONG_TUBE_WIDTH/2.0), 
                         (BS_ELASTIC_LONG_TUBE_LENGTH/BS_ELASTIC_LONG_TUBE_NPIXELS))

    det.addComment("PIXEL FOR BACKSCATTERING ELASTIC TUBES (SHORT)")
    det.addCylinderPixel("pixel-bs-elastic-short-tube", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (BS_ELASTIC_SHORT_TUBE_WIDTH/2.0), 
                         (BS_ELASTIC_SHORT_TUBE_LENGTH/BS_ELASTIC_SHORT_TUBE_NPIXELS))
    
    det.addComment("PIXEL FOR ELASTIC TUBES (90 degrees)")
    det.addCylinderPixel("pixel-elastic-tube", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (ELASTIC_TUBE_WIDTH/2.0), 
                         (ELASTIC_TUBE_LENGTH/ELASTIC_TUBE_NPIXELS))


    det.addComment(" ##### MONITORS ##### ")
    det.addMonitors(names=["monitor1","monitor4"], distance=["-6.71625","0.287"], neutronic=True)


    # MONITORS

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: All monitors share the dimensions of monitor4.")

    det.addCuboidMonitor(0.051,0.054,0.013)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1","-4"])

    det.showGeom()
    det.writeGeom(xml_outfile)




if __name__ == '__main__':
	main()
    
