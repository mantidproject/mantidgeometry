#!/usr/bin/env python

INST_NAME = "SEQUOIA"
NUM_PIXELS_PER_TUBE = 128
NUM_TUBES_PER_BANK = 8
SMALL_TOP_TUBE_SIZE = 0.25908 #meter
SMALL_BOTTOM_TUBE_SIZE = 0.333502 #meter
LARGE_TUBE_SIZE = 1.2 #meter
TUBE_WIDTH = 0.0254 #meter
AIR_GAP_WIDTH = 0.002032 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1.0/0.0254 #x,y,z are in inches
ROTX = None # no x rotation
ROTZ = None # no z rotation
FLIPY = 180.0 # flip y orientation
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0008, "metre")
TUBE_TEMPERATURE = ("tube_temperature", 290.0, "K")
# Add choppers or not?
ADD_CHOPPERS = False
    
def convert(value):
    # set string formatting here
    return '%.8f' % (float(value) / CONVERT_TO_METERS,)
    
if __name__ == "__main__":
    import sys
    from helper import MantidGeom
    from sns_ncolumn import readFile
    
    try:
        geom_input_file = sys.argv[1]
    except IndexError:
        geom_input_file = "SNS/SEQ/SEQ_geom_05142018.txt"
        
    # Set header information
    comment = "For runs after May 14, 2018"
    # Time needs to be in UTC?
    valid_from = "2012-04-04 14:15:46"

    # Get geometry information file

    detinfo = readFile(geom_input_file)
    num_dets = len(detinfo.values()[0])
    xml_outfile = INST_NAME+"_Definition.xml"
    
    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults()
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-20.0114)
    det.addSamplePosition()
    if ADD_CHOPPERS:
        det.addComment("CHOPPERS")
        det.addChopper("t0-chopper",-10.51)
        det.addVerticalAxisT0Chopper("t0-chopper")
        det.addChopper("fermi-chopper",-2.00180)
        det.addFermiChopper("fermi-chopper")
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1", "monitor2"],
                    distance=["-1.77808", "8.99184"])

    row_id = ""
    row_id_list = []
    doc_handle = None
    for i in range(num_dets):
        location = detinfo["Location"][i]
        # REMOVE ME: when A and E rows are filled
        if location.startswith("A") or \
               location.startswith("E"):
            continue
        
        if row_id != location[0]:
            row_id = location[0]
            row_id_list.append(row_id)
            row_id_str = row_id + " row"
            det.addComponent(row_id_str, row_id_str)
            doc_handle = det.makeTypeElement(row_id_str)

        # naming convention for detector packs
        detpackname = 'pack' + str(i+38)
        detpackname = location
        det.addComponent(detpackname, root=doc_handle)
        
        xpos = convert(detinfo["X"][i])
        ypos = convert(detinfo["Y"][i])
        zpos = convert(detinfo["Z"][i])
        roty = float(detinfo["Angle"][i]) + FLIPY
        # string formatting for rotation angle 
        roty = '%.8f' % roty
        det_type = "eightpack"
        
        if location.startswith("C"):
            if location.endswith("T"):
                det_type = "eightpack-top"
            elif location.endswith("B"):
                det_type = "eightpack-bottom"

        det.addDetector(xpos, ypos, zpos, ROTX, roty, ROTZ, detpackname, det_type)

    det.addComment("STANDARD 8-PACK")
    det.addNPack("eightpack", NUM_TUBES_PER_BANK, TUBE_WIDTH, AIR_GAP_WIDTH)
    det.addComment("8-PACK ABOVE BEAMSTOP")
    det.addNPack("eightpack-top", NUM_TUBES_PER_BANK, TUBE_WIDTH,
                 AIR_GAP_WIDTH, type_name="tube-top")
    det.addComment("8-PACK BELOW BEAMSTOP")
    det.addNPack("eightpack-bottom", NUM_TUBES_PER_BANK, TUBE_WIDTH,
                 AIR_GAP_WIDTH, type_name="tube-bottom")

    det.addComment("STANDARD 128 PIXEL TUBE")
    det.addPixelatedTube("tube", NUM_PIXELS_PER_TUBE, LARGE_TUBE_SIZE)
    det.addComment("SMALL TOP 128 PIXEL TUBE")
    det.addPixelatedTube("tube-top", NUM_PIXELS_PER_TUBE, SMALL_TOP_TUBE_SIZE,
                         type_name="pixel-top")
    det.addComment("SMALL BOTTOM 128 PIXEL TUBE")
    det.addPixelatedTube("tube-bottom", NUM_PIXELS_PER_TUBE,
                         SMALL_BOTTOM_TUBE_SIZE, type_name="pixel-bottom")

    det.addComment("PIXEL FOR STANDARD 128 PIXEL TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (LARGE_TUBE_SIZE/NUM_PIXELS_PER_TUBE))
    det.addComment("PIXEL FOR SMALL TOP 128 PIXEL TUBE")
    det.addCylinderPixel("pixel-top", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (SMALL_TOP_TUBE_SIZE/NUM_PIXELS_PER_TUBE))
    det.addComment("PIXEL FOR SMALL BOTTOM 128 PIXEL TUBE")
    det.addCylinderPixel("pixel-bottom", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (SMALL_BOTTOM_TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("DETECTOR IDs")
    # FIXME: Set to zero when A and E rows are filled
    offset = 37888
    for i in range(len(row_id_list)):
        row_id_str = row_id_list[i] + " row"
        det_names = [x for x in detinfo["Location"] if x.startswith(row_id_list[i])]
        id_list = []
        for j in range(len(det_names)):
            id_list.append(j * PIXELS_PER_BANK + offset)
            id_list.append((j+1) * PIXELS_PER_BANK - 1 + offset)
            id_list.append(None)

        offset += (PIXELS_PER_BANK * (j + 1))

        det.addDetectorIds(row_id_str, id_list)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1", "-2"])

    det.addComment("DETECTOR PARAMETERS")
    for row_id in row_id_list:
        row_id_str = row_id + " row"
        det.addDetectorParameters(row_id_str, TUBE_PRESSURE, TUBE_THICKNESS,
                                  TUBE_TEMPERATURE)

    #det.showGeom()
    det.writeGeom(xml_outfile)
