#!/usr/bin/python

NUM_PIXELS_PER_TUBE = 128
NUM_TUBES_PER_BANK = 8
TUBE_SIZE = 2.0 #meter
TUBE_WIDTH = 0.0254 #meter
AIR_GAP_WIDTH = 0.002032 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1.0 #x,y,z are in meters
BANKFMT = "bank%d"
ROTX = None # no X rotation
ROTZ = None # no z rotation
FLIPY = 180.0 # flip y orientation
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 6.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")

def convert(value):
    return float(value) / CONVERT_TO_METERS

if __name__ == "__main__":
    import sys
    from helper import MantidGeom
    from sns_ncolumn import readFile

    try:
        geom_input_file = sys.argv[1]
    except IndexError:
        geom_input_file = "SNS/CNCS/CNCS_geom_136675-.txt"
        
    # Set header information
    comment = "Created by Michael Reuter"
    # Time needs to be in UTC?
    valid_from = "2015-08-01 00:00:00"

    # Get geometry information file
    inst_name = "CNCS"
    detinfo = readFile(geom_input_file)
    num_dets = len(detinfo.values()[0])
    xml_outfile = inst_name+"_Definition.xml"
 
    det = MantidGeom(inst_name, comment=comment, valid_from=valid_from)
    det.addSnsDefaults()
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-36.262)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1", "monitor2", "monitor3"],
                    distance=["-29.949", "-28.706", "-1.416"])

    label = "detectors"
    det.addComponent(label, label)
    doc_handle = det.makeTypeElement(label)
    for i in range(num_dets):
        detname = BANKFMT % (i+1)
        roty = float(detinfo["BankAngle"][i]) + FLIPY
        xpos = convert(detinfo["Bank_xpos"][i])
        ypos = convert(detinfo["Bank_ypos"][i])
        zpos = convert(detinfo["Bank_zpos"][i])
        det.addComponent(detname, root=doc_handle)
        det.addDetector(xpos, ypos, zpos, ROTX, roty, ROTZ, detname, "eightpack")

    det.addComment("STANDARD 8-PACK")
    det.addNPack("eightpack", NUM_TUBES_PER_BANK, TUBE_WIDTH, AIR_GAP_WIDTH)

    det.addComment("STANDARD 2m 128 PIXEL TUBE")
    det.addPixelatedTube("tube", NUM_PIXELS_PER_TUBE, TUBE_SIZE)

    det.addComment("PIXEL FOR STANDARD 2m 128 PIXEL TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("DETECTOR IDs")
    det.addDetectorIds(label, [0, (num_dets * PIXELS_PER_BANK) - 1 , None])

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1", "-2", "-3"])

    det.addComment("DETECTOR PARAMETERS")
    det.addDetectorParameters(label, TUBE_PRESSURE, TUBE_THICKNESS,
                              TUBE_TEMPERATURE)    
    
    #det.showGeom()
    det.writeGeom(xml_outfile)

