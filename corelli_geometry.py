#!/usr/bin/python

INST_NAME = "CORELLI"
NUM_PIXELS_PER_TUBE = 256
NUM_TUBES_PER_BANK = 16
TUBE_SIZE = 0.9107 #meter (34.7 in)
TUBE_WIDTH = 0.0127 #meter
AIR_GAP_WIDTH = 0.00127 #meter
PIXELS_PER_BANK = NUM_TUBES_PER_BANK * NUM_PIXELS_PER_TUBE
CONVERT_TO_METERS = 1000.0 #x,y,z in millimeters
# Detector Parameters
TUBE_PRESSURE = ("tube_pressure", 15.0, "atm")
TUBE_THICKNESS = ("tube_thickness", 0.0005, "metre")
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
        geom_input_file = "SNS/CORELLI/CORELLI_geom.txt"

    # Set header information
    comment = "Created by Ross Whitfield"
    # Time needs to be in UTC?
    valid_from = "2014-02-25 00:00:00"

    # Get geometry information file
    detinfo = readFile(geom_input_file)
    num_dets = len(detinfo.values()[0])
    xml_outfile = INST_NAME+"_Definition.xml"
    
    det = MantidGeom(INST_NAME, comment=comment, valid_from=valid_from)
    det.addSnsDefaults(default_view="cylindrical_y")
    det.addComment("SOURCE AND SAMPLE POSITION")
    det.addCuboidModerator(-20.00)
    det.addSamplePosition()
    det.addComment("MONITORS")
    det.addMonitors(names=["monitor1", "monitor2", "monitor3"],
                    distance=["-2.046", "-1.948", "4.554"])

    det.addChopper("single-disk-chopper",-7.669527)
    det.addSingleDiskChopper("single-disk-chopper")

    det.addChopper("double-disk-chopper",-11.79995,["Speed (Hz)","BL9:Chop:Skf2:MotorSpeed"],["Bandwidth (A)","BL9:Chop:Skf23:Bandwidth"],["Center (A)","BL9:Chop:Skf23:CenterWavelength"])
    det.addDoubleDiskChopper("double-disk-chopper")

    choppersequence="4.185 2.823 4.267 4.248 2.816 2.809 1.388 7.113 1.406 1.41 2.816 4.251 1.403 4.244 5.646 1.43 1.353 1.424 1.429 1.419 1.401 2.803 1.425 2.821 4.262 1.386 7.098 1.403 4.221 4.242 1.332 2.856 4.23 1.437 4.214 7.054 1.423 2.822 2.841 1.38 1.45 2.783 1.446 7.036 1.429 1.384 1.451 1.389 2.847 5.611 1.45 1.379 1.418 1.414 2.866 1.354 1.437 4.225 5.643 2.803 1.444 1.411 2.803 8.488 1.38 5.678 2.838 1.393 2.838 1.411 2.823 4.238 1.379 2.833 2.821 1.402 1.423 1.4 1.421 1.412 8.471 1.415 2.865 1.394 2.805 2.83 4.208 2.851 1.383 2.854 1.299 1.557 4.136 5.692 4.213 1.437 1.345 2.867 2.831 1.426 9.876 4.296 1.388 1.392 1.438 1.376 2.833 1.415 1.42 1.411 1.444 2.789 2.86 5.592 7.069 2.876 9.821 1.417 1.449 1.404 1.41 1.431 1.406 5.642 1.411 2.818 1.405 2.85"
    det.addChopper("correlation-chopper",-2.000653,["Speed (Hz)","BL9:Chop:Skf4:MotorSpeed"])
    det.addCorrelationChopper("correlation-chopper",sequence=choppersequence)
    det.addDetectorStringParameters("correlation-chopper",("sequence",choppersequence))

    row_id = ""
    row_id_list = []
    doc_handle = None
    for i in range(num_dets):
        location = detinfo["Location"][i]

        if location[0] == "#":
            continue

        if row_id != location[0]:
            row_id = location[0]
            row_id_list.append(row_id)
            row_id_str = row_id + " row"
            det.addComponent(row_id_str, row_id_str)
            doc_handle = det.makeTypeElement(row_id_str)

        det.addComponent("bank"+str(i+1), root=doc_handle)
        
        xpos = convert(detinfo["Xsci"][i])
        ypos = convert(detinfo["Ysci"][i])
        zpos = convert(detinfo["Zsci"][i])
        det_type = "sixteenpack"
        
        det.addDetector(xpos, ypos, zpos, 
                        detinfo["Xrot_sci"][i], detinfo["Yrot_sci"][i], detinfo["Zrot_sci"][i],
                        "bank"+str(i+1), det_type)

    det.addComment("16-PACK")
    det.addNPack("sixteenpack", NUM_TUBES_PER_BANK, TUBE_WIDTH, AIR_GAP_WIDTH)

    det.addComment("STANDARD 256 PIXEL TUBE")
    det.addPixelatedTube("tube", NUM_PIXELS_PER_TUBE, TUBE_SIZE)

    det.addComment("PIXEL FOR STANDARD 256 PIXEL TUBE")
    det.addCylinderPixel("pixel", (0.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                         (TUBE_WIDTH/2.0),
                         (TUBE_SIZE/NUM_PIXELS_PER_TUBE))

    det.addComment("MONITOR SHAPE")
    det.addComment("FIXME: Do something real here.")
    det.addDummyMonitor(0.01, 0.03)

    det.addComment("DETECTOR IDs")
    offset = 0
    for i in range(len(row_id_list)):
        row_id_str = row_id_list[i] + " row"
        det_names = [x for x in detinfo["Location"] if x.startswith(row_id_list[i]) or x.startswith("#"+row_id_list[i])]
        id_list = []
        for j in range(len(det_names)):
            if det_names[j][0] == "#":
                continue
            id_list.append(j * PIXELS_PER_BANK + offset)
            id_list.append((j+1) * PIXELS_PER_BANK - 1 + offset)
            id_list.append(None)

        offset += (PIXELS_PER_BANK * (j + 1))

        det.addDetectorIds(row_id_str, id_list)

    det.addComment("MONITOR IDs")
    det.addMonitorIds(["-1", "-2", "-3"])

    det.addComment("DETECTOR PARAMETERS")
    for row_id in row_id_list:
        row_id_str = row_id + " row"
        det.addDetectorParameters(row_id_str, TUBE_PRESSURE, TUBE_THICKNESS,
                                  TUBE_TEMPERATURE)

    #det.showGeom()
    det.writeGeom(xml_outfile)
