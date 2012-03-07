#! /usr/bin/python

INCH_TO_METRE = 0.0254

# BACKSCATTERING ELASTIC
BS_ELASTIC_LONG_TUBES_PER_BANK = 1
BS_ELASTIC_LONG_TUBE_NPIXELS = 256
BS_ELASTIC_LONG_TUBE_LENGTH = (22 - 7) * INCH_TO_METRE
BS_ELASTIC_LONG_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
BS_ELASTIC_LONG_TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
BS_ELASTIC_LONG_TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
BS_ELASTIC_LONG_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

BS_ELASTIC_SHORT_TUBES_PER_BANK = 1
BS_ELASTIC_SHORT_TUBE_NPIXELS = 256
BS_ELASTIC_SHORT_TUBE_LENGTH = (22 - 4) * INCH_TO_METRE
BS_ELASTIC_SHORT_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
BS_ELASTIC_SHORT_TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
BS_ELASTIC_SHORT_TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
BS_ELASTIC_SHORT_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

# ELASTIC (90 deg)
ELASTIC_TUBES_PER_BANK = 8
ELASTIC_TUBE_NPIXELS = 256
ELASTIC_TUBE_LENGTH = 7.5 * INCH_TO_METRE
ELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
ELASTIC_AIR_GAP = 0.14 *  INCH_TO_METRE    # Tube centres are 0.64" apart
ELASTIC_TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
ELASTIC_TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
ELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

# INELASTIC 
INELASTIC_TUBES_PER_BANK = 8
INELASTIC_TUBE_NPIXELS = 128
INELASTIC_TUBE_LENGTH = 6.375 * INCH_TO_METRE
INELASTIC_TUBE_WIDTH = 0.5 * INCH_TO_METRE   # 0.5" diameter tubes
INELASTIC_AIR_GAP = 0.0
INELASTIC_TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
INELASTIC_TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
INELASTIC_TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

def main():
    from helper import MantidGeom
    
    inst_name = "VISION"
    
    xml_outfile = inst_name+"_Definition.xml"
    
    det = MantidGeom(inst_name, comment=" Created by Stuart Campbell ")
    det.addSnsDefaults(indirect=True)
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-16.0)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1"], distance=["-6.71625"], neutronic=True)


    
    #det.addDetector(x, y, z, rot_x, rot_y, rot_z, name, comp_type, usepolar)
    
    
 
    # 8 packs
    
    det.addComment("INELASTIC 8-PACK")
    det.addNPack("eightpack-inelastic", INELASTIC_TUBES_PER_BANK, INELASTIC_TUBE_WIDTH, 
                 INELASTIC_AIR_GAP, "tube-inelastic")    
    
    det.addComment("ELASTIC 8-PACK")
    det.addNPack("eightpack-elastic", ELASTIC_TUBES_PER_BANK, ELASTIC_TUBE_WIDTH, 
                 ELASTIC_AIR_GAP, "tube-inelastic")
 
    # TUBES
    det.addComment("INELASTIC TUBE")
    det.addPixelatedTube("tube-inelastic", INELASTIC_TUBE_NPIXELS, 
                         INELASTIC_TUBE_LENGTH, "pixel-inelastic-tube")
    
    det.addComment("BACKSCATTERING LONG TUBE")
    det.addPixelatedTube("tube-long-bs-elastic", BS_ELASTIC_LONG_TUBE_NPIXELS, 
                         BS_ELASTIC_LONG_TUBE_LENGTH, "pixel-bs-elastic-long-tube")
    det.addComment("BACKSCATTERING SHORT TUBE")
    det.addPixelatedTube("tube-short-bs-elastic", BS_ELASTIC_SHORT_TUBE_NPIXELS, 
                         BS_ELASTIC_SHORT_TUBE_LENGTH, "pixel-bs-elastic-short-tube")

    det.addComment("ELASTIC TUBE (90 degrees)")
    det.addPixelatedTube("tube-elastic", ELASTIC_TUBE_NPIXELS, 
                         ELASTIC_TUBE_LENGTH, "pixel-elastic-tube")

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


    # MONITORS

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1"])




    det.showGeom()
    det.writeGeom(xml_outfile)


if __name__ == '__main__':
	main()