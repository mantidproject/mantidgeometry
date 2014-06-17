#!/usr/bin/python

INST_NAME = "ARCS"
NUM_PIXELS_PER_TUBE = 128
NUM_TUBES_PER_BANK = 8
SMALL_TOP_TUBE_SIZE = 0.2885 #meter
SMALL_BOTTOM_TUBE_SIZE = 0.3925 #meter
LARGE_TUBE_SIZE = 1.00608 #meter
TUBE_WIDTH = 0.0254 #meter
AIR_GAP_WIDTH = 0.002032 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1000.0 #x,y,z in millimeters
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 10.0, "atm")
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
        geom_input_file = "SNS/ARCS/ARCS_geom_20121011-.txt"

    # Set header information
    comment = "Created by Michael Reuter"
    # Time needs to be in UTC?
    valid_from = "2012-10-11 12:54:01"

    # Get geometry information file
    detinfo = readFile(geom_input_file)
    num_dets = len(detinfo.values()[0])
    xml_outfile = INST_NAME+"_Definition.xml"
    
    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(default_view="cylindrical_y")
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addModerator(-13.60)
    det.addSamplePosition()
    det.addComment("CHOPPERS")
    det.addChopper("t0-chopper",-4.83)
    det.addVerticalAxisT0Chopper("t0-chopper")
    det.addChopper("fermi-chopper",-1.99)
    det.addFermiChopper("fermi-chopper")
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1", "monitor2"],
                    distance=["-1.769", "4.9"])

    row_id = ""
    row_id_list = []
    doc_handle = None
    for i in range(num_dets):
        location = detinfo["Location"][i]
    
        if row_id != location[0]:
            row_id = location[0]
            row_id_list.append(row_id)
            row_id_str = row_id + " row"
            det.addComponent(row_id_str, row_id_str)
            doc_handle = det.makeTypeElement(row_id_str)

        det.addComponent(location, root=doc_handle)
        
        xpos = convert(detinfo["Xsci"][i])
        ypos = convert(detinfo["Ysci"][i])
        zpos = convert(detinfo["Zsci"][i])
        det_type = "eightpack"
        
        if location.startswith("M"):
            if location.endswith("A"):
                det_type = "eightpack-top"
            elif location.endswith("B"):
                det_type = "eightpack-bottom"

        det.addDetector(xpos, ypos, zpos, 
                        detinfo["Xrot_sci"][i], detinfo["Yrot_sci"][i], detinfo["Zrot_sci"][i],
                        location, det_type)

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
    offset = 0
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
